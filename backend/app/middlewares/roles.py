from fastapi import Depends, HTTPException, status
from time import monotonic

from app.database.supabase_client import SupabaseRESTClient
from app.middlewares.auth import current_user


_ROLE_CACHE_TTL = 15
_role_cache: dict[str, tuple[float, str]] = {}


def invalidate_role_cache(user_id: str) -> None:
    _role_cache.pop(user_id, None)


async def require_admin(user: dict = Depends(current_user)) -> dict:
    cached = _role_cache.get(user["id"])
    if cached and cached[0] > monotonic():
        if cached[1] == "admin":
            return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol administrador.",
        )

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

    role = profiles[0].get("rol") if profiles else ""
    _role_cache[user["id"]] = (monotonic() + _ROLE_CACHE_TTL, role)
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol administrador.",
        )

    return user
