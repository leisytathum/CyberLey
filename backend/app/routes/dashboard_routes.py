from fastapi import APIRouter, Depends

from app.controllers.dashboard_controller import summary
from app.middlewares.roles import require_admin


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def dashboard_summary(user: dict = Depends(require_admin)):
    return summary(user)
