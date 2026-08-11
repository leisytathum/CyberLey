import os
import time
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from httpx import ConnectError, TimeoutException
from supabase import Client, create_client


# =========================
# CONFIGURACIÓN GENERAL
# =========================

st.set_page_config(
    page_title="CyberLey | Administración",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

ROOT_DIR = Path(__file__).resolve().parents[1]

load_dotenv(ROOT_DIR / ".env")

SUPABASE_URL = "https://zytfjhwdrpbmkkrdbagj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp5dGZqaHdkcnBibWtrcmRiYWdqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY4MjY0NjQsImV4cCI6MjA5MjQwMjQ2NH0.fx9zkY5iWLH-rm0MWEFfh09g7mBPeu-Zgi9vUMm6oAg"

if not SUPABASE_KEY:
    st.error("No se encontró SUPABASE_KEY en el archivo .env.")
    st.stop()

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# =========================
# RESTAURAR SESIÓN
# =========================

access_token = st.session_state.get("access_token")
refresh_token = st.session_state.get("refresh_token")

if access_token and refresh_token:

    sesion_restaurada = False

    for intento in range(2):
        try:
            supabase.auth.set_session(
                access_token,
                refresh_token
            )

            sesion_restaurada = True
            break

        except (TimeoutException, ConnectError):
            if intento == 0:
                time.sleep(1)

    if not sesion_restaurada:
        st.error(
            "No se pudo conectar con Supabase en este momento. "
            "Revisa tu conexión e intenta nuevamente."
        )

        if st.button("Reintentar conexión"):
            st.rerun()

        st.stop()


# =========================
# VALIDAR ADMIN
# =========================

if "usuario" not in st.session_state:
    st.warning("Debes iniciar sesión primero.")
    st.switch_page("app.py")

if st.session_state.get("rol") != "admin":
    st.warning("Esta sección es exclusiva para administradores.")
    st.switch_page("pages/usuario.py")


# =========================
# CARGAR CSS
# =========================

def cargar_css():
    ruta_css = ROOT_DIR / "css" / "dashboard.css"

    with open(
        ruta_css,
        "r",
        encoding="utf-8"
    ) as archivo:
        st.markdown(
            f"<style>{archivo.read()}</style>",
            unsafe_allow_html=True
        )


cargar_css()


# =========================
# FUNCIONES
# =========================

def consultar_tabla(
    nombre_tabla: str,
    columnas: str = "*"
) -> list[dict]:

    respuesta = (
        supabase
        .table(nombre_tabla)
        .select(columnas)
        .execute()
    )

    return respuesta.data or []


def guardar_toast(
    mensaje: str,
    icono: str = "✅"
):
    st.session_state["toast_mensaje"] = mensaje
    st.session_state["toast_icono"] = icono


def mostrar_toast_pendiente():
    mensaje = st.session_state.pop(
        "toast_mensaje",
        None
    )

    icono = st.session_state.pop(
        "toast_icono",
        "✅"
    )

    if mensaje:
        st.toast(
            mensaje,
            icon=icono,
            duration=4
        )


def preparar_usuarios(
    perfiles: list[dict],
    participantes: list[dict],
    respuestas: list[dict]
) -> pd.DataFrame:

    df_perfiles = pd.DataFrame(
        perfiles
    )

    df_participantes = pd.DataFrame(
        participantes
    )

    df_respuestas = pd.DataFrame(
        respuestas
    )

    if df_perfiles.empty:
        return pd.DataFrame()

    if not df_participantes.empty:
        df_perfiles = df_perfiles.merge(
            df_participantes,
            left_on="id",
            right_on="id_usuario",
            how="left"
        )

    else:
        df_perfiles["ciudad"] = "Sin registrar"
        df_perfiles["nivel_educativo"] = "Sin registrar"
        df_perfiles["edad"] = None
        df_perfiles["genero"] = "Sin registrar"

    if not df_respuestas.empty:

        df_respuestas["fecha_respuesta"] = pd.to_datetime(
            df_respuestas["fecha_respuesta"],
            errors="coerce"
        )

        conteo_encuestas = (
            df_respuestas
            .groupby("id_usuario")
            .size()
            .reset_index(name="encuestas_realizadas")
        )

        ultima_encuesta = (
            df_respuestas
            .sort_values("fecha_respuesta")
            .drop_duplicates(
                subset=["id_usuario"],
                keep="last"
            )
            [
                [
                    "id_usuario",
                    "fecha_respuesta",
                    "puntaje_riesgo",
                    "clasificacion_riesgo"
                ]
            ]
            .rename(
                columns={
                    "fecha_respuesta": "ultima_evaluacion"
                }
            )
        )

        df_perfiles = df_perfiles.merge(
            conteo_encuestas,
            left_on="id",
            right_on="id_usuario",
            how="left",
            suffixes=("", "_encuesta")
        )

        df_perfiles = df_perfiles.merge(
            ultima_encuesta,
            left_on="id",
            right_on="id_usuario",
            how="left",
            suffixes=("", "_ultima")
        )

    else:
        df_perfiles["encuestas_realizadas"] = 0
        df_perfiles["ultima_evaluacion"] = None
        df_perfiles["puntaje_riesgo"] = None
        df_perfiles["clasificacion_riesgo"] = "Sin evaluar"

    df_perfiles["encuestas_realizadas"] = (
        df_perfiles["encuestas_realizadas"]
        .fillna(0)
        .astype(int)
    )

    df_perfiles["clasificacion_riesgo"] = (
        df_perfiles["clasificacion_riesgo"]
        .fillna("Sin evaluar")
        .str.title()
    )

    for columna in [
        "ciudad",
        "nivel_educativo",
        "genero"
    ]:
        if columna in df_perfiles.columns:
            df_perfiles[columna] = (
                df_perfiles[columna]
                .fillna("Sin registrar")
            )

    return df_perfiles


mostrar_toast_pendiente()


# =========================
# CARGAR DATOS
# =========================

try:
    perfiles = consultar_tabla(
        "perfiles",
        (
            "id, nombre_completo, rol, foto_url, "
            "fecha_creacion"
        )
    )

    participantes = consultar_tabla(
        "participantes",
        (
            "id_participante, id_usuario, edad, genero, "
            "ciudad, nivel_educativo, fecha_registro"
        )
    )

    respuestas_ciberseguridad = consultar_tabla(
        "respuestas_encuesta_ciberseguridad",
        (
            "id_respuesta, id_usuario, fecha_respuesta, "
            "puntaje_riesgo, clasificacion_riesgo"
        )
    )

    reportes = consultar_tabla(
        "reportes",
        (
            "tipo_reporte, descripcion, fecha_generacion"
        )
    )

except Exception as error:
    st.error(
        "No se pudieron cargar los datos administrativos."
    )
    st.write(error)
    st.stop()


df_usuarios = preparar_usuarios(
    perfiles,
    participantes,
    respuestas_ciberseguridad
)

df_reportes = pd.DataFrame(
    reportes
)


# =========================
# SIDEBAR
# =========================

with st.sidebar:

    st.image(
        str(ROOT_DIR / "Logo.png"),
        use_container_width=True
    )

    st.markdown(
        "<div class='sidebar-title'>Panel Administrador</div>",
        unsafe_allow_html=True
    )

    menu = st.radio(
        "Menú",
        [
            "🏠 Inicio",
            "👥 Participantes",
            "📝 Encuestas",
            "⚠️ Riesgo",
            "🧹 Limpieza de datos",
            "📥 Importar datos históricos",
            "💾 Respaldo y recuperación",
            "📄 Reportes",
            "⚙️ Administración"
        ],
        index=8,
        label_visibility="collapsed"
    )

    st.divider()

    if st.button(
        "🚪 Cerrar sesión",
        use_container_width=True
    ):
        st.session_state.clear()
        st.switch_page("app.py")


# =========================
# NAVEGACIÓN
# =========================

if menu == "🏠 Inicio":
    st.switch_page("pages/dashboard.py")

elif menu == "👥 Participantes":
    st.switch_page("pages/participantes.py")

elif menu == "📝 Encuestas":
    st.switch_page("pages/encuestas.py")

elif menu == "⚠️ Riesgo":
    st.switch_page("pages/riesgo.py")

elif menu == "🧹 Limpieza de datos":
    st.switch_page("pages/limpieza.py")

elif menu == "📥 Importar datos históricos":
    st.switch_page("pages/importar_datos.py")

elif menu == "💾 Respaldo y recuperación":
    st.switch_page("pages/respaldo.py")

elif menu == "📄 Reportes":
    st.switch_page("pages/reportes.py")


# =========================
# ENCABEZADO
# =========================

st.markdown(
    """
<div class="page-heading">
<h1>Administración del sistema</h1>
<p>
Gestiona usuarios, revisa roles, monitorea actividad y valida
el estado general de los datos principales de CyberLey.
</p>
</div>
""",
    unsafe_allow_html=True
)


# =========================
# MÉTRICAS
# =========================

if df_usuarios.empty:
    total_usuarios = 0
    total_admins = 0
    total_participantes = 0
else:
    total_usuarios = len(df_usuarios)

    total_admins = len(
        df_usuarios[
            df_usuarios["rol"] == "admin"
        ]
    )

    total_participantes = len(
        df_usuarios[
            df_usuarios["rol"] == "usuario"
        ]
    )

total_encuestas = len(
    respuestas_ciberseguridad
)

total_reportes = len(
    reportes
)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Usuarios totales",
        total_usuarios
    )

with col2:
    st.metric(
        "Administradores",
        total_admins
    )

with col3:
    st.metric(
        "Participantes",
        total_participantes
    )

with col4:
    st.metric(
        "Encuestas",
        total_encuestas
    )

with col5:
    st.metric(
        "Reportes",
        total_reportes
    )


# =========================
# PESTAÑAS
# =========================

tab_usuarios, tab_roles, tab_actividad, tab_sistema = st.tabs(
    [
        "👥 Usuarios",
        "🔐 Roles",
        "📌 Actividad",
        "🧩 Estado del sistema"
    ]
)


# =========================
# TAB USUARIOS
# =========================

with tab_usuarios:

    st.markdown("### Usuarios registrados")

    if df_usuarios.empty:
        st.info(
            "Todavía no existen usuarios registrados."
        )

    else:
        filtro_rol = st.selectbox(
            "Filtrar por rol",
            [
                "Todos",
                "admin",
                "usuario"
            ]
        )

        df_tabla = df_usuarios.copy()

        if filtro_rol != "Todos":
            df_tabla = df_tabla[
                df_tabla["rol"] == filtro_rol
            ]

        columnas_tabla = [
            "nombre_completo",
            "rol",
            "ciudad",
            "nivel_educativo",
            "encuestas_realizadas",
            "puntaje_riesgo",
            "clasificacion_riesgo",
            "fecha_creacion"
        ]

        columnas_existentes = [
            columna
            for columna in columnas_tabla
            if columna in df_tabla.columns
        ]

        df_tabla = df_tabla[
            columnas_existentes
        ].copy()

        df_tabla = df_tabla.rename(
            columns={
                "nombre_completo": "Nombre completo",
                "rol": "Rol",
                "ciudad": "Ciudad",
                "nivel_educativo": "Nivel educativo",
                "encuestas_realizadas": "Encuestas",
                "puntaje_riesgo": "Puntaje",
                "clasificacion_riesgo": "Riesgo",
                "fecha_creacion": "Fecha de creación"
            }
        )

        st.dataframe(
            df_tabla,
            use_container_width=True,
            hide_index=True
        )


# =========================
# TAB ROLES
# =========================

with tab_roles:

    st.markdown("### Gestión de roles")

    st.info(
        "Desde aquí puedes cambiar el rol de un usuario entre "
        "'usuario' y 'admin'. Usa esta opción con cuidado."
    )

    if df_usuarios.empty:
        st.info(
            "No hay usuarios disponibles para administrar."
        )

    else:
        opciones = {}

        for _, fila in df_usuarios.iterrows():

            nombre = fila.get(
                "nombre_completo",
                "Sin nombre"
            )

            rol = fila.get(
                "rol",
                "sin rol"
            )

            user_id = fila.get(
                "id"
            )

            etiqueta = (
                f"{nombre} — Rol actual: {rol} — {str(user_id)[:8]}"
            )

            opciones[etiqueta] = user_id

        usuario_seleccionado = st.selectbox(
            "Selecciona un usuario",
            opciones.keys()
        )

        usuario_id = opciones[
            usuario_seleccionado
        ]

        usuario_actual = df_usuarios[
            df_usuarios["id"] == usuario_id
        ].iloc[0]

        rol_actual = usuario_actual.get(
            "rol",
            "usuario"
        )

        nuevo_rol = st.selectbox(
            "Nuevo rol",
            [
                "usuario",
                "admin"
            ],
            index=(
                1
                if rol_actual == "admin"
                else 0
            )
        )

        confirmar = st.checkbox(
            "Confirmo que deseo actualizar el rol de este usuario."
        )

        if st.button(
            "Actualizar rol",
            use_container_width=True,
            disabled=not confirmar
        ):

            if usuario_id == st.session_state.get("usuario_id"):
                st.error(
                    "No puedes cambiar tu propio rol desde esta pantalla."
                )

            else:
                try:
                    (
                        supabase
                        .table("perfiles")
                        .update(
                            {
                                "rol": nuevo_rol
                            }
                        )
                        .eq(
                            "id",
                            usuario_id
                        )
                        .execute()
                    )

                    guardar_toast(
                        "Rol actualizado correctamente.",
                        "✅"
                    )

                    st.rerun()

                except Exception as error:
                    st.error(
                        "No se pudo actualizar el rol."
                    )
                    st.write(error)


# =========================
# TAB ACTIVIDAD
# =========================

with tab_actividad:

    st.markdown("### Actividad reciente")

    if respuestas_ciberseguridad:

        df_respuestas = pd.DataFrame(
            respuestas_ciberseguridad
        )

        df_respuestas["fecha_respuesta"] = pd.to_datetime(
            df_respuestas["fecha_respuesta"],
            errors="coerce"
        )

        df_actividad = df_respuestas.copy()

        if not df_usuarios.empty:

            df_actividad = df_actividad.merge(
                df_usuarios[
                    [
                        "id",
                        "nombre_completo",
                        "rol"
                    ]
                ],
                left_on="id_usuario",
                right_on="id",
                how="left"
            )

        columnas_actividad = [
            "fecha_respuesta",
            "nombre_completo",
            "puntaje_riesgo",
            "clasificacion_riesgo"
        ]

        columnas_existentes = [
            columna
            for columna in columnas_actividad
            if columna in df_actividad.columns
        ]

        df_actividad = (
            df_actividad[columnas_existentes]
            .sort_values(
                "fecha_respuesta",
                ascending=False
            )
            .head(10)
        )

        df_actividad = df_actividad.rename(
            columns={
                "fecha_respuesta": "Fecha",
                "nombre_completo": "Usuario",
                "puntaje_riesgo": "Puntaje",
                "clasificacion_riesgo": "Riesgo"
            }
        )

        st.dataframe(
            df_actividad,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info(
            "Todavía no hay evaluaciones registradas."
        )

    st.markdown("### Reportes generados")

    if df_reportes.empty:
        st.info(
            "Todavía no hay reportes generados."
        )

    else:
        df_historial = df_reportes.copy()

        if "fecha_generacion" in df_historial.columns:
            df_historial["fecha_generacion"] = pd.to_datetime(
                df_historial["fecha_generacion"],
                errors="coerce"
            )

        df_historial = (
            df_historial
            .sort_values(
                "fecha_generacion",
                ascending=False
            )
            .head(10)
        )

        df_historial = df_historial.rename(
            columns={
                "tipo_reporte": "Tipo de reporte",
                "descripcion": "Descripción",
                "fecha_generacion": "Fecha"
            }
        )

        st.dataframe(
            df_historial,
            use_container_width=True,
            hide_index=True
        )


# =========================
# TAB SISTEMA
# =========================

with tab_sistema:

    st.markdown("### Estado general de datos")

    estado_sistema = pd.DataFrame({
        "Componente": [
            "Perfiles",
            "Participantes",
            "Encuesta nueva",
            "Reportes",
            "Importación CSV histórico",
            "Limpieza de datos",
            "Respaldo y recuperación"
        ],
        "Estado": [
            "Activo",
            "Activo",
            "Activo",
            "Activo",
            "Activo",
            "Activo",
            "Activo"
        ],
        "Descripción": [
            "Usuarios del sistema y sus roles.",
            "Datos personales básicos de los usuarios.",
            "Respuestas de la encuesta de ciberseguridad.",
            "Reportes generados por administradores.",
            "Carga y limpieza de CSV externo.",
            "Normalización y revisión de calidad.",
            "Generación y restauración de copias de seguridad."
        ]
    })

    st.dataframe(
        estado_sistema,
        use_container_width=True,
        hide_index=True
    )

    st.success(
        "✅ El módulo administrativo está conectado a la estructura nueva de CyberLey."
    )