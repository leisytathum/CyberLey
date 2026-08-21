from __future__ import annotations

import httpx

from app.config.settings import settings


TEST_USERS = [
    {
        "email": "admin@cyberley.com",
        "password": "Admin123*",
        "nombre_completo": "Administrador CyberLey",
        "rol": "admin",
    },
    {
        "email": "usuario1@cyberley.com",
        "password": "Usuario123*",
        "nombre_completo": "Ana Martínez",
        "rol": "usuario",
    },
    {
        "email": "usuario2@cyberley.com",
        "password": "Usuario123*",
        "nombre_completo": "Carlos López",
        "rol": "usuario",
    },
    {
        "email": "usuario3@cyberley.com",
        "password": "Usuario123*",
        "nombre_completo": "María Hernández",
        "rol": "usuario",
    },
]


def _validate_settings() -> None:
    if not settings.supabase_url:
        raise RuntimeError(
            "Falta SUPABASE_URL en backend/.env."
        )

    if not settings.supabase_service_role_key:
        raise RuntimeError(
            "Falta SUPABASE_SERVICE_ROLE_KEY en backend/.env. "
            "Los seeds necesitan la service role key."
        )


def _admin_headers() -> dict[str, str]:
    return {
        "apikey": settings.supabase_service_role_key,
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
        "Content-Type": "application/json",
    }


def _find_user_by_email(
    client: httpx.Client,
    email: str,
) -> dict | None:
    response = client.get(
        f"{settings.supabase_url}/auth/v1/admin/users",
        headers=_admin_headers(),
        params={
            "page": "1",
            "per_page": "1000",
        },
    )

    response.raise_for_status()

    body = response.json()

    users = body.get("users", body if isinstance(body, list) else [])

    for user in users:
        if user.get("email", "").lower() == email.lower():
            return user

    return None


def _create_auth_user(
    client: httpx.Client,
    user_data: dict,
) -> dict:
    existing_user = _find_user_by_email(
        client,
        user_data["email"],
    )

    if existing_user:
        print(
            f"  ↳ Auth existente: {user_data['email']}"
        )
        return existing_user

    response = client.post(
        f"{settings.supabase_url}/auth/v1/admin/users",
        headers=_admin_headers(),
        json={
            "email": user_data["email"],
            "password": user_data["password"],
            "email_confirm": True,
            "user_metadata": {
                "nombre_completo": user_data["nombre_completo"],
                "rol": user_data["rol"],
            },
        },
    )

    response.raise_for_status()

    auth_user = response.json()

    print(
        f"  ✓ Auth creado: {user_data['email']}"
    )

    return auth_user


def _upsert_profile(
    client: httpx.Client,
    auth_user: dict,
    user_data: dict,
) -> None:
    headers = {
        **_admin_headers(),
        "Prefer": "resolution=merge-duplicates,return=representation",
    }

    response = client.post(
        f"{settings.supabase_url}/rest/v1/perfiles",
        headers=headers,
        params={
            "on_conflict": "id",
        },
        json={
            "id": auth_user["id"],
            "nombre_completo": user_data["nombre_completo"],
            "rol": user_data["rol"],
        },
    )

    response.raise_for_status()

    print(
        f"  ✓ Perfil listo: "
        f"{user_data['nombre_completo']} "
        f"({user_data['rol']})"
    )


def seed_users() -> dict[str, str]:
    """
    Crea usuarios de prueba en Supabase Auth y sus perfiles.

    Retorna:
        {
            "admin@cyberley.com": "uuid...",
            ...
        }
    """

    _validate_settings()

    created_users: dict[str, str] = {}

    print("\n=== USUARIOS DE PRUEBA ===")

    with httpx.Client(timeout=30) as client:
        for user_data in TEST_USERS:
            auth_user = _create_auth_user(
                client,
                user_data,
            )

            _upsert_profile(
                client,
                auth_user,
                user_data,
            )

            created_users[user_data["email"]] = auth_user["id"]

    return created_users