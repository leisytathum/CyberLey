from fastapi import APIRouter, Depends

from app.controllers.reports_controller import create_report, get_reports
from app.middlewares.roles import require_admin
from app.schemas.report_schema import ReportRequest


router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("")
def reports(user: dict = Depends(require_admin)):
    return get_reports(user)


@router.post("/generar")
def report_generate(payload: ReportRequest, user: dict = Depends(require_admin)):
    return create_report(payload, user)
