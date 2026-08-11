from fastapi import HTTPException

from app.schemas.risk_schema import RiskInput
from app.services.risk_service import list_risk_responses, save_risk_response


def evaluate(payload: RiskInput, user: dict) -> dict:
    try:
        return save_risk_response(user["token"], user["id"], payload)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


def get_risk(user: dict) -> dict:
    try:
        items = list_risk_responses(user["token"])
        return {"items": items, "total": len(items)}
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
