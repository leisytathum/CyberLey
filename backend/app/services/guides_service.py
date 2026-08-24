from app.database.supabase_client import SupabaseRESTClient
from concurrent.futures import ThreadPoolExecutor


def list_guides(token: str, user_id: str) -> dict:
    db = SupabaseRESTClient(token)
    with ThreadPoolExecutor(max_workers=2) as executor:
        guides_future = executor.submit(
            db.get_all, "guias_ciberseguridad", order="fecha_creacion.desc"
        )
        participants_future = executor.submit(
            db.get_all,
            "participantes",
            filters={"id_usuario": f"eq.{user_id}"},
        )
        guides = guides_future.result()
        participants = participants_future.result()
    participant_id = participants[0].get("id_participante") if participants else None
    completed = db.get_all("guias_completadas", filters={"id_participante": f"eq.{participant_id}"}) if participant_id else []
    completed_ids = {row.get("id_guia") for row in completed}
    return {"items": [{**guide, "completada": guide.get("id_guia") in completed_ids} for guide in guides], "total": len(guides)}


def complete_guide(token: str, user_id: str, guide_id: str) -> dict:
    db = SupabaseRESTClient(token)
    participants = db.get_all("participantes", filters={"id_usuario": f"eq.{user_id}"})
    if not participants: raise ValueError("Tu cuenta no tiene una ficha de participante asociada.")
    participant_id = participants[0]["id_participante"]
    existing = db.get_all("guias_completadas", filters={"id_participante": f"eq.{participant_id}", "id_guia": f"eq.{guide_id}"})
    if not existing: db.insert("guias_completadas", {"id_participante": participant_id, "id_guia": guide_id})
    return {"completada": True, "id_guia": guide_id}
