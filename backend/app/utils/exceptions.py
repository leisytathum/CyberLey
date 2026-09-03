class CyberLeyError(Exception):
    """Error de dominio seguro para exponer mediante la API."""

    status_code = 400
    code = "domain_error"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ResourceNotFoundError(CyberLeyError):
    status_code = 404
    code = "not_found"


class ConflictError(CyberLeyError):
    status_code = 409
    code = "conflict"


class BusinessValidationError(CyberLeyError):
    status_code = 422
    code = "validation_error"


class DataAccessError(CyberLeyError):
    status_code = 503
    code = "data_service_unavailable"
