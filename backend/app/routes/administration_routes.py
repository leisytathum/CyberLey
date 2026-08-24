from fastapi import APIRouter, Depends

from app.controllers.administration_controller import get_profiles, update_role
from app.middlewares.roles import require_admin


router = APIRouter(prefix="/administracion", tags=["Administración"])


@router.get("/perfiles")
def profiles(user: dict = Depends(require_admin)):
    return get_profiles(user)


@router.patch("/perfiles/{target_id}/rol")
def role(target_id: str, role: str, user: dict = Depends(require_admin)):
    return update_role(target_id, role, user)
