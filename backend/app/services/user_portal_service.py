from concurrent.futures import ThreadPoolExecutor

from app.services.dynamic_surveys_service import available_surveys
from app.services.guides_service import list_guides
from app.services.risk_service import user_risk_responses
from app.database.supabase_client import SupabaseRESTClient


def build_user_summary(token: str, user_id: str) -> dict:
    """Build the user landing payload while independent queries run concurrently."""
    with ThreadPoolExecutor(max_workers=3) as executor:
        results_future = executor.submit(user_risk_responses, token, user_id)
        surveys_future = executor.submit(available_surveys, token, user_id)
        guides_future = executor.submit(list_guides, token, user_id)
        results = results_future.result()
        surveys = surveys_future.result()
        guides_payload = guides_future.result()

    guides = guides_payload.get("items", [])
    completed_guides = sum(bool(guide.get("completada")) for guide in guides)
    completed_surveys = sum(bool(survey.get("respondida")) for survey in surveys)
    scores = [float(item["puntaje_riesgo"]) for item in results if item.get("puntaje_riesgo") is not None]
    distribution = {
        level: sum(item.get("clasificacion_riesgo") == level for item in results)
        for level in ("bajo", "medio", "alto")
    }
    return {
        "ultimo_resultado": results[0] if results else None,
        "resultados_recientes": results[:5],
        "guias_sugeridas": [guide for guide in guides if not guide.get("completada")][:3],
        "metricas": {
            "evaluaciones": len(results),
            "encuestas_disponibles": len(surveys),
            "encuestas_pendientes": len(surveys) - completed_surveys,
            "guias_disponibles": len(guides),
            "guias_completadas": completed_guides,
            "promedio_riesgo": round(sum(scores) / len(scores), 1) if scores else None,
        },
        "distribucion_riesgo": distribution,
    }


def complete_user_onboarding(token: str) -> dict:
    result = SupabaseRESTClient(token).rpc("completar_onboarding_usuario")
    return result if isinstance(result, dict) else {"onboarding_completado": True}
