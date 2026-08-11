# Estado de migración

Esta carpeta ya usa React + FastAPI como aplicación principal. El código Streamlit original se conserva sin modificaciones funcionales en `legacy_streamlit/`.

## Módulos conectados
- Login y registro con Supabase Auth
- Perfiles y roles
- Dashboard administrativo (métricas principales)
- Participantes, encuestas, riesgo y reportes (consulta)
- Evaluación de riesgo con el mismo algoritmo de Streamlit
- Importación CSV (validación)
- Diagnóstico de limpieza
- Exportación de respaldo JSON
- Administración de perfiles (consulta)

## Pendientes de paridad total
Las operaciones destructivas/avanzadas del Streamlit original (restaurar respaldos, limpieza masiva, formatos de reportes específicos y algunas transformaciones de importación) permanecen en `legacy_streamlit/` y deben trasladarse después de validar las políticas RLS y los esquemas exactos en Supabase. Se dejaron fuera de ejecución automática para no dañar datos reales.
