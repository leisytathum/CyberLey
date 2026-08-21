from fastapi import APIRouter, Depends

from app.controllers.surveys_controller import get_surveys
from app.middlewares.roles import require_admin


router = APIRouter(
    prefix="/encuestas",
    tags=["Encuestas"],
)


@router.get("")
def surveys(
    user: dict = Depends(require_admin),
):
    return get_surveys(user)