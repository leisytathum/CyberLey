from app.database.supabase_client import SupabaseRESTClient
from concurrent.futures import ThreadPoolExecutor
from app.utils.exceptions import ConflictError, ResourceNotFoundError
from app.schemas.guide_schema import GuideAssignment, GuideCreate, GuideUpdate
from pathlib import Path
from uuid import uuid4


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


def list_admin_guides(token: str) -> dict:
    db = SupabaseRESTClient(token)
    guides = db.get_all("guias_ciberseguridad", order="fecha_creacion.desc")
    assignments = db.get_all("guias_asignadas")
    completed = db.get_all("guias_completadas")
    assigned_count, completed_count = {}, {}
    for row in assignments:
        assigned_count[row["id_guia"]] = assigned_count.get(row["id_guia"], 0) + 1
    for row in completed:
        completed_count[row["id_guia"]] = completed_count.get(row["id_guia"], 0) + 1
    items = [{**guide, "envios": assigned_count.get(guide["id_guia"], 0), "completadas": completed_count.get(guide["id_guia"], 0)} for guide in guides]
    return {"items": items, "total": len(items)}


def create_guide(token: str, admin_id: str, payload: GuideCreate, file_data: tuple[str, str, bytes] | None) -> dict:
    db = SupabaseRESTClient(token)
    data = payload.model_dump()
    data["creado_por"] = admin_id
    if file_data:
        filename, content_type, content = file_data
        safe_name = Path(filename).name.replace(" ", "-")
        path = f"{uuid4()}/{safe_name}"
        data["archivo_url"] = db.upload("guias", path, content, content_type)
        data["archivo_nombre"] = Path(filename).name
    created = db.insert("guias_ciberseguridad", data)
    return created[0]


def assign_guide(token: str, guide_id: str, payload: GuideAssignment) -> dict:
    db = SupabaseRESTClient(token)
    if not db.get("guias_ciberseguridad", filters={"id_guia": f"eq.{guide_id}"}, limit=1):
        raise ResourceNotFoundError("La guía solicitada no existe.")
    rows = [{"id_guia": guide_id, "id_participante": str(participant_id), "mensaje": payload.mensaje} for participant_id in payload.participantes]
    created = db.upsert("guias_asignadas", rows, on_conflict="id_guia,id_participante")
    db.update("guias_ciberseguridad", {"estado": "publicada"}, filters={"id_guia": f"eq.{guide_id}"})
    return {"asignadas": len(created), "id_guia": guide_id}


def update_guide(token: str, guide_id: str, payload: GuideUpdate) -> dict:
    db = SupabaseRESTClient(token)
    updated = db.update("guias_ciberseguridad", payload.model_dump(), filters={"id_guia": f"eq.{guide_id}"})
    if not updated:
        raise ResourceNotFoundError("La guía solicitada no existe.")
    return updated[0]


def delete_guide(token: str, guide_id: str) -> dict:
    db = SupabaseRESTClient(token)
    db.delete("guias_asignadas", filters={"id_guia": f"eq.{guide_id}"})
    db.delete("guias_completadas", filters={"id_guia": f"eq.{guide_id}"})
    deleted = db.delete("guias_ciberseguridad", filters={"id_guia": f"eq.{guide_id}"})
    if not deleted:
        raise ResourceNotFoundError("La guía solicitada no existe.")
    return {"eliminada": True, "id_guia": guide_id}


def complete_guide(token: str, user_id: str, guide_id: str) -> dict:
    db = SupabaseRESTClient(token)
    guides = db.get("guias_ciberseguridad", filters={"id_guia": f"eq.{guide_id}"}, limit=1)
    if not guides:
        raise ResourceNotFoundError("La guía solicitada no existe.")
    participants = db.get_all("participantes", filters={"id_usuario": f"eq.{user_id}"})
    if not participants:
        raise ResourceNotFoundError("Tu cuenta no tiene una ficha de participante asociada.")
    participant_id = participants[0]["id_participante"]
    existing = db.get_all("guias_completadas", filters={"id_participante": f"eq.{participant_id}", "id_guia": f"eq.{guide_id}"})
    if existing:
        return {"completada": True, "id_guia": guide_id, "ya_completada": True}
    try:
        db.insert("guias_completadas", {"id_participante": participant_id, "id_guia": guide_id})
    except RuntimeError as exc:
        if "duplicate" in str(exc).lower() or "unique" in str(exc).lower():
            raise ConflictError("La guía ya estaba marcada como completada.") from exc
        raise
    return {"completada": True, "id_guia": guide_id, "ya_completada": False}
