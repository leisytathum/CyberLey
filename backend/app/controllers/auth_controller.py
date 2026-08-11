from fastapi import HTTPException

from app.services.auth_service import get_profile


def me(user: dict) -> dict:
    try:
        profile = get_profile(user)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return {
        "user": {
            "id": user.get("id"),
            "email": user.get("email"),
        },
        "profile": profile,
    }
