'''from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ChatInput(BaseModel):
    message: str


def detect_intent(msg):
    msg = msg.lower()

    if "crop" in msg:
        return "crop"
    elif "soil" in msg or "ph" in msg:
        return "soil"
    elif "weather" in msg:
        return "weather"
    elif "seed price" in msg:
        return "price"
    else:
        return "general"


knowledge_base = {
    "crop": "Enter soil nutrients and weather to get crop recommendation.",
    "soil": "Soil pH shows acidity level. Ideal range is 6–7.",
    "weather": "Weather data is auto-fetched using API.",
    "price": "Seed price is predicted using regression model.",
    "general": "I can help with crop, soil, weather and price queries."
}


@app.post("/chat")
def chat(input: ChatInput):
    intent = detect_intent(input.message)
    reply = knowledge_base[intent]
    return {"reply": reply}'''