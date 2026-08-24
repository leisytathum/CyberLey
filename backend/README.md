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

Aplica en Supabase SQL Editor los archivos de `database/migrations/` en orden.
Las migraciones incluyen las columnas del registro, las políticas RLS y el
trigger que crea el perfil y participante al registrar una cuenta.

## Ejecutar

```powershell
python run.py
```
## Ejecutar seeds
cd backend
venv\Scripts\activate
python seeds/run_seeds.py

Los seeds crean exclusivamente usuarios y perfiles; no generan encuestas,
resultados ni estadísticas simuladas.

## Pruebas

```powershell
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
```

Con un `.env` conectado y los usuarios seed disponibles, el smoke test de solo
lectura valida las rutas reales y la separación de roles:

```powershell
.\venv\Scripts\python.exe -m tests.live_smoke
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
