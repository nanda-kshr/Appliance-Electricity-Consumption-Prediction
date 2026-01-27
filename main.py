from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import pymongo
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Connect to DB
client = pymongo.MongoClient(os.getenv("MONGO_URI"))
db = client["energy_db"]

# Data Model (What the ESP8266 sends)
class EnergyReading(BaseModel):
    appliance_id: str
    power: float
    timestamp: datetime = None  # Optional, defaults to now

@app.post("/ingest")
async def ingest_data(data: EnergyReading):
    # 1. Set timestamp if missing
    if not data.timestamp:
        data.timestamp = datetime.now()

    # 2. Store Raw Data (The "Hot" Path)
    db.readings.insert_one(data.dict())

    # 3. REAL-TIME SPIKE CHECK
    # ------------------------
    # Round time to the nearest minute to match your forecast keys
    lookup_time = data.timestamp.replace(second=0, microsecond=0)

    # Find the expected threshold for this specific minute
    plan = db.forecasts.find_one({"time": lookup_time})

    alert = False
    message = "Normal"

    if plan:
        threshold = plan['spike_threshold']
        
        # COMPARE: Actual vs Threshold
        if data.power > threshold:
            alert = True
            message = f"⚠️ SPIKE DETECTED! {data.power}W > {threshold:.2f}W"
            # TODO: Trigger email/SMS/Push Notification here
            print(message)
    else:
        message = "No forecast found for this time (Cold Start)"

    return {
        "status": "success",
        "spike_detected": alert,
        "message": message
    }