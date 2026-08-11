# CyberLey — React + FastAPI + Supabase

Migración del proyecto Streamlit a una arquitectura separada:

- `frontend/`: React + Vite + pnpm
- `backend/`: FastAPI + Python
- `legacy_streamlit/`: implementación anterior conservada como referencia
- `Notebook/`: análisis y recursos existentes

## Inicio rápido

### Frontend
```powershell
cd frontend
pnpm install
Copy-Item .env.example .env
pnpm dev
```

### Backend
```powershell
cd backend
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python run.py
```

Configura ambos `.env` antes de iniciar. Nunca subas claves secretas a GitHub.
