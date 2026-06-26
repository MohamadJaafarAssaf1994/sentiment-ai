from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Gauge, Histogram
from src.schemas import PredictionRequest, PredictionResponse
from src.model import SentimentModel
import time

app = FastAPI(title="SentimentAI", version="0.1.0")
model = SentimentModel()

predictions_total = Counter(
    "sentiment_predictions_total",
    "Nombre total de predictions",
    ["label", "status"]
)

confidence_gauge = Gauge(
    "sentiment_confidence_score",
    "Score de confiance de la derniere prediction",
    ["label"]
)

prediction_duration = Histogram(
    "sentiment_prediction_duration_seconds",
    "Duree des predictions en secondes",
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5]
)

Instrumentator().instrument(app).expose(app)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    start = time.time()

    try:
        result = model.predict(request.text)
        duration = time.time() - start

        predictions_total.labels(
            label=result["label"],
            status="ok"
        ).inc()

        confidence_gauge.labels(
            label=result["label"]
        ).set(result["score"])

        prediction_duration.observe(duration)

        return result

    except Exception:
        predictions_total.labels(
            label="UNKNOWN",
            status="error"
        ).inc()
        raise
