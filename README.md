# Appliance Electricity Consumption Prediction

This project monitors real-time electricity consumption of appliances (e.g., laptops) and  detects anomalies (spikes) using an XGBoost model trained on historical data.

## Features

- **Real-time Ingestion**: API to receive power readings from IoT devices (ESP8266).
- **Anomaly Detection**: Compares real-time readings against a forecasted baseline.
- **Alerting**: Logs spikes to MongoDB and provides an API to retrieve recent alerts.
- **Forecasting**: Uses XGBoost to predict expected power consumption.

## Setup

1.  **Clone the repository**:
    ```bash
    git clone <repo-url>
    cd <repo-name>
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Variables**:
    Create a `.env` file in the root directory:
    ```env
    MONGO_URI=mongodb+srv://<username>:<password>@<cluster-url>/?retryWrites=true&w=majority
    ```

## Usage

### 1. Train the Model
Before running the API, you need to generate the initial forecast.

```bash
python initial_train.py
```
This script downloads the dataset (UK-DALE), trains the XGBoost model, and pushes the forecast for the next hour to MongoDB.

### 2. Run the API
Start the FastAPI server:

```bash
uvicorn main:app --reload
```
The server will start at `http://127.0.0.1:8000`.

### 3. API Endpoints

#### Ingest Data (`POST /ingest`)
Send power readings from your device.

**Payload:**
```json
{
  "appliance_id": "laptop",
  "power": 45.5
}
```

**Response:**
```json
{
  "status": "success",
  "spike_detected": false,
  "message": "Normal"
}
```

#### Get Recent Alerts (`GET /alerts/recent`)
Retrieve alerts triggered in the last hour.

**Response:**
```json
{
  "count": 1,
  "alerts": [
    {
      "_id": "...",
      "timestamp": "2026-01-27T10:52:00",
      "appliance_id": "laptop",
      "power": 120.5,
      "threshold": 80.0,
      "message": "SPIKE DETECTED! 120.5W > 80.00W"
    }
  ]
}
```

## Model Retraining
To update the model with new data collected in MongoDB:

```bash
python retrain_model.py
```
