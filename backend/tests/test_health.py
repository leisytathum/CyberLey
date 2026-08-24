from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_protected_endpoint_requires_session():
    response = client.get("/api/v1/participantes")
    assert response.status_code == 401
