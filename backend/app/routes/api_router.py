from fastapi import APIRouter

from app.routes import (
    administration_routes,
    auth_routes,
    backups_routes,
    cleaning_routes,
    dashboard_routes,
    dynamic_surveys_routes,
    health_routes,
    guides_routes,
    imports_routes,
    participants_routes,
    reports_routes,
    risk_routes,
    surveys_routes,
    user_portal_routes,
)


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_routes.router)
api_router.include_router(auth_routes.router)
api_router.include_router(user_portal_routes.router)
api_router.include_router(guides_routes.router)
api_router.include_router(dashboard_routes.router)
api_router.include_router(dynamic_surveys_routes.router)
api_router.include_router(participants_routes.router)
api_router.include_router(surveys_routes.router)
api_router.include_router(risk_routes.router)
api_router.include_router(reports_routes.router)
api_router.include_router(imports_routes.router)
api_router.include_router(cleaning_routes.router)
api_router.include_router(backups_routes.router)
api_router.include_router(administration_routes.router)
