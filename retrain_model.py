import pymongo
import pandas as pd
import xgboost as xgb
import joblib
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# CONFIGURATION
# ----------------
DB_URI = os.getenv("MONGO_URI")
DB_NAME = "energy_db"
COLLECTION_NAME = "readings"
MODEL_FILENAME = "baseline_model_laptop.joblib"
TARGET_APPLIANCE = "laptop"  # Ensure this matches what you send in API

def get_data_from_mongo():
    """Fetches the last 30 days of data from MongoDB."""
    client = pymongo.MongoClient(DB_URI)
    db = client[DB_NAME]
    
    # Filter: Get data from the last 30 days only (Moving window training)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    query = {
        "timestamp": {"$gte": thirty_days_ago},
        "appliance_id": TARGET_APPLIANCE
    }
    
    # Fetch data
    cursor = db[COLLECTION_NAME].find(query)
    data = list(cursor)
    
    if not data:
        print("❌ No data found in MongoDB for the last 30 days.")
        return None

    print(f"✅ Fetched {len(data)} records from MongoDB.")
    return pd.DataFrame(data)

def train_and_save():
    # 1. LOAD DATA
    df = get_data_from_mongo()
    if df is None or len(df) < 100: # Safety check: Need enough data to train
        print("Not enough data to retrain. Skipping.")
        return

    # 2. PREPROCESSING (Must match your Forecaster logic exactly!)
    # -----------------------------------------------------------
    # Convert timestamp to datetime and sort
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp').sort_index()
    
    # Resample from 10s (Raw) to 1min (Model Standard)
    # We take the mean power for that minute
    df_resampled = df[['power']].resample('1min').mean()
    
    # Fill gaps (e.g., if system was off) with 0
    df_resampled = df_resampled.fillna(0)

    # 3. FEATURE ENGINEERING
    # ----------------------
    # Create the 'Baseline' Target (Trend)
    window_size = 15
    df_resampled['baseline'] = df_resampled['power'].rolling(window=window_size).mean()
    
    # Create Time Features
    df_resampled['hour'] = df_resampled.index.hour
    df_resampled['minute'] = df_resampled.index.minute
    df_resampled['dayofweek'] = df_resampled.index.dayofweek
    df_resampled['is_weekend'] = df_resampled['dayofweek'].apply(lambda x: 1 if x >= 5 else 0)

    # Drop NaNs created by rolling window
    df_resampled = df_resampled.dropna()

    # 4. TRAIN MODEL
    # --------------
    print(f"Training on {len(df_resampled)} minutes of data...")
    
    X = df_resampled[['hour', 'minute', 'dayofweek', 'is_weekend']]
    y = df_resampled['baseline']
    
    model = xgb.XGBRegressor(n_estimators=100, max_depth=3, learning_rate=0.1)
    model.fit(X, y)

    # 5. SAVE MODEL
    # -------------
    joblib.dump(model, MODEL_FILENAME)
    print(f"✅ Model successfully retrained and saved to '{MODEL_FILENAME}'")

    # 6. GENERATE FORECAST FOR NEXT HOUR
    # ----------------------------------
    print("\nGenerating Forecast for the next hour...")
    
    current_time = datetime.now().replace(second=0, microsecond=0)
    future_dates = [current_time + timedelta(minutes=i) for i in range(60)]
    
    future_df = pd.DataFrame({'time': future_dates})
    future_df['hour'] = future_df['time'].dt.hour
    future_df['minute'] = future_df['time'].dt.minute
    future_df['dayofweek'] = future_df['time'].dt.dayofweek
    future_df['is_weekend'] = future_df['dayofweek'].apply(lambda x: 1 if x >= 5 else 0)
    
    X_future = future_df[['hour', 'minute', 'dayofweek', 'is_weekend']]
    future_df['expected_power'] = model.predict(X_future)
    
    # SPIKE THRESHOLD: 50% above expected
    future_df['spike_threshold'] = future_df['expected_power'] * 1.5
    
    # Upload to MongoDB
    client = pymongo.MongoClient(DB_URI)
    db = client[DB_NAME]
    
    records = future_df[['time', 'expected_power', 'spike_threshold']].to_dict("records")
    
    # Clear old forecasts and insert new ones
    db.forecasts.delete_many({})
    db.forecasts.insert_many(records)
    print(f"✅ Successfully uploaded {len(records)} forecast points to MongoDB.")

if __name__ == "__main__":
    train_and_save()