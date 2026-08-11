from typing import Literal, TypedDict


class Profile(TypedDict, total=False):
    id: str
    nombre_completo: str
    rol: Literal["admin", "usuario"]
