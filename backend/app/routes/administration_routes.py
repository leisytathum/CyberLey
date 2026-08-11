from fastapi import APIRouter, Depends

from app.controllers.administration_controller import get_profiles
from app.middlewares.roles import require_admin


router = APIRouter(prefix="/administracion", tags=["Administración"])


@router.get("/perfiles")
def profiles(user: dict = Depends(require_admin)):
    return get_profiles(user)
