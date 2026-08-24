from fastapi import HTTPException

from app.schemas.report_schema import ReportRequest
from app.services.reports_service import generate_report, list_reports


def get_reports(user: dict) -> dict:
    try:
        items = list_reports(user["token"])
        return {"items": items, "total": len(items)}
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


def create_report(payload: ReportRequest, user: dict) -> dict:
    try:
        return generate_report(user["token"], user["id"], payload)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
