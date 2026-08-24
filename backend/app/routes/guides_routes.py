from fastapi import APIRouter, Depends
from app.controllers.guides_controller import get_guides, mark_complete
from app.middlewares.auth import current_user

router = APIRouter(prefix="/guias", tags=["Guías"])

@router.get("")
def guides(user: dict = Depends(current_user)):
    return get_guides(user)

@router.post("/{guide_id}/completar")
def complete(guide_id: str, user: dict = Depends(current_user)):
    return mark_complete(guide_id, user)
