from __future__ import annotations

import sys
from pathlib import Path


# Permite ejecutar:
# python seeds/run_seeds.py
BACKEND_DIR = Path(__file__).resolve().parent.parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


from seeds.seed_users import seed_users


def main() -> None:
    print("=" * 55)
    print("CYBERLEY - CARGA DE USUARIOS DE PRUEBA")
    print("=" * 55)

    try:
        seed_users()

        print("\n" + "=" * 55)
        print("SEEDS EJECUTADOS CORRECTAMENTE")
        print("=" * 55)

        print("\nCredenciales de prueba:")

        print(
            "\nADMIN\n"
            "Correo: admin@cyberley.com\n"
            "Contraseña: Admin123*"
        )

        print(
            "\nUSUARIOS\n"
            "usuario1@cyberley.com\n"
            "usuario2@cyberley.com\n"
            "usuario3@cyberley.com\n"
            "Contraseña para todos: Usuario123*"
        )

    except Exception as exc:
        print("\nERROR EJECUTANDO SEEDS")
        print(str(exc))
        raise


if __name__ == "__main__":
    main()