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

def restaurar_sesion():
    """
    Restaura la sesión del administrador.
    Realiza un segundo intento si Supabase tarda en responder.
    """

    access_token = st.session_state.get("access_token")
    refresh_token = st.session_state.get("refresh_token")

    if not access_token or not refresh_token:
        return

    for intento in range(2):
        try:
            supabase.auth.set_session(
                access_token,
                refresh_token
            )

            return

        except (TimeoutException, ConnectError):
            if intento == 0:
                time.sleep(1)

    st.error(
        "No se pudo conectar con Supabase en este momento. "
        "Revisa tu conexión e intenta nuevamente."
    )

    if st.button("Reintentar conexión"):
        st.rerun()

    st.stop()


restaurar_sesion()


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

    with open(ruta_css, "r", encoding="utf-8") as archivo:
        st.markdown(
            f"<style>{archivo.read()}</style>",
            unsafe_allow_html=True
        )


cargar_css()


# =========================
# FUNCIONES GENERALES
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
    """
    Guarda una notificación temporal para mostrarla
    después de recargar la pantalla.
    """

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
            icon=icono
        )


mostrar_toast_pendiente()


# =========================
# CONSULTAR DATOS
# =========================

try:
    perfiles = consultar_tabla(
        "perfiles",
        (
            "id, nombre_completo, rol, foto_url, "
            "fecha_creacion"
        )
    )

    guias = consultar_tabla(
        "guias_ciberseguridad",
        (
            "id_guia, titulo, categoria, descripcion, "
            "contenido, nivel_recomendado, fecha_creacion"
        )
    )

    notificaciones = consultar_tabla(
        "notificaciones",
        (
            "id_notificacion, id_usuario, titulo, "
            "mensaje, leida, fecha_creacion"
        )
    )

except Exception as error:
    st.error(
        "No se pudieron cargar los datos administrativos."
    )
    st.write(error)
    st.stop()


# =========================
# PREPARAR DATAFRAMES
# =========================

df_perfiles = pd.DataFrame(perfiles)
df_guias = pd.DataFrame(guias)
df_notificaciones = pd.DataFrame(notificaciones)


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
            "💾 Respaldo y recuperación",
            "📄 Reportes",
            "⚙️ Administración"
        ],
        index=7,
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
<h1>Administración</h1>
<p>
Gestiona usuarios, roles, guías educativas
y notificaciones internas del sistema.
</p>
</div>
""",
    unsafe_allow_html=True
)


# =========================
# MÉTRICAS GENERALES
# =========================

total_perfiles = len(df_perfiles)

total_usuarios = (
    len(
        df_perfiles[
            df_perfiles["rol"] == "usuario"
        ]
    )
    if not df_perfiles.empty
    else 0
)

total_admins = (
    len(
        df_perfiles[
            df_perfiles["rol"] == "admin"
        ]
    )
    if not df_perfiles.empty
    else 0
)

total_guias = len(df_guias)
total_notificaciones = len(df_notificaciones)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Perfiles",
        total_perfiles
    )

with col2:
    st.metric(
        "Usuarios",
        total_usuarios
    )

with col3:
    st.metric(
        "Administradores",
        total_admins
    )

with col4:
    st.metric(
        "Guías",
        total_guias
    )

with col5:
    st.metric(
        "Notificaciones",
        total_notificaciones
    )


st.write("")


# =========================
# PESTAÑAS
# =========================

tab_usuarios, tab_guias, tab_notificaciones = st.tabs(
    [
        "👥 Usuarios y roles",
        "📚 Guías de ciberseguridad",
        "🔔 Notificaciones"
    ]
)


# =========================
# TAB: USUARIOS Y ROLES
# =========================

with tab_usuarios:

    st.markdown("### Usuarios registrados")

    st.write(
        "Consulta los perfiles existentes y cambia el rol "
        "únicamente cuando sea necesario."
    )

    if df_perfiles.empty:
        st.info("Todavía no existen perfiles registrados.")

    else:
        tabla_perfiles = df_perfiles[
            [
                "nombre_completo",
                "rol",
                "fecha_creacion"
            ]
        ].copy()

        tabla_perfiles["rol"] = (
            tabla_perfiles["rol"]
            .str.title()
        )

        tabla_perfiles["fecha_creacion"] = (
            pd.to_datetime(
                tabla_perfiles["fecha_creacion"],
                errors="coerce"
            )
            .dt.strftime(
                "%d/%m/%Y %H:%M"
            )
        )

        st.dataframe(
            tabla_perfiles,
            use_container_width=True,
            hide_index=True,
            column_config={
                "nombre_completo": "Nombre completo",
                "rol": "Rol",
                "fecha_creacion": "Fecha de creación"
            }
        )

        st.markdown("### Cambiar rol")

        opciones_perfiles = {
            (
                f"{fila['nombre_completo']} — "
                f"{fila['rol'].title()}"
            ): fila["id"]

            for _, fila in df_perfiles.iterrows()
        }

        perfil_seleccionado_texto = st.selectbox(
            "Selecciona un perfil",
            opciones_perfiles.keys()
        )

        perfil_id = opciones_perfiles[
            perfil_seleccionado_texto
        ]

        perfil_actual = df_perfiles[
            df_perfiles["id"] == perfil_id
        ].iloc[0]

        nuevo_rol = st.selectbox(
            "Nuevo rol",
            [
                "usuario",
                "admin"
            ],
            index=(
                1
                if perfil_actual["rol"] == "admin"
                else 0
            )
        )

        if perfil_id == st.session_state.get("usuario_id"):
            st.info(
                "Tu propio rol no puede modificarse desde esta pantalla "
                "para evitar bloquear el acceso administrativo."
            )

        if st.button(
            "Actualizar rol",
            use_container_width=True,
            disabled=(
                perfil_id
                == st.session_state.get("usuario_id")
            )
        ):
            try:
                (
                    supabase
                    .table("perfiles")
                    .update({
                        "rol": nuevo_rol
                    })
                    .eq(
                        "id",
                        perfil_id
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
# TAB: GUÍAS
# =========================

with tab_guias:

    st.markdown("### Crear guía de ciberseguridad")

    with st.form(
        "formulario_nueva_guia",
        clear_on_submit=True
    ):

        titulo_guia = st.text_input(
            "Título",
            placeholder="Ejemplo: Protege tus contraseñas"
        )

        categoria_guia = st.text_input(
            "Categoría",
            placeholder="Ejemplo: Contraseñas"
        )

        descripcion_guia = st.text_area(
            "Descripción breve",
            placeholder=(
                "Explica de forma sencilla el propósito de la guía."
            )
        )

        contenido_guia = st.text_area(
            "Contenido",
            placeholder=(
                "Escribe recomendaciones claras para los usuarios."
            ),
            height=180
        )

        nivel_guia = st.selectbox(
            "Nivel recomendado",
            [
                "general",
                "bajo",
                "medio",
                "alto"
            ]
        )

        crear_guia = st.form_submit_button(
            "Guardar guía",
            use_container_width=True
        )

        if crear_guia:

            if (
                titulo_guia.strip() == ""
                or categoria_guia.strip() == ""
            ):
                st.warning(
                    "Completa el título y la categoría."
                )

            else:
                try:
                    (
                        supabase
                        .table("guias_ciberseguridad")
                        .insert({
                            "titulo": titulo_guia.strip(),
                            "categoria": categoria_guia.strip(),
                            "descripcion": (
                                descripcion_guia.strip()
                            ),
                            "contenido": (
                                contenido_guia.strip()
                            ),
                            "nivel_recomendado": nivel_guia
                        })
                        .execute()
                    )

                    guardar_toast(
                        "Guía creada correctamente.",
                        "✅"
                    )

                    st.rerun()

                except Exception as error:
                    st.error(
                        "No se pudo crear la guía."
                    )

                    st.write(error)

    st.divider()

    st.markdown("### Guías registradas")

    if df_guias.empty:
        st.info(
            "Todavía no existen guías de ciberseguridad."
        )

    else:
        tabla_guias = df_guias[
            [
                "titulo",
                "categoria",
                "nivel_recomendado",
                "fecha_creacion"
            ]
        ].copy()

        tabla_guias["nivel_recomendado"] = (
            tabla_guias["nivel_recomendado"]
            .fillna("general")
            .str.title()
        )

        tabla_guias["fecha_creacion"] = (
            pd.to_datetime(
                tabla_guias["fecha_creacion"],
                errors="coerce"
            )
            .dt.strftime(
                "%d/%m/%Y %H:%M"
            )
        )

        st.dataframe(
            tabla_guias,
            use_container_width=True,
            hide_index=True,
            column_config={
                "titulo": "Título",
                "categoria": "Categoría",
                "nivel_recomendado": "Nivel recomendado",
                "fecha_creacion": "Fecha de creación"
            }
        )

        st.markdown("### Editar guía")

        opciones_guias = {
            fila["titulo"]: fila["id_guia"]
            for _, fila in df_guias.iterrows()
        }

        guia_seleccionada_texto = st.selectbox(
            "Selecciona una guía",
            opciones_guias.keys()
        )

        guia_id = opciones_guias[
            guia_seleccionada_texto
        ]

        guia_actual = df_guias[
            df_guias["id_guia"] == guia_id
        ].iloc[0]

        nuevo_titulo = st.text_input(
            "Editar título",
            value=(
                guia_actual.get("titulo")
                or ""
            )
        )

        nueva_categoria = st.text_input(
            "Editar categoría",
            value=(
                guia_actual.get("categoria")
                or ""
            )
        )

        nueva_descripcion = st.text_area(
            "Editar descripción",
            value=(
                guia_actual.get("descripcion")
                or ""
            )
        )

        nuevo_contenido = st.text_area(
            "Editar contenido",
            value=(
                guia_actual.get("contenido")
                or ""
            ),
            height=180
        )

        niveles_disponibles = [
            "general",
            "bajo",
            "medio",
            "alto"
        ]

        nivel_actual = (
            guia_actual.get("nivel_recomendado")
            or "general"
        )

        nuevo_nivel = st.selectbox(
            "Editar nivel recomendado",
            niveles_disponibles,
            index=niveles_disponibles.index(
                nivel_actual
            )
        )

        if st.button(
            "Actualizar guía",
            use_container_width=True
        ):
            try:
                (
                    supabase
                    .table("guias_ciberseguridad")
                    .update({
                        "titulo": nuevo_titulo.strip(),
                        "categoria": nueva_categoria.strip(),
                        "descripcion": nueva_descripcion.strip(),
                        "contenido": nuevo_contenido.strip(),
                        "nivel_recomendado": nuevo_nivel
                    })
                    .eq(
                        "id_guia",
                        guia_id
                    )
                    .execute()
                )

                guardar_toast(
                    "Guía actualizada correctamente.",
                    "✅"
                )

                st.rerun()

            except Exception as error:
                st.error(
                    "No se pudo actualizar la guía."
                )

                st.write(error)


# =========================
# TAB: NOTIFICACIONES
# =========================

with tab_notificaciones:

    st.markdown("### Enviar notificación")

    if df_perfiles.empty:
        st.info(
            "No existen usuarios para enviar notificaciones."
        )

    else:
        opciones_destinatarios = {
            (
                f"{fila['nombre_completo']} — "
                f"{fila['rol'].title()}"
            ): fila["id"]

            for _, fila in df_perfiles.iterrows()
        }

        destinatario_texto = st.selectbox(
            "Destinatario",
            opciones_destinatarios.keys()
        )

        destinatario_id = opciones_destinatarios[
            destinatario_texto
        ]

        titulo_notificacion = st.text_input(
            "Título de la notificación",
            placeholder="Ejemplo: Nueva guía disponible"
        )

        mensaje_notificacion = st.text_area(
            "Mensaje",
            placeholder=(
                "Escribe un mensaje breve para el usuario."
            )
        )

        if st.button(
            "Enviar notificación",
            use_container_width=True
        ):

            if (
                titulo_notificacion.strip() == ""
                or mensaje_notificacion.strip() == ""
            ):
                st.warning(
                    "Completa el título y el mensaje."
                )

            else:
                try:
                    (
                        supabase
                        .table("notificaciones")
                        .insert({
                            "id_usuario": destinatario_id,
                            "titulo": (
                                titulo_notificacion.strip()
                            ),
                            "mensaje": (
                                mensaje_notificacion.strip()
                            ),
                            "leida": False
                        })
                        .execute()
                    )

                    guardar_toast(
                        "Notificación enviada correctamente.",
                        "✅"
                    )

                    st.rerun()

                except Exception as error:
                    st.error(
                        "No se pudo enviar la notificación."
                    )

                    st.write(error)

    st.divider()

    st.markdown("### Notificaciones recientes")

    if df_notificaciones.empty:
        st.info(
            "Todavía no existen notificaciones."
        )

    else:
        nombres_perfiles = {
            fila["id"]: fila["nombre_completo"]
            for _, fila in df_perfiles.iterrows()
        }

        tabla_notificaciones = df_notificaciones.copy()

        tabla_notificaciones["destinatario"] = (
            tabla_notificaciones["id_usuario"]
            .map(nombres_perfiles)
            .fillna("Usuario no disponible")
        )

        tabla_notificaciones["estado"] = (
            tabla_notificaciones["leida"]
            .map({
                True: "Leída",
                False: "Pendiente"
            })
        )

        tabla_notificaciones["fecha_creacion"] = (
            pd.to_datetime(
                tabla_notificaciones["fecha_creacion"],
                errors="coerce"
            )
            .dt.strftime(
                "%d/%m/%Y %H:%M"
            )
        )

        tabla_notificaciones = (
            tabla_notificaciones
            .sort_values(
                "fecha_creacion",
                ascending=False
            )
        )

        st.dataframe(
            tabla_notificaciones[
                [
                    "destinatario",
                    "titulo",
                    "mensaje",
                    "estado",
                    "fecha_creacion"
                ]
            ],
            use_container_width=True,
            hide_index=True,
            column_config={
                "destinatario": "Destinatario",
                "titulo": "Título",
                "mensaje": "Mensaje",
                "estado": "Estado",
                "fecha_creacion": "Fecha"
            }
        )