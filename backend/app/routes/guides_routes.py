from uuid import UUID

from fastapi import APIRouter, Depends, status
from app.controllers.guides_controller import get_guides, mark_complete
from app.middlewares.auth import current_user

router = APIRouter(prefix="/guias", tags=["Guías"])

@router.get("", summary="Listar guías y progreso del usuario")
def guides(user: dict = Depends(current_user)):
    return get_guides(user)

@router.post("/{guide_id}/completar", status_code=status.HTTP_200_OK, summary="Marcar una guía como completada")
def complete(guide_id: UUID, user: dict = Depends(current_user)):
    return mark_complete(str(guide_id), user)
