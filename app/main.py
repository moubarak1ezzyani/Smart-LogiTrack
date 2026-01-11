import os
import joblib
import pandas as pd
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from fastapi.security import OAuth2PasswordRequestForm
from app.auth import create_access_token, verify_token

# app : fastapi 
app = FastAPI(title="Smart LogiTrack API")

# --- db setup 
db_url = os.getenv("db_url_env")
engine = create_engine(db_url)
model = None

# --- Startup Event ---
# ML --> memory : server is ON 
@app.on_event("startup")
def load_model():
    global model
    try:
        # Load the pre-trained model from the specific Docker/Server path
        model = joblib.load('/opt/project/models/model.pkl')
    except:
        print("Model not found")

# --- Data Validation Schemas ---
# Defines the expected data structure for the prediction payload using Pydantic.
class TripFeatures(BaseModel):
    trip_distance: float
    passenger_count: int
    pickup_hour: int
    day_of_week: int

# --- Authentication Endpoint ---
# Handles user login and generates a JWT (JSON Web Token).
# Currently uses hardcoded credentials (admin/admin) for demonstration.
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username == "admin" and form_data.password == "admin":
        return {"access_token": create_access_token({"sub": "admin"}), "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Incorrect credentials")

# --- Prediction Endpoint ---
# Protected route: Requires a valid JWT token.
# 1. Accepts trip features.
# 2. Predicts the ETA using the loaded model.
# 3. LOGS the prediction to the database (Monitoring/Observability).
@app.post("/predict", dependencies=[Depends(verify_token)])
def predict_eta(trip: TripFeatures):
    # Ensure the model is loaded before attempting prediction
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Convert Pydantic model to Pandas DataFrame for the ML model
    data = pd.DataFrame([trip.dict()])
    prediction = model.predict(data)[0]
    
    # Log the input and the result into PostgreSQL for auditing and drift detection
    with engine.connect() as conn:
        # Create table if it doesn't exist (Idempotency)
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS eta_predictions 
            (timestamp TIMESTAMP DEFAULT NOW(), input TEXT, prediction FLOAT)
        """))
        # Insert the log entry
        conn.execute(text("INSERT INTO eta_predictions (input, prediction) VALUES (:inp, :pred)"), 
                     {"inp": str(trip.dict()), "pred": prediction})
    
    return {"estimated_duration_minutes": round(prediction, 2)}

# --- Analytics Endpoints (SQLAlchemy Raw SQL) ---

# Endpoint 1: Aggregation using a CTE (Common Table Expression).
# Calculates the average trip duration per hour of the day from the 'silver' layer.
@app.get("/analytics/avg-duration-by-hour")
def avg_duration_by_hour():
    sql = """
    WITH HourlyStats AS (
        SELECT pickup_hour, AVG(duration_minutes) as avg_dur
        FROM silver_taxi_trips
        GROUP BY pickup_hour
    )
    SELECT pickup_hour, avg_dur FROM HourlyStats ORDER BY pickup_hour;
    """
    with engine.connect() as conn:
        result = conn.execute(text(sql)).fetchall()
    return [{"pickuphour": row[0], "avgduration": round(row[1], 2)} for row in result]

# Endpoint 2: Grouping analysis.
# Analyzes trip volume and duration based on the payment method.
@app.get("/analytics/payment-analysis")
def payment_analysis():
    sql = """
    SELECT payment_type, COUNT(*) as total, AVG(duration_minutes) as avg_dur
    FROM silver_taxi_trips
    GROUP BY payment_type
    """
    with engine.connect() as conn:
        result = conn.execute(text(sql)).fetchall()
    return [{"payment_type": row[0], "total_trips": row[1], "avg_duration": round(row[2], 2)} for row in result]