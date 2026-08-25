from fastapi import FastAPI, HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel

# 1. Define your secret API Key
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
    # 2. Risk Calculation Math Logic
    score = 0.0
    if data.glucose_level > 125: 
        score += 0.4
    elif data.glucose_level > 100: 
        score += 0.2
    
    if data.bmi > 25: 
        score += 0.3
    if data.age > 45: 
        score += 0.2
    if data.family_history == 1: 
        score += 0.1
    if data.high_blood_pressure == 1: 
        score += 0.1
    
    score = min(score, 1.0)
    
    # 3. Dynamic Mapping to match your n8n HTML template variables perfectly
    if score >= 0.7:
        risk_band_label = "High Risk"
        risk_signal = "🔴 High Priority Review Needed"
        action_plan = [
            "Flag file for urgent clinician manual intake review",
            "Order follow-up diagnostic HbA1c testing",
            "Provide immediate diabetic lifestyle management resources"
        ]
    elif score >= 0.4:
        risk_band_label = "Moderate Risk"
        risk_signal = "季 Moderate Monitoring"
        action_plan = [
            "Schedule standard clinical consultation follow-up",
            "Discuss preventative dietary changes"
        ]
    else:
        risk_band_label = "Low Risk"
        risk_signal = "🟢 Normal / Baseline"
        action_plan = [
            "Send standard wellness and diabetes prevention guide",
            "Rescreen routinely at next annual checkup"
        ]
        
    # 4. Return properties looking exactly like your layout expressions
    return {
        "diabetes_risk": round(score * 100, 1),  # Multiplied by 100 to feed into {{ ... }}% raw
        "risk_band_label": risk_band_label,
        "risk_signal": risk_signal,
        "action_plan": action_plan
    }
