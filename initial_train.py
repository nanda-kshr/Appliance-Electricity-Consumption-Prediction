import kagglehub
import os
import pandas as pd
import xgboost as xgb
import joblib
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Download latest version
path = kagglehub.dataset_download("noohshaikh/ukdale-dataset-house-2-june-to-september-2013")

print("Path to dataset files:", path)

# 1. List the files in the downloaded directory to see what we have
files = os.listdir(path)
print("Files in directory:", files)

# 2. Filter for the CSV file (assuming there's one main CSV)
csv_files = [f for f in files if f.endswith('.csv')]

if csv_files:
    # Construct the full file path
    csv_path = os.path.join(path, csv_files[0])
    
    # 3. Load the dataframe
    df = pd.read_csv(csv_path)
    
    # Display the first few rows
    print(f"\nLoaded file: {csv_files[0]}")
    print(df.head())
else:
    print("No CSV file found in the directory.")
    exit()

# ==========================================
# 1. LOAD & PREPARE DATA (Run Weekly)
# ==========================================
# Load your dataset (from CSV or MongoDB)
# Note: df is already loaded above
df['time'] = pd.to_datetime(df['time'])
df = df.set_index('time').sort_index()

# CLEANING: Fill missing values with 0
df = df.fillna(0)

# TARGET SMOOTHING: Create a 'baseline' target
# We smooth the data so the model learns the "trend", not the noise.
window_size = 15 # 15-minute moving average
df['baseline'] = df['laptop'].rolling(window=window_size).mean()

# FEATURE ENGINEERING: Pure Time Features (No Lags!)
df['hour'] = df.index.hour
df['minute'] = df.index.minute
df['dayofweek'] = df.index.dayofweek
df['is_weekend'] = df['dayofweek'].apply(lambda x: 1 if x >= 5 else 0)

# Drop NaN rows created by rolling window
df = df.dropna()

# ==========================================
# 2. TRAIN THE BASELINE MODEL
# ==========================================
print("Training Baseline Model...")
X = df[['hour', 'minute', 'dayofweek', 'is_weekend']]
y = df['baseline']

model = xgb.XGBRegressor(n_estimators=100, max_depth=3, learning_rate=0.1)
model.fit(X, y)

# Save the model (optional, if you want to reuse it without retraining)
joblib.dump(model, 'baseline_model_laptop.joblib')
print("✅ Model Trained & Saved!")

# ==========================================
# 3. GENERATE "EXPECTED VALUES" (Run Hourly)
# ==========================================
# We want to predict the baseline for the NEXT 60 MINUTES
print("\nGenerating Forecast for the next hour...")

# Create a dataframe for the next 60 minutes
current_time = datetime.now().replace(second=0, microsecond=0)
future_dates = [current_time + timedelta(minutes=i) for i in range(60)]

future_df = pd.DataFrame({'time': future_dates})
future_df['hour'] = future_df['time'].dt.hour
future_df['minute'] = future_df['time'].dt.minute
future_df['dayofweek'] = future_df['time'].dt.dayofweek
future_df['is_weekend'] = future_df['dayofweek'].apply(lambda x: 1 if x >= 5 else 0)

# Predict the Expected Baseline
X_future = future_df[['hour', 'minute', 'dayofweek', 'is_weekend']]
future_df['expected_power'] = model.predict(X_future)

# DEFINE THRESHOLD: 
# "Spike" = Expected Power + Buffer (e.g., 20% or +50 Watts)
future_df['spike_threshold'] = future_df['expected_power'] * 1.5 

# ==========================================
# 4. EXPORT TO DATABASE (MongoDB/Redis)
# ==========================================
# This is what your API will read to detect anomalies
output = future_df[['time', 'expected_power', 'spike_threshold']]

# Example: Print the first 5 mins of the plan
print(output.head())

# In production:

import pymongo

# Connect to local MongoDB
client = pymongo.MongoClient(os.getenv("MONGO_URI"))
db = client["energy_db"]

# 1. Convert DataFrame to a list of dictionaries (JSON-like)
records = output.to_dict("records")

# 2. Clear old forecasts (optional: keeps the collection clean)
db.forecasts.delete_many({})

# 3. Insert the new 60-minute plan
db.forecasts.insert_many(records)

print(f"✅ Successfully uploaded {len(records)} forecast points to MongoDB.")

# output.to_dict('records') -> db.forecasts.insert_many(...)