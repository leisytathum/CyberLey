from fastapi import APIRouter, Depends

from app.controllers.participants_controller import get_participants
from app.middlewares.roles import require_admin


router = APIRouter(prefix="/participantes", tags=["Participantes"])


@router.get("")
def participants(user: dict = Depends(require_admin)):
    return get_participants(user)
