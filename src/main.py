from fastapi import FastAPI

from src.schemas import PredictionRequest, PredictionResponse
from src.model import SentimentModel


app = FastAPI(title="SentimentAI", version="0.1.0")

model = SentimentModel()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    return model.predict(request.text)
