from pathlib import Path

from fastapi import UploadFile

from app.utils.exceptions import BusinessValidationError


async def read_limited_upload(
    upload: UploadFile,
    *,
    allowed_suffixes: set[str],
    max_bytes: int,
) -> bytes:
    """Read an upload with extension, empty-file and size validation."""
    filename = (upload.filename or "").strip()
    suffix = Path(filename).suffix.casefold()
    if suffix not in allowed_suffixes:
        expected = ", ".join(sorted(allowed_suffixes))
        raise BusinessValidationError(f"Formato de archivo inválido. Formatos permitidos: {expected}.")
    content = await upload.read(max_bytes + 1)
    if not content:
        raise BusinessValidationError("El archivo está vacío.")
    if len(content) > max_bytes:
        megabytes = max_bytes // (1024 * 1024)
        raise BusinessValidationError(f"El archivo supera el límite de {megabytes} MB.")
    return content
