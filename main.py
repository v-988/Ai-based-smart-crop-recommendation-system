'''#IMP Part
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
from pydantic import BaseModel



app = FastAPI()

# ✅ enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ request model
class CropInput(BaseModel):
    N: float
    P: float
    K: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float

# load model
model = joblib.load("crop_model.pkl")


@app.get("/")
def home():
    return {"message": "API running"}


@app.post("/predict")
#IMP PART

#def predict(data: CropInput):

 #   df = pd.DataFrame([[ 
  #      data.N, data.P, data.K,
   #     data.temperature, data.humidity,
    #    data.ph, data.rainfall
    #]],
    #columns=["N","P","K","temperature","humidity","ph","rainfall"])

    #result = model.predict(df)

    #return {"recommended_crop": result[0]}
#IMP PART
def predict(data: CropInput):

    df = pd.DataFrame([[ 
        data.N, data.P, data.K,
        data.temperature, data.humidity,
        data.ph, data.rainfall
    ]],
    columns=["N","P","K","temperature","humidity","ph","rainfall"])

    # get probabilities
    probs = model.predict_proba(df)[0]

    # class labels
    crops = model.classes_

    # sort top 3
    top_idx = probs.argsort()[-3:][::-1]

    top_crops = [
        {"crop": crops[i], "confidence": float(probs[i])}
        for i in top_idx
    ]

    return {
      "recommended_crop": top_crops[0]["crop"],
       "alternatives": top_crops
    }
#IMP PART

''OLD CODE
class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(req: ChatRequest):
    answer = ask_rag(req.message)
    return {"reply": answer}

from rag_chat import ask_rag

@app.post("/chat")
def chat(q: str):
    return {"reply": ask_rag(q)}



class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(req: ChatRequest):
    return {"reply": ask_rag(req.message)}


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd

# ✅ ADD — import chatbot function
from rag_chat import ask_bot

app = FastAPI()

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Crop Prediction Model
# =========================

class CropInput(BaseModel):
    N: float
    P: float
    K: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float

model = joblib.load("crop_model.pkl")


@app.get("/")
def home():
    return {"message": "API running"}


@app.post("/predict")
def predict(data: CropInput):

    df = pd.DataFrame([[ 
        data.N, data.P, data.K,
        data.temperature, data.humidity,
        data.ph, data.rainfall
    ]],
    columns=["N","P","K","temperature","humidity","ph","rainfall"])

    probs = model.predict_proba(df)[0]
    crops = model.classes_

    top_idx = probs.argsort()[-3:][::-1]

    top_crops = [
        {"crop": crops[i], "confidence": float(probs[i])}
        for i in top_idx
    ]

    return {
        "recommended_crop": top_crops[0]["crop"],
        "alternatives": top_crops
    }


# =========================
# ✅ RAG Chatbot Endpoint
# =========================

class ChatRequest(BaseModel):
    question: str


@app.post("/chat")
def chat(req: ChatRequest):
    answer = ask_bot(req.question)
    return {"answer": answer}'''''



from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
import joblib
import pandas as pd
import numpy as np
import logging
import time
from datetime import datetime

# ─── Logging setup ───────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ─── App ─────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AgroSense Crop Recommendation API",
    description="Predicts the best crop based on soil and climate parameters.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Valid ranges for each input (based on crop dataset distribution) ─────────
VALID_RANGES = {
    "N":           (0,   200),
    "P":           (5,   145),
    "K":           (5,   205),
    "temperature": (8.0,  44.0),
    "humidity":    (14.0, 100.0),
    "ph":          (3.5,  9.5),
    "rainfall":    (20.0, 3000.0),
}

# Crops that are physically unsuitable for extreme conditions.
# Used as a post-processing filter to remove noisy low-confidence picks.
CROP_CONSTRAINTS = {
    "rice":        {"temp_min": 20, "temp_max": 37, "ph_min": 5.0, "ph_max": 8.0},
    "maize":       {"temp_min": 18, "temp_max": 35, "ph_min": 5.5, "ph_max": 7.5},
    "chickpea":    {"temp_min": 15, "temp_max": 35, "ph_min": 5.5, "ph_max": 8.5},
    "kidneybeans": {"temp_min": 15, "temp_max": 30, "ph_min": 6.0, "ph_max": 7.5},
    "pigeonpeas":  {"temp_min": 18, "temp_max": 35, "ph_min": 5.0, "ph_max": 7.0},
    "mothbeans":   {"temp_min": 24, "temp_max": 42, "ph_min": 6.0, "ph_max": 8.0},
    "mungbean":    {"temp_min": 25, "temp_max": 40, "ph_min": 6.2, "ph_max": 7.2},
    "blackgram":   {"temp_min": 25, "temp_max": 40, "ph_min": 5.5, "ph_max": 7.0},
    "lentil":      {"temp_min": 15, "temp_max": 30, "ph_min": 5.8, "ph_max": 8.0},
    "pomegranate": {"temp_min": 25, "temp_max": 40, "ph_min": 5.5, "ph_max": 7.5},
    "banana":      {"temp_min": 20, "temp_max": 38, "ph_min": 5.5, "ph_max": 7.0},
    "mango":       {"temp_min": 22, "temp_max": 40, "ph_min": 5.5, "ph_max": 7.5},
    "grapes":      {"temp_min": 15, "temp_max": 35, "ph_min": 5.5, "ph_max": 6.5},
    "watermelon":  {"temp_min": 22, "temp_max": 38, "ph_min": 6.0, "ph_max": 7.0},
    "muskmelon":   {"temp_min": 22, "temp_max": 38, "ph_min": 6.0, "ph_max": 7.0},
    "apple":       {"temp_min": 10, "temp_max": 25, "ph_min": 5.5, "ph_max": 6.5},
    "orange":      {"temp_min": 15, "temp_max": 35, "ph_min": 5.5, "ph_max": 7.0},
    "papaya":      {"temp_min": 22, "temp_max": 38, "ph_min": 6.0, "ph_max": 7.0},
    "coconut":     {"temp_min": 20, "temp_max": 38, "ph_min": 5.0, "ph_max": 8.0},
    "cotton":      {"temp_min": 21, "temp_max": 37, "ph_min": 5.8, "ph_max": 8.0},
    "jute":        {"temp_min": 24, "temp_max": 38, "ph_min": 6.0, "ph_max": 7.5},
    "coffee":      {"temp_min": 15, "temp_max": 28, "ph_min": 5.0, "ph_max": 6.5},
}

# ─── Input Model ─────────────────────────────────────────────────────────────
class CropInput(BaseModel):
    N:           float = Field(..., ge=0,    le=200,  description="Nitrogen content (kg/ha)")
    P:           float = Field(..., ge=5,    le=145,  description="Phosphorus content (kg/ha)")
    K:           float = Field(..., ge=5,    le=205,  description="Potassium content (kg/ha)")
    temperature: float = Field(..., ge=8.0,  le=44.0, description="Temperature in °C")
    humidity:    float = Field(..., ge=14.0, le=100.0,description="Relative humidity %")
    ph:          float = Field(..., ge=3.5,  le=9.5,  description="Soil pH value")
    rainfall:    float = Field(..., ge=20.0, le=3000.0, description="Annual rainfall in mm")

    # Round to 2 decimal places on the way in
    @field_validator("N","P","K","temperature","humidity","ph","rainfall", mode="before")
    @classmethod
    def round_values(cls, v):
        return round(float(v), 2)


# ─── Load model ──────────────────────────────────────────────────────────────
try:
    model = joblib.load("crop_model_new.pkl")
    logger.info(f"Model loaded — classes: {list(model.classes_)}")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    model = None


# ─── Helper: check if a crop is physically feasible ──────────────────────────
def is_feasible(crop: str, temp: float, ph: float) -> bool:
    """Return False if the crop cannot grow at these temp/pH values."""
    c = CROP_CONSTRAINTS.get(crop.lower())
    if c is None:
        return True  # unknown crop — don't filter it
    if not (c["temp_min"] <= temp <= c["temp_max"]):
        return False
    if not (c["ph_min"]  <= ph  <= c["ph_max"]):
        return False
    return True


# ─── Helper: build confidence label ──────────────────────────────────────────
def confidence_label(score: float) -> str:
    if score >= 0.80: return "high"
    if score >= 0.55: return "moderate"
    if score >= 0.35: return "low"
    return "very_low"


# ─── Endpoints ───────────────────────────────────────────────────────────────
@app.get("/")
def home():
    return {
        "status": "running",
        "api": "AgroSense Crop Recommendation v2.0",
        "model_loaded": model is not None,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/crops")
def list_crops():
    """Return the list of crops the model can predict."""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"crops": sorted(list(model.classes_)), "count": len(model.classes_)}


@app.post("/predict")
def predict(data: CropInput):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Check server logs.")

    start = time.time()

    # ── Build feature dataframe ───────────────────────────────────────────────
    df = pd.DataFrame([[
        data.N, data.P, data.K,
        data.temperature, data.humidity,
        data.ph, data.rainfall
    ]], columns=["N", "P", "K", "temperature", "humidity", "ph", "rainfall"])

    # ── Predict ───────────────────────────────────────────────────────────────
    try:
        probs = model.predict_proba(df)[0]
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

    crops = model.classes_

    # ── Sort ALL crops by probability ─────────────────────────────────────────
    all_sorted = sorted(
        zip(crops, probs),
        key=lambda x: x[1],
        reverse=True
    )

    # ── Apply feasibility filter for alternatives only ────────────────────────
    # (keep top-1 always, even if borderline, so we always return something)
    top_crop_name, top_crop_prob = all_sorted[0]

    # Filter alternatives: must be feasible AND confidence >= 10%
    CONFIDENCE_THRESHOLD = 0.10
    alternatives = [
        {
            "crop":       name,
            "confidence": round(float(prob), 4),
            "confidence_label": confidence_label(float(prob)),
            "feasible":   is_feasible(name, data.temperature, data.ph),
        }
        for name, prob in all_sorted[1:]
        if float(prob) >= CONFIDENCE_THRESHOLD
           and is_feasible(name, data.temperature, data.ph)
    ][:4]  # max 4 alternatives

    # ── Warn if top crop itself has low confidence ────────────────────────────
    top_confidence = round(float(top_crop_prob), 4)
    warning = None
    if top_confidence < 0.40:
        warning = (
            "Low confidence prediction. Consider entering your "
            "actual soil test values (N, P, K, pH) for better accuracy."
        )
    elif not is_feasible(top_crop_name, data.temperature, data.ph):
        warning = (
            f"{top_crop_name.title()} may not be ideal for your temperature "
            f"({data.temperature}°C) or pH ({data.ph}). Review conditions."
        )

    elapsed = round((time.time() - start) * 1000, 1)

    logger.info(
        f"Prediction → {top_crop_name} ({top_confidence:.1%}) | "
        f"temp={data.temperature} ph={data.ph} rainfall={data.rainfall} | "
        f"{elapsed}ms"
    )

    return {
        "recommended_crop":       top_crop_name,
        "confidence":             top_confidence,
        "confidence_label":       confidence_label(top_confidence),
        "warning":                warning,
        "alternatives":           alternatives,
        "input_summary": {
            "temperature": data.temperature,
            "humidity":    data.humidity,
            "ph":          data.ph,
            "rainfall":    data.rainfall,
            "N":           data.N,
            "P":           data.P,
            "K":           data.K,
        },
        "prediction_time_ms": elapsed,
    }


@app.post("/validate")
def validate_inputs(data: CropInput):
    """
    Dry-run endpoint — validates inputs and returns range warnings
    without running the model. Useful for frontend live feedback.
    """
    warnings = []
    values = {
        "N": data.N, "P": data.P, "K": data.K,
        "temperature": data.temperature, "humidity": data.humidity,
        "ph": data.ph, "rainfall": data.rainfall,
    }
    for field, val in values.items():
        lo, hi = VALID_RANGES[field]
        if not (lo <= val <= hi):
            warnings.append(
                f"{field} value {val} is outside expected range ({lo}–{hi})"
            )

    # Extra agronomic checks
    if data.ph < 5.0:
        warnings.append("Very acidic soil (pH < 5.0) — suitable only for tea/blueberry type crops")
    if data.ph > 8.5:
        warnings.append("Very alkaline soil (pH > 8.5) — very few crops tolerate this")
    if data.temperature < 10:
        warnings.append("Temperature below 10°C — most tropical crops will fail")
    if data.rainfall < 300:
        warnings.append("Very low rainfall — consider drought-resistant crops only")
    if data.N > 150:
        warnings.append("Very high Nitrogen — risk of over-fertilisation")

    return {
        "valid":    len(warnings) == 0,
        "warnings": warnings,
        "values":   values,
    }