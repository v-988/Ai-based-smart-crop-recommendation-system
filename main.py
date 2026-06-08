from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import sys
import importlib.util
from dotenv import load_dotenv
import requests
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from datetime import datetime
import rasterio
from fastapi import UploadFile, File, HTTPException, status
from loguru import logger
import httpx
from typing import Tuple, List
from fastapi import APIRouter, Request, Body, HTTPException
from pydantic import BaseModel
import io
import tempfile
import uuid

# Latest sensor readings from ESP32 (updated by /save-sensor-data)
latest_temperature = None
latest_humidity = None
latest_moisture = None

load_dotenv()

# Integrate disease detection and chatbot services from diseasedetection&chatbot backend
integration_backend_path = os.path.join(
    os.path.dirname(__file__),
    "diseasedetection&chatbot",
    "backend"
)
if integration_backend_path not in sys.path:
    sys.path.append(integration_backend_path)

integrated_disease_service = None
integrated_llm_service = None
integrated_speech_service = None
IntegratedLanguageEnum = None
integration_error_msg = "No error"
try:
    from services.disease_service import disease_service as integrated_disease_service
    from services.llm_service import llm_service as integrated_llm_service
    from services.speech_service import speech_service as integrated_speech_service
    from models.schemas import LanguageEnum as IntegratedLanguageEnum
except Exception as integration_error:
    integration_error_msg = str(integration_error)
    print(f"Integration load warning: {integration_error}")

app = FastAPI()

# Load soil dataset
try:
    soil_df = pd.read_csv("datasets/Soil data.csv")
    print("Soil dataset loaded successfully! Rows:", len(soil_df))
    print("Columns in dataset:", soil_df.columns.tolist())
except Exception as e:
    print("Error loading soil dataset:", str(e))
    soil_df = None

# Calculate district averages
soil_avg_df = None
if soil_df is not None:
    soil_avg_df = soil_df.groupby('District').agg({
        'Nitrogen Value': 'mean',
        'Phosphorous value': 'mean',
        'Potassium value': 'mean',
        'pH': 'mean'
    }).reset_index()
    soil_avg_df.columns = ['District', 'avg_n', 'avg_p', 'avg_k', 'avg_ph']
    print("District soil averages calculated! Number of districts:", len(soil_avg_df))

# Load all new uploaded datasets
tn_crop_prod_df = None
rice_prod_df = None
crop_history_df = None
rainfall_df = None
land_use_df = None
agri_yield_df = None

try:
    tn_crop_prod_df = pd.read_csv("datasets/Tamilnadu Crop-Production.csv")
    print("Tamilnadu Crop-Production loaded! Rows:", len(tn_crop_prod_df))
except Exception as e:
    print("Error loading Tamilnadu Crop-Production:", str(e))

try:
    rice_prod_df = pd.read_csv("datasets/rice_production.csv")
    print("rice_production loaded! Rows:", len(rice_prod_df))
except Exception as e:
    print("Error loading rice_production:", str(e))

try:
    crop_history_df = pd.read_csv("datasets/crop_production_history.csv")
    print("crop_production_history loaded! Rows:", len(crop_history_df))
    print("Crop history columns:", crop_history_df.columns.tolist())
except Exception as e:
    print("Error loading crop_production_history:", str(e))

try:
    rainfall_df = pd.read_csv("datasets/rainfall_data.csv")
    print("rainfall_data loaded! Rows:", len(rainfall_df))
except Exception as e:
    print("Error loading rainfall_data:", str(e))

try:
    land_use_df = pd.read_csv("datasets/land_use.csv")
    print("land_use loaded! Rows:", len(land_use_df))
    print("Land use columns:", land_use_df.columns.tolist())
except Exception as e:
    print("Error loading land_use:", str(e))

try:
    agri_yield_df = pd.read_csv("datasets/Tamilnadu agriculture yield data.csv")
    print("Tamilnadu agriculture yield data loaded! Rows:", len(agri_yield_df))
except Exception as e:
    print("Error loading Tamilnadu agriculture yield data:", str(e))

# District lat/long dictionary (exact names from your CSV)
district_latlon = {
    "Ariyalur": (11.1385, 79.0779),
    "Chengalpattu": (12.6833, 79.9833),
    "Coimbatore": (11.0168, 76.9558),
    "Dindigul": (10.3687, 77.9803),
    "Erode": (11.3410, 77.7172),
    "Kanchipuram": (12.8352, 79.6993),
    "Kanniyakumari": (8.0883, 77.5385),
    "Karur": (10.9596, 78.0766),
    "Madurai": (9.9252, 78.1198),
    "Nagapattinam": (10.7662, 79.8449),
    "Namakkal": (11.2195, 78.1676),
    "Perambalur": (11.2333, 78.8667),
    "Pudukkottai": (10.4500, 78.8167),
    "Ramanathapuram": (9.3713, 78.8314),
    "Salem": (11.6643, 78.1460),
    "Sivaganga": (9.8433, 78.4803),
    "Thanjavur": (10.786999, 79.137827),
    "The Nilgiris": (11.4917, 76.7333),
    "Theni": (10.0104, 77.4770),
    "Thiruvallur": (13.1433, 79.9083),
    "Thiruvarur": (10.7672, 79.6350),
    "Tiruchippalli": (10.7905, 78.7047),
    "Tirunelveli": (8.7139, 77.7567),
    "Tirupathur": (12.4935, 78.2132),
    "Tiruppur": (11.1085, 77.3411),
    "Tiruvannamalai": (12.2250, 79.0747),
    "Tuticorn": (8.7642, 78.1348),
    "Vellore": (12.9165, 79.1325),
    "Villupuram": (11.9395, 79.4924),
    "Virudhunagar": (9.5790, 77.9584),
}

# Load crop recommendation dataset and train model
try:
    crop_df = pd.read_csv("datasets/Crop_recommendation.csv")
except Exception as e:
    print("Error loading Crop_recommendation:", str(e))
    crop_df = None

model = None
if crop_df is not None:
    features = crop_df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
    target = crop_df['label']
    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    print(f"Crop ML model trained! Accuracy: {accuracy_score(y_test, model.predict(X_test)):.2f}")

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
AGROMONITORING_APPID = os.getenv("AGROMONITORING_APPID")

# =========================
# FRONTEND PAGE ROUTES
# =========================

@app.get("/", response_class=HTMLResponse)
def signup_page(request: Request):
    return templates.TemplateResponse(request=request, name="signup.html")

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/disease", response_class=HTMLResponse)
def disease_page(request: Request):
    return templates.TemplateResponse(request=request, name="disease.html")

# ────────────────────────────────────────────────
# NEW FEATURE: Plant Disease Detection (from Plant-AI)
# Uses HuggingFace Inference API - no local model download needed
# ────────────────────────────────────────────────

@app.post("/api/detect-disease")
async def detect_disease(image: UploadFile = File(...)):
    try:
        contents = await image.read()

        if not contents:
            raise HTTPException(status_code=400, detail="Empty image")
        if integrated_disease_service is None:
            raise HTTPException(status_code=500, detail="Integrated disease service not loaded")

        disease, confidence, recommendations = await integrated_disease_service.detect_disease(contents)
        confidence_percent = confidence * 100 if confidence <= 1 else confidence

        return {
            "status": "success",
            "disease": disease,
            "confidence": f"{confidence_percent:.1f}%",
            "recommendations": recommendations or []
        }

    except Exception as e:
        logger.error(f"Disease API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ────────────────────────────────────────────────
# NEW ROUTE: Separate Disease Detection Page
# Uses diseasenew.html to avoid conflict with existing /disease
# ────────────────────────────────────────────────

@app.get("/diseasenew")
async def disease_new_page(request: Request):
    return templates.TemplateResponse(request=request, name="diseasenew.html")

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse(request=request, name="chat.html")
# ────────────────────────────────────────────────
# Chatbot Endpoint - Text-based farming advice
# ────────────────────────────────────────────────

@app.post("/api/transcribe")
async def transcribe_audio(audio: UploadFile = File(...), language: str = "English"):
    try:
        contents = await audio.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Empty audio file")
            
        if integrated_speech_service is None or IntegratedLanguageEnum is None:
            raise HTTPException(status_code=500, detail="Integrated speech service not loaded")
            
        lang_enum = IntegratedLanguageEnum.TAMIL if language.lower() == "tamil" else IntegratedLanguageEnum.ENGLISH
        
        text, detected_lang = await integrated_speech_service.speech_to_text(
            contents,
            lang_enum,
            filename=audio.filename
        )
        
        return {
            "status": "success",
            "text": text,
            "language": detected_lang.value
        }
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class ChatRequest(BaseModel):
    message: str
    language: str = "English"  # Optional: English or Tamil
    session_id: str

@app.post("/api/chat")
async def chat_with_farmer(request: ChatRequest):
    try:
        if integrated_llm_service is None or IntegratedLanguageEnum is None:
            raise HTTPException(status_code=500, detail="Integrated chatbot service not loaded")

        lang = request.language or "English"
        if lang.lower() == "tamil":
            selected_language = IntegratedLanguageEnum.TAMIL
        else:
            selected_language = IntegratedLanguageEnum.ENGLISH

        reply = await integrated_llm_service.chat(
            message=request.message,
            session_id=request.session_id,
            disease_context=None,
            language=selected_language,
        )

        return {
            "status": "success",
            "reply": reply,
            "language": lang
        }

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/debug")
def api_debug():
    return {
        "disease_service_loaded": integrated_disease_service is not None,
        "llm_service_loaded": integrated_llm_service is not None,
        "speech_service_loaded": integrated_speech_service is not None,
        "integration_error_msg": integration_error_msg,
        "OPENWEATHER_API_KEY_exists": bool(os.getenv("OPENWEATHER_API_KEY")),
        "AGROMONITORING_APPID_exists": bool(os.getenv("AGROMONITORING_APPID")),
        "sys_path": sys.path
    }
    
# Register root crop router without package-name conflicts
crop_router_file = os.path.join(os.path.dirname(__file__), "routers", "crop_router.py")
crop_router_spec = importlib.util.spec_from_file_location("root_crop_router", crop_router_file)
crop_router_module = importlib.util.module_from_spec(crop_router_spec)
crop_router_spec.loader.exec_module(crop_router_module)
app.include_router(crop_router_module.router)
