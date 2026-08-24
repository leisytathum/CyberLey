import httpx
from time import monotonic
from fastapi import Header, HTTPException, status

from app.config.settings import settings


_AUTH_CACHE_TTL = 20
_auth_cache: dict[str, tuple[float, dict]] = {}


async def current_user(
    authorization: str | None = Header(default=None),
) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión requerida.",
        )

    if not settings.supabase_url or not settings.supabase_publishable_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase no está configurado en backend/.env.",
        )

    token = authorization.split(" ", 1)[1]

    cached = _auth_cache.get(token)
    if cached and cached[0] > monotonic():
        return {"token": token, **cached[1]}

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(
            f"{settings.supabase_url}/auth/v1/user",
            headers={
                "apikey": settings.supabase_publishable_key,
                "Authorization": f"Bearer {token}",
            },
        )

    if response.status_code != 200:
        _auth_cache.pop(token, None)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión inválida o expirada.",
        )

    user = response.json()
    if len(_auth_cache) > 100:
        now = monotonic()
        for cache_token, (expires, _) in list(_auth_cache.items()):
            if expires <= now:
                _auth_cache.pop(cache_token, None)
    _auth_cache[token] = (monotonic() + _AUTH_CACHE_TTL, user)
    return {"token": token, **user}
