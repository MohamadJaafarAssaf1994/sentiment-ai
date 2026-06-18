from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_predict_positive():
    r = client.post(
        "/predict",
        json={"text": "Ce produit est excellent !"}
    )

    assert r.status_code == 200

    data = r.json()

    assert data["label"] in ["POSITIVE", "NEGATIVE", "NEUTRAL"]
    assert 0 <= data["score"] <= 1
    assert data["text"] == "Ce produit est excellent !"


def test_predict_empty_fails():
    r = client.post("/predict", json={"text": ""})
    assert r.status_code == 422
