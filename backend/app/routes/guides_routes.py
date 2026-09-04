from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from app.controllers.guides_controller import assign_for_admin, create_for_admin, delete_for_admin, get_admin_guides, get_guides, mark_complete, update_for_admin
from app.middlewares.auth import current_user
from app.middlewares.roles import require_admin
from app.schemas.guide_schema import GuideAssignment, GuideCreate, GuideUpdate
from app.utils.uploads import read_limited_upload

router = APIRouter(prefix="/guias", tags=["Guías"])

@router.get("/admin", summary="Listar guías para administración")
def admin_guides(user: dict = Depends(require_admin)):
    return get_admin_guides(user)

@router.post("/admin", status_code=status.HTTP_201_CREATED, summary="Crear una guía")
async def create_admin_guide(
    titulo: str = Form(...), categoria: str = Form(...), descripcion: str = Form(""), contenido: str = Form(""),
    nivel_recomendado: str = Form("general"), tipo_recurso: str = Form("documento"), estado: str = Form("borrador"),
    archivo: UploadFile | None = File(None), user: dict = Depends(require_admin),
):
    payload = GuideCreate(titulo=titulo, categoria=categoria, descripcion=descripcion, contenido=contenido, nivel_recomendado=nivel_recomendado, tipo_recurso=tipo_recurso, estado=estado)
    file_data = None
    if archivo:
        content = await read_limited_upload(archivo, allowed_suffixes={".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png", ".webp", ".mp4", ".webm"}, max_bytes=50 * 1024 * 1024)
        file_data = (archivo.filename or "archivo", archivo.content_type or "application/octet-stream", content)
    return create_for_admin(payload, file_data, user)

@router.post("/admin/{guide_id}/asignar", summary="Asignar una guía a participantes")
def assign_admin_guide(guide_id: UUID, payload: GuideAssignment, user: dict = Depends(require_admin)):
    return assign_for_admin(str(guide_id), payload, user)

@router.put("/admin/{guide_id}", summary="Editar una guía")
def edit_admin_guide(guide_id: UUID, payload: GuideUpdate, user: dict = Depends(require_admin)):
    return update_for_admin(str(guide_id), payload, user)

@router.delete("/admin/{guide_id}", summary="Eliminar una guía")
def remove_admin_guide(guide_id: UUID, user: dict = Depends(require_admin)):
    return delete_for_admin(str(guide_id), user)

@router.get("", summary="Listar guías y progreso del usuario")
def guides(user: dict = Depends(current_user)):
    return get_guides(user)

@router.post("/{guide_id}/completar", status_code=status.HTTP_200_OK, summary="Marcar una guía como completada")
def complete(guide_id: UUID, user: dict = Depends(current_user)):
    return mark_complete(str(guide_id), user)
