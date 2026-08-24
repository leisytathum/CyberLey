# Estado de migración

Esta carpeta ya usa React + FastAPI como aplicación principal. El código Streamlit original se conserva sin modificaciones funcionales en `legacy_streamlit/`.

## Módulos migrados

- Login, registro, perfiles y roles con Supabase Auth
- Dashboard y analítica administrativa con datos reales
- Participantes, encuestas, riesgo y detalle de evaluaciones
- Evaluación e historial de riesgo del usuario
- Guías educativas para administradores y usuarios
- Importación histórica CSV: validación, limpieza, vista previa y descarga
- Limpieza con diagnóstico, previsualización, confirmación y aplicación
- Generación, filtrado, historial y descarga de reportes CSV
- Respaldo comprimido, validación previa y restauración por upsert
- Administración de usuarios, roles, métricas y actividad

## Paridad funcional

La aplicación React + FastAPI incluye dashboard, participantes, encuestas,
riesgo, analítica, guías, importación histórica, limpieza confirmada, reportes,
respaldo/restauración, administración y área de usuario. `legacy_streamlit/`
permanece como referencia hasta completar la validación manual de aceptación.

Las políticas reproducibles están en `backend/database/migrations/003_versionar_rls.sql`
y el alta automática Auth → perfil/participante en `004_registro_auth.sql`.
Las migraciones deben aplicarse en orden en Supabase antes de desplegar.

## Decisiones conservadas del legacy

El importador histórico no inserta registros en Supabase: igual que la versión
Streamlit, prepara un CSV limpio para análisis externo. Se descartaron solamente
la navegación, el CSS y la autenticación propios de Streamlit, porque sus
equivalentes pertenecen a React, los layouts actuales y Supabase Auth.

## Verificación

```powershell
cd backend
.\venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\venv\Scripts\python.exe -m tests.live_smoke

cd ..\frontend
npm run lint
npm run build
```
