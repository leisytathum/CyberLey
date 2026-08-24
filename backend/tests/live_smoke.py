"""Smoke test manual contra el proyecto Supabase configurado en backend/.env."""

import logging

import httpx
from fastapi.testclient import TestClient

from app.config.settings import settings
from app.main import app


def login(email: str, password: str) -> str:
    response = httpx.post(
        f"{settings.supabase_url}/auth/v1/token?grant_type=password",
        headers={"apikey": settings.supabase_publishable_key},
        json={"email": email, "password": password},
        timeout=20,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def main() -> None:
    logging.disable(logging.CRITICAL)
    admin_token = login("admin@cyberley.com", "Admin123*")
    user_token = login("usuario1@cyberley.com", "Usuario123*")
    client = TestClient(app)
    checks = [
        ("admin", admin_token, path)
        for path in (
            "/api/v1/dashboard/summary",
            "/api/v1/participantes",
            "/api/v1/encuestas",
            "/api/v1/riesgo",
            "/api/v1/guias",
            "/api/v1/reportes",
            "/api/v1/limpieza/diagnostico",
            "/api/v1/respaldos/exportar",
            "/api/v1/administracion/perfiles",
        )
    ] + [
        ("usuario", user_token, path)
        for path in (
            "/api/v1/riesgo/mis-resultados",
            "/api/v1/guias",
            "/api/v1/participantes",
        )
    ]

    unexpected = []
    for role, token, path in checks:
        response = client.get(
            path,
            headers={"Authorization": f"Bearer {token}"},
        )
        expected = 403 if role == "usuario" and path.endswith("participantes") else 200
        print(f"{role:7} {path:40} {response.status_code}")
        if response.status_code != expected:
            unexpected.append((path, response.status_code, response.text[:200]))

    if unexpected:
        raise SystemExit(f"Fallaron rutas: {unexpected}")


if __name__ == "__main__":
    main()
