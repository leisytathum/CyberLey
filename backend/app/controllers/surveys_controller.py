from fastapi import HTTPException

from app.services.surveys_service import (
    get_survey_statistics,
    list_surveys,
)


def get_surveys(user: dict) -> dict:
    try:
        items = list_surveys(
            user["token"]
        )

        statistics = (
            get_survey_statistics(
                user["token"]
            )
        )

        return {
            "items": items,
            "total": len(items),
            "estadisticas": statistics,
        }

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc