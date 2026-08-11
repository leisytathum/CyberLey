from fastapi import APIRouter, Depends

from app.controllers.auth_controller import me
from app.middlewares.auth import current_user


router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.get("/me")
def current_session(user: dict = Depends(current_user)):
    return me(user)
