import os
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from supabase import Client, create_client


# =========================
# CONFIGURACIÓN GENERAL
# =========================

st.set_page_config(
    page_title="CyberLey | Limpieza de datos",
    page_icon="🧹",
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
    supabase.auth.set_session(
        access_token,
        refresh_token
    )


# =========================
# VALIDAR ACCESO ADMIN
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
# NOTIFICACIONES
# =========================

def guardar_notificacion(
    mensaje: str,
    icono: str = "✅"
):
    st.session_state["toast_mensaje"] = mensaje
    st.session_state["toast_icono"] = icono


def mostrar_notificacion_pendiente():
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


mostrar_notificacion_pendiente()


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
        index=4,
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

elif menu == "📥 Importar datos históricos":
    st.switch_page("pages/importar_datos.py")

elif menu == "💾 Respaldo y recuperación":
    st.switch_page("pages/respaldo.py")

elif menu == "📄 Reportes":
    st.switch_page("pages/reportes.py")

elif menu == "⚙️ Administración":
    st.switch_page("pages/administracion.py")


# =========================
# CONSULTAS A SUPABASE
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


# =========================
# FUNCIONES DE LIMPIEZA
# =========================

def normalizar_texto(valor) -> str:
    if valor is None:
        return ""

    texto = str(valor).strip()

    if texto == "":
        return ""

    return " ".join(
        texto.split()
    ).title()


def normalizar_genero(valor) -> str:
    texto = normalizar_texto(valor)

    equivalencias = {
        "Femenino": "Femenino",
        "Masculino": "Masculino",
        "Otro": "Otro",
        "Prefiero No Responder": "Prefiero no responder"
    }

    return equivalencias.get(
        texto,
        texto
    )


def normalizar_nivel_educativo(valor) -> str:
    texto = normalizar_texto(valor)

    equivalencias = {
        "Secundaria": "Secundaria",
        "Universidad": "Universidad",
        "Técnico": "Técnico",
        "Tecnico": "Técnico",
        "Posgrado": "Posgrado",
        "Otro": "Otro"
    }

    return equivalencias.get(
        texto,
        texto
    )


def normalizar_si_no(valor) -> str:
    texto = str(valor).strip()

    equivalencias = {
        "Si": "Sí",
        "si": "Sí",
        "SI": "Sí",
        "Sí": "Sí",
        "No": "No",
        "no": "No"
    }

    return equivalencias.get(
        texto,
        texto
    )


def normalizar_tipo_conexion(valor) -> str:
    texto = normalizar_texto(valor)

    equivalencias = {
        "Wifi": "Wi-Fi",
        "Wi Fi": "Wi-Fi",
        "Wi-Fi": "Wi-Fi",
        "Rauter": "Router",
        "Router": "Router",
        "Adsl": "ADSL",
        "Fibra Óptica": "Fibra óptica",
        "Datos Móviles": "Datos móviles",
        "Satelital": "Satelital",
        "Otro": "Otro"
    }

    return equivalencias.get(
        texto,
        texto
    )


def preparar_cambios_participantes(
    df_participantes: pd.DataFrame
) -> pd.DataFrame:

    cambios = []

    for _, fila in df_participantes.iterrows():

        nombre_original = fila.get("nombre_completo")
        ciudad_original = fila.get("ciudad")
        genero_original = fila.get("genero")
        nivel_original = fila.get("nivel_educativo")

        nombre_limpio = normalizar_texto(nombre_original)
        ciudad_limpia = normalizar_texto(ciudad_original)
        genero_limpio = normalizar_genero(genero_original)
        nivel_limpio = normalizar_nivel_educativo(nivel_original)

        datos_actualizados = {}

        if nombre_limpio and nombre_limpio != nombre_original:
            datos_actualizados["nombre_completo"] = nombre_limpio

        if ciudad_limpia and ciudad_limpia != ciudad_original:
            datos_actualizados["ciudad"] = ciudad_limpia

        if genero_limpio and genero_limpio != genero_original:
            datos_actualizados["genero"] = genero_limpio

        if nivel_limpio and nivel_limpio != nivel_original:
            datos_actualizados["nivel_educativo"] = nivel_limpio

        if datos_actualizados:
            cambios.append({
                "id_participante": fila["id_participante"],
                "Nombre actual": nombre_original,
                "Nombre limpio": nombre_limpio,
                "Ciudad actual": ciudad_original,
                "Ciudad limpia": ciudad_limpia,
                "Género actual": genero_original,
                "Género limpio": genero_limpio,
                "Nivel actual": nivel_original,
                "Nivel limpio": nivel_limpio,
                "_datos_actualizados": datos_actualizados
            })

    return pd.DataFrame(
        cambios
    )


def preparar_cambios_encuestas(
    df_respuestas: pd.DataFrame
) -> pd.DataFrame:

    cambios = []

    for _, fila in df_respuestas.iterrows():

        datos_actualizados = {}

        usa_nube_original = fila.get("usa_nube")
        reutiliza_original = fila.get("reutiliza_contrasenas")
        conexion_original = fila.get("tipo_conexion")
        plataforma_original = fila.get("plataforma_nube")
        contenido_original = fila.get("contenido_nube")

        usa_nube_limpio = normalizar_si_no(
            usa_nube_original
        )

        reutiliza_limpio = normalizar_si_no(
            reutiliza_original
        )

        conexion_limpia = normalizar_tipo_conexion(
            conexion_original
        )

        if (
            usa_nube_limpio
            and usa_nube_limpio != usa_nube_original
        ):
            datos_actualizados["usa_nube"] = usa_nube_limpio

        if (
            reutiliza_limpio
            and reutiliza_limpio != reutiliza_original
        ):
            datos_actualizados["reutiliza_contrasenas"] = reutiliza_limpio

        if (
            conexion_limpia
            and conexion_limpia != conexion_original
        ):
            datos_actualizados["tipo_conexion"] = conexion_limpia

        if (
            usa_nube_limpio == "No"
            and (
                not plataforma_original
                or str(plataforma_original).strip() == ""
            )
        ):
            datos_actualizados["plataforma_nube"] = "No aplica"

        if (
            usa_nube_limpio == "No"
            and (
                not contenido_original
                or str(contenido_original).strip() == ""
            )
        ):
            datos_actualizados["contenido_nube"] = "No aplica"

        if datos_actualizados:
            cambios.append({
                "id_respuesta": fila["id_respuesta"],
                "Usa nube actual": usa_nube_original,
                "Usa nube limpio": datos_actualizados.get(
                    "usa_nube",
                    usa_nube_original
                ),
                "Reutiliza actual": reutiliza_original,
                "Reutiliza limpio": datos_actualizados.get(
                    "reutiliza_contrasenas",
                    reutiliza_original
                ),
                "Conexión actual": conexion_original,
                "Conexión limpia": datos_actualizados.get(
                    "tipo_conexion",
                    conexion_original
                ),
                "Plataforma actual": plataforma_original,
                "Plataforma limpia": datos_actualizados.get(
                    "plataforma_nube",
                    plataforma_original
                ),
                "Contenido actual": contenido_original,
                "Contenido limpio": datos_actualizados.get(
                    "contenido_nube",
                    contenido_original
                ),
                "_datos_actualizados": datos_actualizados
            })

    return pd.DataFrame(
        cambios
    )


def aplicar_cambios_participantes(
    df_cambios: pd.DataFrame
) -> int:

    total_actualizados = 0

    for _, fila in df_cambios.iterrows():

        datos_actualizados = fila["_datos_actualizados"]

        if datos_actualizados:
            (
                supabase
                .table("participantes")
                .update(datos_actualizados)
                .eq(
                    "id_participante",
                    fila["id_participante"]
                )
                .execute()
            )

            total_actualizados += 1

    return total_actualizados


def aplicar_cambios_encuestas(
    df_cambios: pd.DataFrame
) -> int:

    total_actualizados = 0

    for _, fila in df_cambios.iterrows():

        datos_actualizados = fila["_datos_actualizados"]

        if datos_actualizados:
            (
                supabase
                .table(
                    "respuestas_encuesta_ciberseguridad"
                )
                .update(datos_actualizados)
                .eq(
                    "id_respuesta",
                    fila["id_respuesta"]
                )
                .execute()
            )

            total_actualizados += 1

    return total_actualizados


# =========================
# CARGAR DATOS
# =========================

try:
    participantes = consultar_tabla(
        "participantes",
        (
            "id_participante, id_usuario, nombre_completo, "
            "edad, genero, ciudad, nivel_educativo, fecha_registro"
        )
    )

    perfiles = consultar_tabla(
        "perfiles",
        "id, rol"
    )

    respuestas_ciberseguridad = consultar_tabla(
        "respuestas_encuesta_ciberseguridad",
        (
            "id_respuesta, id_usuario, fecha_respuesta, usa_nube, "
            "plataforma_nube, contenido_nube, nivel_conocimiento, "
            "manejo_ciberseguridad, frecuencia_info_seguridad, "
            "reconoce_phishing, identifica_herramientas_seguridad, "
            "estado_antivirus, tipo_conexion, estabilidad_conexion, "
            "frecuencia_fallas_internet, cambio_contrasenas_anual, "
            "reutiliza_contrasenas, importancia_actualizar_contrasenas, "
            "puntaje_riesgo, clasificacion_riesgo, observacion"
        )
    )

except Exception as error:
    st.error("No se pudieron cargar los datos.")
    st.write(error)
    st.stop()


# =========================
# PREPARAR DATAFRAMES
# =========================

df_participantes = pd.DataFrame(
    participantes
)

df_perfiles = pd.DataFrame(
    perfiles
)

df_respuestas = pd.DataFrame(
    respuestas_ciberseguridad
)

if not df_participantes.empty and not df_perfiles.empty:

    df_participantes = df_participantes.merge(
        df_perfiles,
        left_on="id_usuario",
        right_on="id",
        how="left"
    )

    df_participantes = df_participantes[
        df_participantes["rol"] == "usuario"
    ].copy()


if not df_respuestas.empty:
    df_respuestas["fecha_respuesta"] = pd.to_datetime(
        df_respuestas["fecha_respuesta"],
        errors="coerce"
    )

    df_respuestas["puntaje_riesgo"] = pd.to_numeric(
        df_respuestas["puntaje_riesgo"],
        errors="coerce"
    )


# =========================
# ANÁLISIS DE CALIDAD
# =========================

df_cambios_participantes = (
    preparar_cambios_participantes(
        df_participantes
    )
    if not df_participantes.empty
    else pd.DataFrame()
)

df_cambios_encuestas = (
    preparar_cambios_encuestas(
        df_respuestas
    )
    if not df_respuestas.empty
    else pd.DataFrame()
)

duplicados = pd.DataFrame()

if not df_participantes.empty:
    duplicados = df_participantes[
        df_participantes.duplicated(
            subset=[
                "nombre_completo",
                "edad",
                "ciudad"
            ],
            keep=False
        )
    ].copy()


encuestas_incompletas = pd.DataFrame()

if not df_respuestas.empty:

    columnas_obligatorias = [
        "id_usuario",
        "usa_nube",
        "nivel_conocimiento",
        "manejo_ciberseguridad",
        "reconoce_phishing",
        "estado_antivirus",
        "tipo_conexion",
        "reutiliza_contrasenas",
        "puntaje_riesgo",
        "clasificacion_riesgo"
    ]

    columnas_existentes = [
        columna
        for columna in columnas_obligatorias
        if columna in df_respuestas.columns
    ]

    encuestas_incompletas = df_respuestas[
        df_respuestas[columnas_existentes]
        .isna()
        .any(axis=1)
    ].copy()


usuarios_sin_encuesta = pd.DataFrame()

if not df_participantes.empty:

    usuarios_con_encuesta = (
        df_respuestas["id_usuario"]
        .dropna()
        .unique()
        .tolist()
        if not df_respuestas.empty
        else []
    )

    usuarios_sin_encuesta = df_participantes[
        ~df_participantes["id_usuario"]
        .isin(usuarios_con_encuesta)
    ].copy()


# =========================
# ENCABEZADO
# =========================

st.markdown(
    """
<div class="page-heading">
<h1>Limpieza y calidad de datos</h1>
<p>
Revisa la calidad de la información registrada, detecta posibles
errores y aplica normalizaciones seguras sin eliminar datos.
</p>
</div>
""",
    unsafe_allow_html=True
)


# =========================
# MÉTRICAS
# =========================

total_participantes = len(
    df_participantes
)

total_encuestas = len(
    df_respuestas
)

total_cambios_participantes = len(
    df_cambios_participantes
)

total_cambios_encuestas = len(
    df_cambios_encuestas
)

total_duplicados = len(
    duplicados
)

total_incompletas = len(
    encuestas_incompletas
)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Participantes",
        total_participantes
    )

with col2:
    st.metric(
        "Encuestas",
        total_encuestas
    )

with col3:
    st.metric(
        "Correcciones",
        total_cambios_participantes + total_cambios_encuestas
    )

with col4:
    st.metric(
        "Duplicados",
        total_duplicados
    )

with col5:
    st.metric(
        "Incompletas",
        total_incompletas
    )


# =========================
# PESTAÑAS
# =========================

tab_resumen, tab_participantes, tab_encuestas, tab_duplicados, tab_sin_encuesta = st.tabs(
    [
        "📊 Resumen",
        "👥 Limpieza participantes",
        "📝 Limpieza encuestas",
        "🔎 Duplicados",
        "⚠️ Usuarios sin encuesta"
    ]
)


# =========================
# TAB RESUMEN
# =========================

with tab_resumen:

    st.markdown("### Calidad general de datos")

    st.write(
        "Este módulo analiza los datos registrados en CyberLey. "
        "La limpieza automática aplica normalizaciones seguras, "
        "como corrección de espacios, formato de texto y valores "
        "como 'Wifi' → 'Wi-Fi' o 'Rauter' → 'Router'."
    )

    resumen_calidad = pd.DataFrame({
        "Indicador": [
            "Participantes registrados",
            "Encuestas de ciberseguridad",
            "Participantes con correcciones sugeridas",
            "Encuestas con correcciones sugeridas",
            "Posibles duplicados",
            "Encuestas incompletas",
            "Usuarios sin encuesta"
        ],
        "Cantidad": [
            total_participantes,
            total_encuestas,
            total_cambios_participantes,
            total_cambios_encuestas,
            total_duplicados,
            total_incompletas,
            len(usuarios_sin_encuesta)
        ]
    })

    st.dataframe(
        resumen_calidad,
        use_container_width=True,
        hide_index=True
    )

    if not df_respuestas.empty:
        st.markdown("### Valores faltantes por columna de encuesta")

        nulos = (
            df_respuestas
            .isna()
            .sum()
            .reset_index()
        )

        nulos.columns = [
            "Columna",
            "Valores faltantes"
        ]

        st.dataframe(
            nulos,
            use_container_width=True,
            hide_index=True
        )


# =========================
# TAB PARTICIPANTES
# =========================

with tab_participantes:

    st.markdown("### Correcciones seguras en participantes")

    if df_cambios_participantes.empty:
        st.success(
            "✅ Los datos de participantes ya tienen formato uniforme."
        )

    else:
        columnas_vista = [
            "Nombre actual",
            "Nombre limpio",
            "Ciudad actual",
            "Ciudad limpia",
            "Género actual",
            "Género limpio",
            "Nivel actual",
            "Nivel limpio"
        ]

        st.dataframe(
            df_cambios_participantes[columnas_vista],
            use_container_width=True,
            hide_index=True
        )

        st.warning(
            "Revisa la vista previa antes de aplicar los cambios."
        )

        confirmar = st.checkbox(
            "Confirmo que revisé las correcciones de participantes."
        )

        if st.button(
            "Aplicar limpieza de participantes",
            use_container_width=True,
            disabled=not confirmar
        ):
            try:
                total_actualizados = aplicar_cambios_participantes(
                    df_cambios_participantes
                )

                guardar_notificacion(
                    f"Se actualizaron {total_actualizados} participantes correctamente.",
                    "✅"
                )

                st.rerun()

            except Exception as error:
                st.error(
                    "No se pudieron aplicar las correcciones."
                )
                st.write(error)


# =========================
# TAB ENCUESTAS
# =========================

with tab_encuestas:

    st.markdown("### Correcciones seguras en encuestas")

    if df_cambios_encuestas.empty:
        st.success(
            "✅ Las respuestas de encuestas ya tienen formato uniforme."
        )

    else:
        columnas_vista = [
            "Usa nube actual",
            "Usa nube limpio",
            "Reutiliza actual",
            "Reutiliza limpio",
            "Conexión actual",
            "Conexión limpia",
            "Plataforma actual",
            "Plataforma limpia",
            "Contenido actual",
            "Contenido limpio"
        ]

        st.dataframe(
            df_cambios_encuestas[columnas_vista],
            use_container_width=True,
            hide_index=True
        )

        st.warning(
            "Estas correcciones no recalculan el puntaje, solo normalizan valores de texto."
        )

        confirmar_encuestas = st.checkbox(
            "Confirmo que revisé las correcciones de encuestas."
        )

        if st.button(
            "Aplicar limpieza de encuestas",
            use_container_width=True,
            disabled=not confirmar_encuestas
        ):
            try:
                total_actualizados = aplicar_cambios_encuestas(
                    df_cambios_encuestas
                )

                guardar_notificacion(
                    f"Se actualizaron {total_actualizados} respuestas correctamente.",
                    "✅"
                )

                st.rerun()

            except Exception as error:
                st.error(
                    "No se pudieron aplicar las correcciones de encuestas."
                )
                st.write(error)

    st.markdown("### Encuestas incompletas")

    if encuestas_incompletas.empty:
        st.success(
            "✅ Todas las encuestas tienen los datos principales completos."
        )

    else:
        st.warning(
            "Estas encuestas tienen campos principales vacíos."
        )

        columnas_incompletas = [
            "fecha_respuesta",
            "id_usuario",
            "usa_nube",
            "nivel_conocimiento",
            "reconoce_phishing",
            "estado_antivirus",
            "puntaje_riesgo",
            "clasificacion_riesgo"
        ]

        columnas_existentes = [
            columna
            for columna in columnas_incompletas
            if columna in encuestas_incompletas.columns
        ]

        st.dataframe(
            encuestas_incompletas[columnas_existentes],
            use_container_width=True,
            hide_index=True
        )


# =========================
# TAB DUPLICADOS
# =========================

with tab_duplicados:

    st.markdown("### Posibles registros duplicados")

    if duplicados.empty:
        st.success(
            "✅ No se detectaron posibles participantes duplicados."
        )

    else:
        st.warning(
            "Estos registros podrían corresponder a la misma persona. "
            "No se eliminarán automáticamente."
        )

        columnas_duplicados = [
            "nombre_completo",
            "edad",
            "genero",
            "ciudad",
            "nivel_educativo",
            "fecha_registro"
        ]

        columnas_existentes = [
            columna
            for columna in columnas_duplicados
            if columna in duplicados.columns
        ]

        st.dataframe(
            duplicados[columnas_existentes],
            use_container_width=True,
            hide_index=True
        )


# =========================
# TAB USUARIOS SIN ENCUESTA
# =========================

with tab_sin_encuesta:

    st.markdown("### Usuarios registrados sin encuesta")

    if usuarios_sin_encuesta.empty:
        st.success(
            "✅ Todos los usuarios registrados ya completaron al menos una encuesta."
        )

    else:
        st.warning(
            "Estos usuarios están registrados, pero aún no han completado la encuesta nueva."
        )

        columnas_sin_encuesta = [
            "nombre_completo",
            "edad",
            "genero",
            "ciudad",
            "nivel_educativo",
            "fecha_registro"
        ]

        columnas_existentes = [
            columna
            for columna in columnas_sin_encuesta
            if columna in usuarios_sin_encuesta.columns
        ]

        st.dataframe(
            usuarios_sin_encuesta[columnas_existentes],
            use_container_width=True,
            hide_index=True
        )