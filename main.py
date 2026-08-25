from fastapi import FastAPI, HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel

# 1. Define your secret API Key (Change this to a long random string!)
API_KEY = "my_super_secret_n8n_token_123"
API_KEY_NAME = "X-API-KEY"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

app = FastAPI()

class PatientData(BaseModel):
    age: int
    bmi: float
    high_blood_pressure: int
    glucose_level: int
    family_history: int

def verify_api_key(header_value: str = Security(api_key_header)):
    if header_value != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key"
        )
    return header_value

@app.post("/predict")
def predict_risk(data: PatientData, token: str = Security(verify_api_key)):
    # Math calculation logic
    score = 0.0
    if data.glucose_level > 125: score += 0.4
    elif data.glucose_level > 100: score += 0.2
    
    if data.bmi > 25: score += 0.3
    if data.age > 45: score += 0.2
    if data.family_history == 1: score += 0.1
    if data.high_blood_pressure == 1: score += 0.1
    
    score = min(score, 1.0)
    
    return {
        "risk_score": round(score, 2),
        "high_risk": score >= 0.5
    }
