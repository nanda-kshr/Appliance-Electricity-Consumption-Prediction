from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
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
            
            # Log Alert to DB
            alert_doc = {
                "timestamp": data.timestamp,
                "appliance_id": data.appliance_id,
                "power": data.power,
                "threshold": threshold,
                "message": message
            }
            db.alerts.insert_one(alert_doc)
            print(message)
    else:
        message = "No forecast found for this time (Cold Start)"

    return {
        "status": "success",
        "spike_detected": alert,
        "message": message
    }

@app.get("/alerts/recent")
async def get_recent_alerts():
    """Get all alerts from the last hour"""
    one_hour_ago = datetime.now() - timedelta(hours=1)
    
    # Query for alerts newer than 1 hour
    query = {"timestamp": {"$gte": one_hour_ago}}
    
    # Sort by newest first
    alerts = list(db.alerts.find(query).sort("timestamp", -1))
    
    # Convert ObjectIds to strings for JSON serialization
    for alert in alerts:
        alert["_id"] = str(alert["_id"])
    
    return {
        "count": len(alerts),
        "alerts": alerts
    }