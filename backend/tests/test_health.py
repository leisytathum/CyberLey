from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-request-id"]
    assert float(response.headers["x-process-time-ms"]) >= 0


def test_protected_endpoint_requires_session():
    response = client.get("/api/v1/participantes")
    assert response.status_code == 401


def test_development_cors_accepts_vite_fallback_port():
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:5174",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5174"
