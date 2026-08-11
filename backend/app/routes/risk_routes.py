from fastapi import APIRouter, Depends

from app.controllers.risk_controller import evaluate, get_risk
from app.middlewares.auth import current_user
from app.middlewares.roles import require_admin
from app.schemas.risk_schema import RiskInput


router = APIRouter(prefix="/riesgo", tags=["Riesgo"])


@router.get("")
def risk_list(user: dict = Depends(require_admin)):
    return get_risk(user)


@router.post("/evaluar")
def risk_evaluate(payload: RiskInput, user: dict = Depends(current_user)):
    return evaluate(payload, user)
