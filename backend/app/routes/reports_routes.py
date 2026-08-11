from fastapi import APIRouter, Depends

from app.controllers.reports_controller import get_reports
from app.middlewares.roles import require_admin


router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("")
def reports(user: dict = Depends(require_admin)):
    return get_reports(user)
