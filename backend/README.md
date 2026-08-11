# CyberLey Backend

Backend de CyberLey construido con FastAPI y Supabase.

## Arquitectura

```text
routes -> controllers -> services -> database/Supabase
```

- `config/`: variables de entorno y logging.
- `controllers/`: coordinación entre las rutas y los servicios.
- `database/`: acceso centralizado a Supabase.
- `jobs/`: procesos reutilizables o programables, como respaldos.
- `middlewares/`: autenticación, roles, logs, errores y headers.
- `models/`: representaciones de entidades del dominio.
- `routes/`: endpoints HTTP.
- `schemas/`: validación de entrada/salida con Pydantic.
- `services/`: lógica de negocio.
- `utils/`: utilidades compartidas.

## Primera instalación en Windows

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
```

Crea `backend/.env` tomando como base `.env.example`.

## Ejecutar

```powershell
python run.py
```

## Después de un `git pull`

Si el entorno `venv` ya existe:

```powershell
cd backend
venv\Scripts\activate
python -m pip install -r requirements.txt
python run.py
```

`python -m pip install -r requirements.txt` es seguro volver a ejecutarlo; instalará o actualizará únicamente lo necesario.
