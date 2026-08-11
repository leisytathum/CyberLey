from fastapi import APIRouter

from app.controllers.health_controller import health_status
from app.schemas.common_schema import HealthResponse


router = APIRouter(tags=["Sistema"])


@router.get("/health", response_model=HealthResponse)
def health():
    return health_status()
