import pymongo
import random
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
# Use the same URI as the app
DB_URI = os.getenv("MONGO_URI") 
DB_NAME = "energy_db"
COLLECTION_NAME = "readings"
TARGET_APPLIANCE = "laptop"

def generate_data():
    client = pymongo.MongoClient(DB_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    print("Generating synthetic data...")

    records = []
    # Generate data for the last 24 hours, one reading every minute
    # Total = 60 * 24 = 1440 records
    start_time = datetime.now() - timedelta(days=1)
    
    for i in range(1440):
        current_time = start_time + timedelta(minutes=i)
        
        # Simulate power readings
        # Base power ~50W, with random fluctuations
        # Occasional spikes up to 150W
        is_spike = random.random() < 0.05 # 5% chance of spike
        if is_spike:
             power = random.uniform(100, 160)
        else:
             power = random.uniform(30, 70)

        record = {
            "appliance_id": TARGET_APPLIANCE,
            "power": round(power, 2),
            "timestamp": current_time
        }
        records.append(record)

    # Insert into MongoDB
    if records:
        collection.insert_many(records)
        print(f"✅ Successfully inserted {len(records)} synthetic records into '{COLLECTION_NAME}'")
    else:
        print("No records generated.")

if __name__ == "__main__":
    generate_data()
