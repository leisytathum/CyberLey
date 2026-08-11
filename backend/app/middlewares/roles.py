from fastapi import Depends, HTTPException, status

from app.database.supabase_client import SupabaseRESTClient
from app.middlewares.auth import current_user


async def require_admin(user: dict = Depends(current_user)) -> dict:
    try:
        profiles = SupabaseRESTClient(user["token"]).get(
            "perfiles",
            select="rol",
            filters={"id": f"eq.{user['id']}"},
            limit=1,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    if not profiles or profiles[0].get("rol") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol administrador.",
        )

    return user
