import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="Diabetes Risk Assessment API",
    description="Microservice for evaluating patient diabetes risk factors.",
    version="1.0.0"
)

# Define the data structure expected from the n8n Webhook
class PatientData(BaseModel):
    age: int = Field(..., ge=0, le=120, description="Age of the patient in years")
    bmi: float = Field(..., ge=10.0, le=60.0, description="Body Mass Index")
    high_blood_pressure: int = Field(..., ge=0, le=1, description="1 if diagnosed, 0 if not")
    glucose_level: int = Field(..., ge=50, le=400, description="Fasting blood glucose level in mg/dL")
    family_history: int = Field(..., ge=0, le=1, description="1 if immediate family has diabetes, 0 if not")

@app.post("/v1/predict/diabetes", tags=["Prediction"])
async def predict_diabetes_risk(patient: PatientData):
    try:
        # Base scoring calculation based on statistical health risk weights
        score = 0.0
        
        # 1. Age Factor
        if patient.age >= 45:
            score += 0.25
        elif patient.age >= 35:
            score += 0.15
            
        # 2. BMI Factor (Overweight >= 25, Obese >= 30)
        if patient.bmi >= 30.0:
            score += 0.30
        elif patient.bmi >= 25.0:
            score += 0.15
            
        # 3. Fasting Glucose Factor
        if patient.glucose_level >= 126:  # Diabetic threshold
            score += 0.40
        elif patient.glucose_level >= 100:  # Prediabetic threshold
            score += 0.20
            
        # 4. Comorbidities & Heredity
        if patient.high_blood_pressure == 1:
            score += 0.15
        if patient.family_history == 1:
            score += 0.20
            
        # Normalize score to a maximum cap of 1.0 (100% risk representation)
        final_risk_score = min(round(score, 2), 1.0)
        
        # Determine classification category
        if final_risk_score >= 0.7:
            risk_level = "High"
        elif final_risk_score >= 0.4:
            risk_level = "Moderate"
        else:
            risk_level = "Low"
            
        return {
            "status": "success",
            "risk_score": final_risk_score,
            "risk_level": risk_level,
            "recommendation": "Refer to doctor for diagnostic testing" if risk_level == "High" else "Monitor health metrics"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk processing error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
