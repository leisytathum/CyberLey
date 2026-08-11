from typing import TypedDict


class Participant(TypedDict, total=False):
    id: str
    nombre: str
    correo: str
    ciudad: str
