import re
import unicodedata
from difflib import SequenceMatcher

from app.services.dynamic_surveys_service import available_surveys
from app.services.guides_service import list_guides
from app.services.risk_service import user_risk_responses


def _normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.casefold())
    value = "".join(character for character in value if not unicodedata.combining(character))
    return " ".join(re.sub(r"[^a-z0-9\s]", " ", value).split())


def _matches(text: str, *expressions: str) -> bool:
    if any(expression in text for expression in expressions):
        return True
    words = text.split()
    for expression in expressions:
        expected_words = expression.split()
        if len(expected_words) > 1 and all(
            any(SequenceMatcher(None, expected, received).ratio() >= 0.82 for received in words)
            for expected in expected_words
        ):
            return True
    candidates = [item for item in expressions if " " not in item and len(item) >= 4]
    return any(SequenceMatcher(None, word, candidate).ratio() >= 0.84 for word in words for candidate in candidates)


def _reply(intent: str, answer: str, suggestions: list[str], action: dict | None = None) -> dict:
    return {"intent": intent, "respuesta": answer, "sugerencias": suggestions[:3], "accion": action}


def _previous_user_message(history: list[dict]) -> str:
    for message in reversed(history):
        if message.get("rol") == "usuario":
            return _normalize(str(message.get("texto", "")))
    return ""


def _recent_user_context(history: list[dict]) -> str:
    messages = [
        _normalize(str(message.get("texto", "")))
        for message in history
        if message.get("rol") == "usuario"
    ]
    return " ".join(messages[-3:])


def _risk_areas(result: dict) -> list[str]:
    areas = []
    if result.get("reutiliza_contrasenas") in {"Sí", "A veces", "Si"}:
        areas.append("usar una contraseña diferente en cada cuenta")
    if result.get("reconoce_phishing") in {"No", "A veces"}:
        areas.append("reconocer mensajes y enlaces sospechosos")
    if result.get("estado_antivirus") in {"No tengo antivirus", "Tengo antivirus, pero no está actualizado", "No sé"}:
        areas.append("mantener protegido y actualizado tu dispositivo")
    if result.get("cambio_contrasenas_anual") == "Nunca":
        areas.append("cambiar las claves que puedan estar expuestas")
    return areas[:3]


def answer_from_knowledge(token: str, user_id: str, question: str, history: list[dict] | None = None) -> dict:
    text = _normalize(question)
    history = history or []
    previous = _previous_user_message(history)
    recent_context = _recent_user_context(history)
    continuation = text in {"si", "sip", "aja", "tambien"} or _matches(text, "lo hice", "ya lo hice", "puse mi contrasena", "di mis datos", "solo lo abri")
    context = f"{recent_context} {text}" if recent_context and continuation else text

    # Entradas generales usadas por los botones del propio chat.
    if _matches(text, "tuve un problema de seguridad", "creo que tuve un problema", "necesito ayuda de seguridad", "algo malo paso"):
        return _reply("tipo_problema", "Estoy contigo. Para ayudarte bien, dime qué ocurrió.", ["Entraron a mi cuenta", "Abrí un enlace extraño", "Perdí mi celular"])
    if _matches(text, "quiero cuidar mis cuentas", "proteger mi cuenta", "proteger mis cuentas", "como cuido mis cuentas", "como evito que me hackeen"):
        return _reply("proteger_cuentas", "Buena decisión. Empieza por tres cosas: usa una contraseña diferente en cada cuenta, activa la verificación en dos pasos y revisa dónde tienes sesiones abiertas. Tu correo es la cuenta más importante para comenzar.", ["Crear una contraseña segura", "Activar verificación en dos pasos", "Revisar sesiones abiertas"])
    if _matches(text, "necesito usar cyberley", "usar cyberley", "explicame cyberley", "cuentame de cyberley"):
        return _reply("usar_cyberley", "CyberLey te ayuda a conocer tus hábitos de seguridad. Primero haces una evaluación, luego revisas tu resultado y finalmente usas las guías para mejorar poco a poco.", ["Ver mis evaluaciones", "Ver mis resultados", "Ver las guías"], {"label": "Ir al inicio", "path": "/usuario"})
    if _matches(text, "aprender seguridad", "sigamos aprendiendo", "dame un truco de seguridad", "dame un consejo facil", "dame un consejo sencillo", "otro consejo divertido"):
        return _reply("consejo_seguridad", "Aquí tienes uno sencillo: activa la verificación en dos pasos primero en tu correo. El correo suele servir para recuperar las demás cuentas, así que protegerlo ayuda a cuidar todo lo demás.", ["¿Qué es la verificación en dos pasos?", "Quiero cuidar mis cuentas", "Ver las guías"])

    # Límites defensivos: Ciby protege, nunca enseña a atacar a otras personas.
    unsafe_phrases = ("como hackeo", "como puedo hackear", "hackear una cuenta", "robar una contrasena", "sacar la contrasena", "crear phishing", "hacer un virus", "espiar a alguien", "entrar sin permiso", "evadir autenticacion")
    if any(phrase in text for phrase in unsafe_phrases):
        return _reply("solicitud_no_segura", "No puedo ayudarte a entrar en una cuenta ajena, engañar o dañar a alguien. Si quieres recuperar tu propia cuenta o aprender a protegerla, sí puedo ayudarte.", ["Recuperar mi cuenta", "Proteger mi cuenta", "Aprender seguridad"])

    # No se repite ni se almacena en la respuesta ningún secreto escrito por el usuario.
    secret_pattern = r"\b(?:mi\s+(?:contrasena|clave|pin|cvv)\s+(?:es|:)|(?:contrasena|clave|pin|cvv)\s*:)\s*(?!segura\b|buena\b|fuerte\b|debil\b|mala\b|correcta\b|suficiente\b)\S+"
    if re.search(secret_pattern, text):
        return _reply("dato_sensible", "No compartas contraseñas, PIN ni códigos por el chat. Si escribiste un dato que usas actualmente, cámbialo desde la página o aplicación oficial. Yo no necesito conocerlo para ayudarte.", ["Cambiar mi contraseña", "Proteger mi cuenta", "Compartí un dato bancario"])

    if _matches(context, "puse mi contrasena", "meti mi clave", "comparti mi contrasena", "alguien sabe mi clave", "filtraron mi contrasena", "contrasena aparecio en filtracion", "clave comprometida"):
        return _reply("credencial_expuesta", "Haz esto primero: cambia esa contraseña desde la página o aplicación oficial. Después cierra las sesiones abiertas y activa la verificación en dos pasos. Si usabas la misma clave en otras cuentas, cámbiala también, empezando por tu correo.", ["¿Cómo cierro otras sesiones?", "¿Qué es la verificación en dos pasos?", "También di datos de mi tarjeta"])
    if _matches(context, "di datos bancarios", "datos de mi tarjeta", "numero de tarjeta", "comparti mi cvv", "comparti mi pin", "informacion bancaria"):
        return _reply("datos_financieros", "Comunícate cuanto antes con tu banco usando el número de su aplicación, tarjeta o página oficial. Pide que revisen y protejan la cuenta. No escribas aquí el número de tarjeta, PIN, código de seguridad ni claves bancarias.", ["¿Qué información guardo como prueba?", "También compartí una contraseña", "¿Cómo evito otro fraude?"])
    if _matches(text, "codigo que no pedi", "me llego un codigo", "me piden el codigo", "le paso el codigo", "llegan codigos", "codigo de instagram", "codigo de facebook"):
        return _reply("codigo_inesperado", "No compartas ese código. Puede ser que alguien esté intentando entrar a tu cuenta, aunque también podría ser un error. Abre directamente la aplicación, revisa dónde está iniciada tu cuenta y cambia la contraseña si ves algo que no reconoces.", ["¿Cómo reviso las sesiones?", "¿Debo cambiar mi contraseña?", "¿Qué es la verificación en dos pasos?"])

    if _matches(text, "revisar sesiones", "sesiones abiertas", "cerrar otras sesiones", "cerrar sesiones abiertas", "dispositivos conectados"):
        return _reply("sesiones", "Entra directamente a la configuración de seguridad de la cuenta y busca «Dónde iniciaste sesión», «Actividad de inicio» o «Dispositivos». Cierra lo que no reconozcas. Si ves algo extraño, cambia también la contraseña.", ["Veo un dispositivo extraño", "Cambiar mi contraseña", "Activar verificación en dos pasos"])

    previous_is_suspicious = _matches(recent_context, "link", "enlace", "correo raro", "mensaje raro", "sera real", "sera falso")
    if previous_is_suspicious and _matches(text, "por whatsapp", "whatsapp", "por sms", "mensaje de texto", "por correo", "instagram", "facebook"):
        return _reply("canal_sospechoso", "Gracias, eso ayuda. No respondas ni abras el enlace desde ese mensaje. Busca la cuenta o empresa directamente en su aplicación oficial y comprueba allí si realmente existe algún aviso. ¿El mensaje te pide iniciar sesión, pagar o compartir un código?", ["Pide iniciar sesión", "Pide dinero", "Pide un código"])
    if previous_is_suspicious and _matches(text, "iniciar sesion", "confirmar mi cuenta", "verificar mi cuenta"):
        return _reply("phishing_inicio_sesion", "Esa petición merece cuidado. No inicies sesión desde el enlace del mensaje. Abre tú mismo la aplicación o página oficial y revisa si aparece el mismo aviso. Si no aparece, repórtalo como mensaje sospechoso.", ["Ya puse mi contraseña", "¿Cómo lo reporto?", "Sólo abrí el enlace"])
    if previous_is_suspicious and _matches(text, "solo lo abri", "solo hice click", "no puse nada"):
        return _reply("enlace_abierto", "Si sólo abriste la página y no escribiste datos ni descargaste archivos, ciérrala y no vuelvas a entrar. Revisa que no se haya descargado nada. Si notas cambios extraños, cuéntame qué ves.", ["Se descargó un archivo", "Sí puse información", "No pasó nada más"])
    if previous_is_suspicious and _matches(text, "pide dinero", "pagar", "depositar", "transferir"):
        return _reply("solicitud_dinero", "No pagues todavía. Confirma la solicitud hablando con la persona o empresa por un número que tú ya conozcas. Si dicen ser un familiar, hazle una pregunta que sólo esa persona pueda responder.", ["Dice que es un familiar", "Ya envié dinero", "También envió un enlace"])
    if previous_is_suspicious and _matches(text, "pide codigo", "pide un codigo", "compartir codigo"):
        return _reply("solicitud_codigo", "No compartas el código. Las empresas no deberían pedírtelo por mensaje o llamada. Abre la aplicación oficial y revisa si hubo un intento de entrar a tu cuenta.", ["Ya compartí el código", "Revisar sesiones abiertas", "Cambiar mi contraseña"])
    if previous_is_suspicious and _matches(text, "se descargo un archivo", "descargue un archivo", "se bajo algo"):
        return _reply("descarga_sospechosa", "No abras el archivo. Elimínalo de Descargas y también de la papelera. Después ejecuta el análisis de seguridad del dispositivo. Si ya lo abriste, desconecta internet y cuéntame qué cambios notaste.", ["Ya abrí el archivo", "Me salen cosas extrañas", "¿Necesito antivirus?"])
    if previous_is_suspicious and _matches(text, "no paso nada", "nada mas", "todo normal"):
        return _reply("sin_senales", "Eso es una buena señal, aunque no permite asegurar que todo esté perfecto. Si no escribiste datos ni descargaste archivos, basta con cerrar la página y mantener el dispositivo actualizado. Si notas algo extraño después, vuelve y lo revisamos.", ["¿Qué señales debo vigilar?", "¿Cómo protejo mi dispositivo?", "Entendido, gracias"])

    if _matches(text, "que evaluaciones tengo", "evaluaciones disponibles", "cuales evaluaciones", "tengo evaluaciones pendientes"):
        surveys = available_surveys(token, user_id)
        if not surveys:
            return _reply("evaluaciones_disponibles", "Ahora mismo no tienes evaluaciones publicadas. Cuando haya una disponible aparecerá en la sección Evaluación.", ["¿Para qué sirven las evaluaciones?", "Ver mis resultados"], {"label": "Ir a Evaluación", "path": "/usuario/encuesta"})
        pending = [survey for survey in surveys if not survey.get("respondida")]
        names = ", ".join(f'«{survey.get("titulo", "Evaluación")}»' for survey in pending[:3])
        if pending:
            answer = f"Tienes {len(pending)} evaluación{' pendiente' if len(pending) == 1 else 'es pendientes'}. Puedes comenzar con {names}."
        else:
            answer = "Ya respondiste todas las evaluaciones que están disponibles. Puedes revisar tus resultados cuando quieras."
        return _reply("evaluaciones_disponibles", answer, ["Ver mis resultados", "¿Cómo se calcula el puntaje?"], {"label": "Abrir evaluaciones", "path": "/usuario/encuesta"})
    if _matches(text, "que guias hay", "guias disponibles", "cuales guias", "recomiendame una guia"):
        guides = list_guides(token, user_id).get("items", [])
        if not guides:
            return _reply("guias_disponibles", "Ahora mismo no hay guías publicadas. No te recomendaré una que no exista; puedes volver a revisar esta sección más tarde.", ["Dame un consejo sencillo", "¿Qué hago primero?"], {"label": "Revisar Guías", "path": "/usuario/guias"})
        names = ", ".join(f'«{guide.get("titulo", "Guía")}»' for guide in guides[:3])
        return _reply("guias_disponibles", f"Encontré estas guías en CyberLey: {names}. Puedes abrirlas y elegir la que más te ayude.", ["¿Por cuál empiezo?", "¿Cómo puedo mejorar?"], {"label": "Abrir Guías", "path": "/usuario/guias"})

    if _matches(text, "mi contrasena es segura", "mi clave es buena", "contrasena fuerte", "como hago una contrasena buena"):
        return _reply("evaluar_contrasena", "No me envíes la contraseña. Puedes revisarla así: debe ser larga, distinta para cada cuenta y difícil de adivinar. Una frase de varias palabras suele ser más fácil de recordar. Evita nombres, fechas y datos personales.", ["Uso la misma clave para todo", "¿Qué es un gestor de contraseñas?", "¿Qué es la verificación en dos pasos?"])
    if _matches(text, "cada cuanto cambio", "cuando cambiar contrasena", "debo cambiar mi clave"):
        return _reply("cambio_contrasena", "No necesitas cambiarla cada mes si es larga, única y nadie más la conoce. Cámbiala de inmediato si se filtró, la compartiste, la reutilizaste o ves un inicio de sesión extraño.", ["Mi contraseña se filtró", "Uso la misma clave", "¿Cómo reviso mis sesiones?"])
    if _matches(text, "smishing"):
        return _reply("smishing", "En palabras sencillas, es un mensaje de texto falso que intenta hacerte abrir un enlace o entregar información. Trátalo como un correo sospechoso: no pulses el enlace y verifica la solicitud desde la aplicación oficial.", ["Me llegó un SMS raro", "¿Qué hago si ya lo abrí?", "¿Cómo reporto el mensaje?"])
    if _matches(text, "vishing", "llamada sospechosa", "llamada del banco", "me llamaron pidiendo codigo"):
        return _reply("vishing", "Es un engaño por llamada. Cuelga si te piden claves, códigos o datos de tarjeta. Después llama tú al número oficial de la empresa o banco. Que sepan tu nombre no demuestra que la llamada sea verdadera.", ["Compartí un código", "Compartí datos bancarios", "¿Cómo reconozco un fraude?"])
    if _matches(text, "subir mi ubicacion", "publicar mi ubicacion", "foto de mi boleto", "subir mi identificacion", "publicar identificacion", "que no debo publicar"):
        return _reply("publicacion_sensible", "Evita publicar tu ubicación en tiempo real, boletos con códigos, documentos de identidad, dirección, teléfono o datos bancarios. Aunque borres la publicación después, alguien podría haber guardado una copia.", ["¿Qué puedo publicar con seguridad?", "¿Cómo hago privado mi perfil?", "Ya publiqué un documento"])
    if _matches(text, "ya publique un documento", "publique mi identificacion", "publique mi boleto", "mostre mi direccion"):
        return _reply("dato_publicado", "Elimina la publicación y revisa quién pudo verla. Si mostraba un boleto, código o documento importante, comunícate con la organización que lo emitió para saber si deben reemplazarlo. Guarda una captura por si notas un uso indebido.", ["¿Qué datos no debo publicar?", "¿Cómo hago privado mi perfil?", "¿Cómo guardo pruebas?"])
    if _matches(text, "compartir archivo", "enlace publico", "carpeta publica", "quien puede ver mi archivo"):
        return _reply("compartir_archivos", "Comparte el archivo sólo con las personas necesarias. Si puedes, elige sus correos en lugar de usar un enlace público. Después revisa la lista de personas con acceso y quita a quien ya no lo necesite.", ["¿Es segura la nube?", "¿Cómo protejo documentos?", "¿Qué permisos debo revisar?"])

    if text in {"esto es seguro", "sera real", "que hago", "me pueden hackear", "esto esta bien", "ayuda"}:
        return _reply("pregunta_ambigua", "Puedo ayudarte a revisarlo. ¿Se trata de un enlace, un correo, un mensaje, una aplicación o una red Wi‑Fi?", ["Es un enlace", "Es un mensaje", "Es una red Wi‑Fi"])

    if re.search(r"https?\s+|www\s+|\b[a-z0-9-]+\s+(?:com|net|org)\b", text):
        return _reply("enlace_recibido", "No puedo confirmar que ese enlace sea seguro sólo por cómo se ve. Si no esperabas el mensaje, no lo abras. Entra al servicio desde su aplicación o escribe tú mismo la dirección oficial.", ["Me llegó por WhatsApp", "Me llegó por correo", "Ya lo abrí"])

    if _matches(text, "me mandaron un link", "me llego un link", "link raro", "sera falso", "sera estafa", "me llego algo raro", "correo raro", "mensaje raro", "le doy click"):
        return _reply("mensaje_por_revisar", "Podría ser un mensaje falso, pero necesito un dato para orientarte mejor. ¿Te llegó por correo, SMS, WhatsApp u otra aplicación? Mientras lo revisamos, no abras el enlace ni compartas información.", ["Por correo", "Por SMS", "Por WhatsApp"])
    suspicious_signals = ("urgente", "ultima oportunidad", "ganaste", "premio", "confirma tu cuenta", "verifica tu cuenta", "paga ahora", "comparte el codigo", "cuenta sera bloqueada")
    if len(text) >= 60 and any(signal in text for signal in suspicious_signals):
        return _reply("analisis_mensaje", "Veo señales que conviene tomar con cuidado, como presión, premios o solicitudes de información. No puedo confirmar que sea falso sólo por el texto, pero no pulses enlaces ni respondas. Comprueba el aviso directamente con la empresa o persona por un canal oficial.", ["También trae un enlace", "Me pide un código", "Ya respondí"])
    if _matches(text, "archivo inesperado", "archivo raro", "adjunto raro", "me mandaron un archivo", "habilitar macros", "habilitar contenido"):
        return _reply("archivo_sospechoso", "No abras el archivo ni actives contenido o macros. Confirma con la persona que supuestamente lo envió usando otro medio. Si no lo esperabas o no puedes confirmarlo, elimínalo y repórtalo.", ["Ya lo abrí", "Me llegó por correo", "¿Cómo lo reporto?"])
    if _matches(text, "internet lento tengo virus", "computadora lenta tiene virus", "telefono lento tiene virus", "se calienta tengo virus"):
        return _reply("diagnostico_incierto", "No necesariamente. La lentitud o el calentamiento pueden tener varias causas. Revisa si también aparecen aplicaciones que no instalaste, anuncios extraños o cambios que no hiciste. Si no ves esas señales, prueba cerrar aplicaciones y reiniciar el equipo.", ["Veo aplicaciones desconocidas", "Me salen anuncios solos", "Sólo está lento"])
    if _matches(text, "telefono esta raro", "compu anda rara", "se instalaron cosas", "anuncios solos", "apps que no conozco", "aplicaciones desconocidas", "telefono se calienta"):
        return _reply("dispositivo_por_revisar", "Eso puede tener varias causas y no confirma que sea un virus. Primero elimina aplicaciones que no reconozcas, revisa sus permisos, actualiza el equipo y ejecuta el análisis de seguridad que ya incluye el sistema. Si continúa, busca soporte técnico confiable.", ["Descargué algo antes", "¿Cómo reviso permisos?", "¿Necesito antivirus?"])
    if _matches(text, "me dijeron que gane", "gane un iphone", "premio inesperado", "depositar primero", "dinero urgente", "dice que es mi primo", "oferta demasiado buena"):
        return _reply("posible_fraude", "Hay señales que hacen dudar, pero no puedo confirmarlo sólo con eso. No envíes dinero ni datos todavía. Comprueba la historia hablando con la persona o empresa por un número oficial que tú ya conozcas.", ["Me piden pagar primero", "Me piden un código", "Me enviaron un enlace"])

    if _matches(text, "no entendi", "no entiendo", "explicamelo facil", "como asi", "decime sencillo", "no se de computadoras", "me perdi") and previous:
        clarified = answer_from_knowledge(token, user_id, previous, [])
        if clarified["intent"] != "ayuda_general":
            clarified["respuesta"] = f"Claro, te lo explico más fácil: {clarified['respuesta']}"
            return clarified

    if _matches(text, "perdi mi celular", "robaron mi celular", "dispositivo perdido", "perdi la computadora"):
        return _reply("dispositivo_perdido", "Siento que estés pasando por esto. Desde otro teléfono o computadora, intenta localizarlo y bloquearlo. Cambia primero la contraseña de tu correo y cierra las sesiones abiertas. Si perdiste el celular, avisa también a tu compañía telefónica. No vayas a buscarlo si eso puede ponerte en peligro.", ["¿Cómo cierro sesiones abiertas?", "¿Cómo protejo mi teléfono?", "¿Qué es la verificación en dos pasos?"])

    # Las urgencias se evalúan primero para no confundirlas con dudas generales.
    if _matches(text, "abri un enlace", "abri enlace", "abri un link", "abri link", "ya le di click", "hice clic", "di mis datos", "la regue", "me hackearon", "me jakieron", "me hackiaron", "robaron mi cuenta", "me rovaron", "alguien entro", "entraron a mi cuenta", "se metio a mi correo", "queriendo entrar", "cambiaron mi contrasena", "inicio que no fui yo", "intentos de inicio", "cuenta comprometida", "actividad extrana", "incidente"):
        return _reply("incidente", "Tranquilo, vamos paso a paso. Cambia la contraseña desde un equipo seguro, cierra las sesiones que no reconozcas y activa la verificación en dos pasos. Si compartiste datos de una tarjeta, llama al banco. Si es una cuenta de estudio o trabajo, avisa a la persona encargada. Guarda capturas de lo ocurrido.", ["¿Cómo recupero una cuenta?", "¿Cómo reporto un correo falso?", "¿Qué es la verificación en dos pasos?"])
    if _matches(text, "olvide mi contrasena", "no puedo entrar", "recuperar cuenta", "bloquearon mi cuenta"):
        return _reply("recuperar_cuenta", "Entra a la página o aplicación oficial y pulsa «Olvidé mi contraseña». Si usaste la misma clave en otra cuenta, cámbiala también. Cierra las sesiones que no reconozcas y nunca compartas el código que recibas para recuperar la cuenta.", ["¿Cómo creo una contraseña segura?", "¿Qué es la verificación en dos pasos?", "¿Qué hago si entraron a mi cuenta?"])
    if _matches(text, "perdi mi celular", "robaron mi celular", "dispositivo perdido", "perdi la computadora"):
        return _reply("dispositivo_perdido", "Siento que estés pasando por esto. Desde otro teléfono o computadora, intenta localizarlo y bloquearlo. Cambia primero la contraseña de tu correo y cierra las sesiones abiertas. Si perdiste el celular, avisa también a tu compañía telefónica. No vayas a buscarlo si eso puede ponerte en peligro.", ["¿Cómo cierro sesiones abiertas?", "¿Cómo protejo mi teléfono?", "¿Qué es la verificación en dos pasos?"])

    if _matches(text, "como estas", "como te va", "todo bien", "que tal estas"):
        return _reply("estado", "¡Estoy muy bien, gracias por preguntar! 😊 Listo para ayudarte. ¿Cómo estás tú?", ["Estoy bien, gracias", "Necesito ayuda", "Dame un consejo"])
    if _matches(text, "estoy bien", "todo bien gracias", "me siento bien"):
        return _reply("estado_usuario_bien", "¡Qué bueno saberlo! 😊 Si quieres, podemos revisar tu seguridad digital o puedo mostrarte alguna parte de CyberLey.", ["Revisar mi resultado", "Dame un consejo", "Muéstrame CyberLey"])
    if _matches(text, "estoy mal", "preocupado", "preocupada", "tengo miedo", "necesito ayuda urgente"):
        return _reply("estado_usuario_preocupado", "Lo siento. Vamos con calma y paso a paso. Si crees que alguien entró a una cuenta o compartiste información por error, cuéntame qué pasó y te indicaré qué hacer primero.", ["Entraron a mi cuenta", "Abrí un enlace extraño", "Perdí mi celular"])
    if _matches(text, "adios", "hasta luego", "nos vemos", "chao"):
        return _reply("despedida", "¡Hasta luego! 👋 Recuerda que puedes volver cuando tengas una duda. Cuidarte en internet empieza con pequeños pasos.", ["Dame un último consejo", "Cerrar sesión"])
    if _matches(text, "eres un robot", "eres inteligencia artificial", "eres una ia", "eres humano", "eres real"):
        return _reply("identidad", "Soy un asistente virtual con forma de pequeño guardián digital 🤖. No soy una persona, pero fui creado para explicar las cosas con calma y ayudarte dentro de CyberLey.", ["¿Quién te creó?", "¿Qué puedes hacer?", "Cuéntame de CyberLey"])
    if _matches(text, "quien te creo", "quien hizo ciby", "de donde vienes"):
        return _reply("origen", "Nací como el acompañante de CyberLey. Mi trabajo es hacer que aprender seguridad digital se sienta sencillo, cercano y nada aburrido 🛡️.", ["¿Qué puedes hacer?", "¿Por qué te llamas Ciby?", "Dame un consejo"])
    if _matches(text, "por que te llamas ciby", "que significa ciby", "tu nombre"):
        return _reply("nombre", "Me llamo Ciby porque suena cercano a «ciberseguridad». Soy pequeño, curioso y siempre llevo mi escudo listo para ayudarte 🛡️.", ["¿Qué puedes hacer?", "¿Cómo estás?", "Cuéntame de CyberLey"])
    if _matches(text, "cuantos anos tienes", "que edad tienes"):
        return _reply("edad", "Los asistentes virtuales no cumplimos años como las personas 😄. Digamos que soy joven, pero ya aprendí muchos trucos para cuidarte en internet.", ["Cuéntame un chiste", "¿Qué puedes hacer?", "Dame un truco de seguridad"])
    if _matches(text, "chiste", "hazme reir", "algo divertido"):
        return _reply("humor", "¿Por qué la contraseña fue al gimnasio? Porque quería hacerse más fuerte… y dejar de ser «123456» 😄", ["Otro consejo divertido", "¿Cómo creo una buena contraseña?", "¿Qué puedes hacer?"])
    if _matches(text, "te quiero", "me caes bien", "eres lindo", "eres bonita", "buen trabajo"):
        return _reply("afecto", "¡Qué bonito! 💜 Tú también me caes muy bien. Me alegra acompañarte mientras aprendes a cuidarte en internet.", ["¿Cómo estás?", "Dame un consejo", "Sigamos aprendiendo"])
    if _matches(text, "no ayudas", "no entiendes", "respuesta mala", "no sirves", "eres tonto", "eres estupido"):
        return _reply("disculpa", "Lo siento, esta vez no te entendí bien. Quiero ayudarte. Puedes contarme qué estás intentando hacer o elegir una opción y lo vemos juntos.", ["Usar CyberLey", "Proteger una cuenta", "Tuve un problema"])
    if _matches(text, "hola", "buenas", "buen dia", "quien eres", "que eres", "como te llamas"):
        return _reply("saludo", "¡Hola! Soy Ciby 😊 Estoy aquí para ayudarte. Puedo mostrarte cómo funciona CyberLey, explicarte tu resultado o darte consejos para cuidarte en internet. ¿Qué necesitas?", ["¿Qué hago primero?", "Explícame mi resultado", "Quiero proteger mis cuentas"])
    if _matches(text, "gracias", "muy amable", "me ayudaste"):
        return _reply("agradecimiento", "¡Con gusto! Me alegra haberte ayudado. La seguridad digital se construye con pequeños hábitos, así que puedes volver a preguntarme cuando lo necesites.", ["Dame un consejo rápido", "¿Cómo puedo mejorar?", "Ver mis guías"])
    if _matches(text, "que puedes hacer", "que puedo preguntarte", "en que ayudas", "temas conoces", "ayuda disponible"):
        return _reply("capacidades", "Puedo mostrarte cómo usar CyberLey, explicarte tus evaluaciones y ayudarte a cuidar tus cuentas, tu teléfono y tu información. También puedo orientarte si recibiste un mensaje extraño o crees que alguien entró a una cuenta.", ["Quiero proteger mis cuentas", "Creo que tuve un problema", "Explícame CyberLey"])
    if _matches(text, "primero", "empezar", "comenzar", "como funciona cyberley", "como uso", "que hago aqui"):
        return _reply("inicio", "Te recomiendo este camino: 1) responde una evaluación con sinceridad; 2) revisa tu nivel de riesgo y las observaciones; 3) practica con las guías sugeridas. No necesitas conocimientos técnicos y puedes avanzar a tu ritmo.", ["¿Cómo funciona la evaluación?", "¿Qué mide mi puntaje?", "¿Mis datos son privados?"], {"label": "Comenzar mi evaluación", "path": "/usuario/encuesta"})
    if _matches(text, "recorrido", "tour", "explicame la pagina", "muestrame el sistema"):
        return _reply("recorrido", "Puedo mostrarte nuevamente el recorrido visual. Pulsa el botón de brújula en la parte superior del chat; iré abriendo y resaltando cada sección importante.", ["¿Qué hago primero?", "¿Dónde veo mis resultados?", "¿Dónde están las guías?"])
    if _matches(text, "evaluacion", "encuesta", "cuestionario", "preguntas", "repetir evaluacion"):
        return _reply("evaluacion", "La evaluación analiza hábitos reales: contraseñas, mensajes sospechosos y protección del dispositivo. Responde pensando en lo que haces normalmente; no hay respuestas para castigarte. Cuando la envíes, el resultado quedará en tu historial.", ["¿Qué mide el puntaje?", "¿Puedo cambiar una respuesta?", "¿Dónde veo mis resultados?"], {"label": "Ver evaluaciones", "path": "/usuario/encuesta"})
    if _matches(text, "cambiar respuesta", "editar respuesta", "me equivoque al responder"):
        return _reply("editar_respuesta", "Para mantener coherente el historial, una evaluación enviada no se modifica desde el portal. Puedes consultar el resultado guardado; si fue un error importante, comunícalo al administrador para que revise el caso.", ["Ver mis resultados", "¿Cómo se calcula el riesgo?", "¿Quién ve mis respuestas?"], {"label": "Abrir resultados", "path": "/usuario/resultados"})
    if _matches(text, "mi riesgo", "mi puntaje", "mi resultado", "como sali", "cuanto saque"):
        try:
            results = user_risk_responses(token, user_id)
        except RuntimeError:
            return _reply("resultado_no_disponible", "Ahora mismo no pude consultar tu resultado, pero tus datos siguen guardados. Inténtalo otra vez en unos segundos o ábrelo desde «Mis resultados».", ["¿Cómo se interpreta el riesgo?", "¿Cómo puedo mejorar?"], {"label": "Abrir mis resultados", "path": "/usuario/resultados"})
        if not results:
            return _reply("resultado_personal", "Aún no tienes un resultado para interpretar. Al completar tu primera evaluación podré explicarte el puntaje y sugerirte por dónde comenzar.", ["¿Cómo funciona la evaluación?", "¿Mis datos son privados?"], {"label": "Hacer mi evaluación", "path": "/usuario/encuesta"})
        latest = results[0]
        score = latest.get("puntaje_riesgo", "sin puntaje")
        level = latest.get("clasificacion_riesgo", "sin clasificación")
        areas = _risk_areas(latest)
        if areas:
            priorities = "; y ".join(areas[:2])
            detail = f"Te recomiendo empezar por {priorities}."
        else:
            detail = latest.get("observacion") or "Abre el resultado para revisar qué hábito puedes fortalecer primero."
        return _reply("resultado_personal", f"Tu resultado más reciente es de {score} puntos y muestra un nivel {level}. Esto habla de tus hábitos, no de ti, y no significa que te hayan atacado. {detail}", ["¿Cómo puedo mejorar?", "¿Qué guías hay?", "¿Cómo se calcula?"], {"label": "Ver el resultado completo", "path": "/usuario/resultados"})
    if _matches(text, "puntaje", "riesgo alto", "riesgo medio", "riesgo bajo", "resultado", "como se calcula", "que significa riesgo"):
        return _reply("riesgo", "El puntaje muestra qué tan seguros son tus hábitos. Riesgo bajo significa que vas por buen camino; medio indica que puedes mejorar algunas cosas; alto significa que hay varios cuidados que conviene aplicar pronto. No es una nota ni significa que hiciste algo mal.", ["Explícame mi resultado", "¿Cómo puedo mejorar?", "Ver mis resultados"], {"label": "Consultar mi historial", "path": "/usuario/resultados"})
    if _matches(text, "mejorar", "guia", "aprender", "recomendacion", "consejo", "habito seguro"):
        return _reply("guias", "Vamos paso a paso. Empieza por una contraseña única y el doble factor en tu correo; después aprende a reconocer mensajes falsos y mantén tus dispositivos actualizados. En Guías encontrarás explicaciones breves para practicar cada hábito.", ["Dame un consejo rápido", "¿Cómo creo una contraseña segura?", "¿Qué es phishing?"], {"label": "Explorar las guías", "path": "/usuario/guias"})

    if _matches(text, "phishing", "correo falso", "correo sospechoso", "mensaje sospechoso", "enlace sospechoso", "estafa por correo", "remitente falso"):
        return _reply("phishing", "El phishing es un mensaje falso que busca engañarte para que entregues una contraseña, un código o dinero. Desconfía si te apuran o te amenazan. Revisa quién lo envió y no pulses el enlace; abre la página oficial por tu cuenta. Nadie debería pedirte tu contraseña por mensaje.", ["¿Qué hago si abrí un enlace?", "¿Cómo reporto un correo falso?", "¿Cómo reviso un enlace?"])
    if _matches(text, "reportar correo", "denunciar phishing", "marcar como spam"):
        return _reply("reportar_phishing", "No respondas ni reenvíes el mensaje de forma normal. Usa «Reportar phishing» o «Correo no deseado» y, si pertenece a tu universidad o trabajo, notifícalo al soporte oficial. Después elimínalo.", ["¿Cómo reconozco un correo falso?", "¿Qué hago si hice clic?", "¿Mis datos están seguros?"])
    if _matches(text, "revisar enlace", "link seguro", "url segura", "puedo abrir este enlace"):
        return _reply("enlaces", "No lo abras todavía. En una computadora, coloca el cursor encima para ver a dónde lleva. Revisa que el nombre de la página esté bien escrito y desconfía de direcciones muy cortas o mensajes que te apuran. El dibujo de un candado no garantiza que la página sea verdadera.", ["¿Qué es phishing?", "¿Qué hago si hice clic?", "¿Cómo reporto el mensaje?"])
    if _matches(text, "gestor", "administrador de contrasenas"):
        return _reply("gestor", "Un gestor de contraseñas es una aplicación que guarda tus claves por ti. Es más seguro que repetir la misma. Protégelo con una frase larga, activa la verificación en dos pasos y guarda sus códigos de recuperación en un lugar seguro.", ["¿Cómo creo una frase segura?", "¿Qué es la verificación en dos pasos?", "¿Dónde guardo códigos de recuperación?"])
    if _matches(text, "contrasena", "contra", "clave", "password", "misma clave"):
        return _reply("contrasenas", "Una buena contraseña es larga, única y difícil de adivinar. Usa una frase de varias palabras o deja que un gestor genere una clave aleatoria; nunca la reutilices. El gestor puede guardarla cifrada para que no debas memorizar todas.", ["¿Es seguro un gestor?", "¿Cómo activo el doble factor?", "¿Qué hago si filtraron mi clave?"])
    if _matches(text, "doble factor", "dos pasos", "2fa", "autenticacion", "verificacion en dos pasos", "activar verificacion", "codigo de verificacion"):
        return _reply("doble_factor", "La verificación en dos pasos agrega una segunda barrera después de tu contraseña. Por ejemplo, puede pedirte un código desde el teléfono. Así, aunque alguien descubra tu clave, le será más difícil entrar. Nunca compartas un código que tú no pediste.", ["¿Dónde guardo códigos de recuperación?", "¿Qué pasa si pierdo el teléfono?", "¿Cómo protejo mi contraseña?"])
    if _matches(text, "codigo de recuperacion", "codigos de respaldo", "backup codes"):
        return _reply("codigos_recuperacion", "Guárdalos fuera del teléfono donde usas el autenticador: impresos en un lugar privado o dentro de un gestor confiable. Cada código suele funcionar una sola vez y jamás debes enviárselo a otra persona.", ["¿Qué es el doble factor?", "¿Qué hago si pierdo mi teléfono?", "¿Es seguro un gestor?"])
    if _matches(text, "wifi publico", "wifi gratis", "red publica", "cafeteria", "aeropuerto"):
        return _reply("wifi_publico", "El Wi‑Fi gratis puede ser útil, pero evita revisar el banco o enviar información importante. Confirma el nombre de la red con el lugar, desactiva la conexión automática y, si puedes, usa los datos de tu teléfono.", ["¿Necesito una VPN?", "¿Cómo protejo mi teléfono?", "¿Qué significa el candado de una página?"])
    if _matches(text, "vpn"):
        return _reply("vpn", "Una VPN es una aplicación que ayuda a proteger tu conexión, especialmente en redes públicas. Aun así, no evita mensajes falsos, virus ni páginas engañosas. Si vas a usar una, elige un servicio conocido y confiable.", ["¿Es seguro el Wi-Fi público?", "¿Qué significa el candado?", "¿Cómo reconozco un mensaje falso?"])
    if _matches(text, "virus", "birus", "malware", "ransomware", "computadora rara", "telefono raro", "ventanas emergentes"):
        return _reply("malware", "Si el equipo se comporta de forma extraña, desconéctalo de internet, no introduzcas contraseñas y ejecuta un análisis con la protección actualizada. No pagues ni instales supuestas soluciones mostradas en ventanas emergentes; pide ayuda técnica confiable si continúa.", ["¿Cómo hago una copia de seguridad?", "¿Qué hago si me hackearon?", "¿Necesito antivirus?"])
    if _matches(text, "antivirus", "actualizar", "actualizacion", "dispositivo", "proteger mi telefono", "proteger mi computadora"):
        return _reply("dispositivos", "Activa las actualizaciones automáticas, usa bloqueo con PIN o biometría y descarga programas sólo de tiendas o sitios oficiales. La protección integrada suele ser suficiente si permanece activa y actualizada.", ["¿Necesito antivirus?", "¿Cómo hago una copia de seguridad?", "¿Qué permisos debo revisar?"])
    if _matches(text, "copia de seguridad", "respaldo", "backup", "guardar mis archivos"):
        return _reply("copias_seguridad", "Mantén una copia automática de tus archivos importantes y otra separada del dispositivo principal. Comprueba de vez en cuando que puedas restaurarlas; una copia que nunca se prueba puede fallar cuando más la necesitas.", ["¿Dónde guardo la copia?", "¿Qué es ransomware?", "¿Cómo protejo mi computadora?"])
    if _matches(text, "permiso", "camara", "microfono", "ubicacion", "aplicaciones"):
        return _reply("permisos", "Revisa periódicamente qué aplicaciones acceden a cámara, micrófono, contactos y ubicación. Conserva sólo los permisos necesarios mientras usas la aplicación y elimina las que ya no reconozcas o utilices.", ["¿Cómo protejo mi privacidad?", "¿Es segura una aplicación?", "¿Cómo protejo mi teléfono?"])
    if _matches(text, "red social", "facebook", "instagram", "tiktok", "publicar", "perfil publico"):
        return _reply("redes_sociales", "Limita quién ve tus publicaciones, evita mostrar ubicación o rutinas en tiempo real y revisa etiquetas antes de que aparezcan. Desconfía de perfiles que pidan códigos, dinero o información personal, aunque parezcan conocidos.", ["¿Cómo detecto una cuenta falsa?", "¿Qué datos no debo publicar?", "¿Cómo protejo mi privacidad?"])
    if _matches(text, "cuenta falsa", "perfil falso", "suplantacion", "se hacen pasar por mi", "robo de identidad"):
        return _reply("suplantacion", "Guarda capturas y la dirección del perfil, repórtalo desde la plataforma y avisa a tus contactos por otro canal. Refuerza la privacidad de tu cuenta y cambia la contraseña si sospechas que también obtuvieron acceso. No confrontes ni envíes documentos al perfil falso.", ["¿Cómo protejo mis redes sociales?", "¿Qué hago si me hackearon?", "¿Cómo creo una contraseña segura?"])
    if _matches(text, "descargar", "archivo adjunto", "aplicacion segura", "app segura", "programa seguro"):
        return _reply("descargas", "Descarga sólo desde la tienda oficial o la página auténtica del proveedor. Revisa quién publica la aplicación, sus permisos, reseñas y fecha de actualización. No abras adjuntos inesperados, aunque parezcan facturas o documentos urgentes.", ["¿Cómo reviso un enlace?", "¿Qué permisos debo revisar?", "¿Qué hago si abrí un archivo?"])
    if _matches(text, "privado", "privacidad", "mis datos", "quien ve", "respuestas seguras", "administrador ve"):
        return _reply("privacidad", "CyberLey protege tus respuestas para que otros usuarios no puedan verlas. Las personas administradoras sólo usan la información necesaria para manejar el sistema y revisar los resultados. Recuerda: nunca escribas contraseñas ni datos de tarjetas en una respuesta.", ["¿Qué ve el administrador?", "¿Cómo funciona la evaluación?", "¿Cómo cierro sesión?"])
    if _matches(text, "cerrar sesion", "salir de cyberley", "logout", "desconectarme"):
        return _reply("sesion", "Selecciona tu nombre en la esquina superior derecha y pulsa «Cerrar sesión». Hazlo siempre en equipos compartidos; cerrar solamente la pestaña no necesariamente termina la sesión.", ["¿Mis datos son privados?", "¿Cómo uso CyberLey?", "¿Cómo protejo un equipo compartido?"])
    if _matches(text, "equipo compartido", "computadora publica", "cyber cafe"):
        return _reply("equipo_compartido", "Evita guardar contraseñas, usa una ventana privada si no tienes alternativa y cierra sesión al terminar. No descargues archivos sensibles. Para cuentas importantes, es preferible usar tu propio dispositivo.", ["¿Cómo cierro sesión?", "¿Es seguro el Wi-Fi público?", "¿Cómo activo el doble factor?"])
    if _matches(text, "https", "candado"):
        return _reply("https", "El candado indica que la información viaja protegida entre tu navegador y la página. Pero cuidado: una página falsa también puede tenerlo. Revisa siempre que el nombre del sitio esté bien escrito y piensa cómo llegaste hasta ahí.", ["¿Cómo reviso un enlace?", "¿Qué es phishing?", "¿Es seguro el Wi-Fi público?"])
    if _matches(text, "ciberseguridad", "seguridad digital", "seguridad en internet"):
        return _reply("ciberseguridad", "La seguridad digital son los cuidados que tomas para proteger tus cuentas, tus dispositivos y tu información. Se parece a cerrar la puerta de casa: una buena contraseña, las actualizaciones y pensar antes de abrir un enlace son parte de esos cuidados.", ["Dame un consejo fácil", "¿Cómo protejo mis cuentas?", "¿Qué es un mensaje falso?"])
    if _matches(text, "hacker", "hackear", "hackeo"):
        return _reply("hacker", "La palabra hacker suele usarse para alguien que conoce mucho de computadoras. Algunas personas usan ese conocimiento para proteger; otras intentan entrar sin permiso. Si crees que alguien entró a tu cuenta, puedo ayudarte a reaccionar.", ["Entraron a mi cuenta", "¿Cómo evito que me hackeen?", "¿Cómo protejo mi contraseña?"])
    if _matches(text, "spam", "correo basura", "mensaje basura"):
        return _reply("spam", "El spam son mensajes que no pediste y que suelen enviarse a muchas personas. Algunos sólo son publicidad, pero otros pueden ser engaños. No respondas, no abras enlaces extraños y usa el botón «Marcar como spam».", ["¿Cómo reconozco un engaño?", "¿Qué es phishing?", "¿Cómo reporto un correo?"])
    if _matches(text, "codigo qr", "qr", "escanear codigo"):
        return _reply("qr", "Un código QR puede llevarte a una página igual que un enlace. Antes de continuar, revisa la dirección que muestra el teléfono. Si pide una contraseña, dinero o datos personales sin que lo esperes, ciérralo.", ["¿Cómo reviso un enlace?", "Abrí una página extraña", "¿Qué es phishing?"])
    if _matches(text, "usb", "memoria encontrada", "pendrive"):
        return _reply("usb", "No conectes una memoria USB desconocida o encontrada: podría dañar el equipo o copiar información. Si pertenece a tu trabajo o universidad, entrégala a la persona encargada de tecnología.", ["¿Cómo protejo mi computadora?", "¿Qué es un virus?", "¿Es segura una descarga?"])
    if _matches(text, "compra por internet", "comprar en linea", "tienda falsa", "pagar por internet"):
        return _reply("compras", "Antes de comprar, revisa que la tienda sea conocida, busca opiniones fuera de su propia página y desconfía de precios demasiado bajos. Evita transferencias a desconocidos y nunca compartas el código secreto de tu tarjeta.", ["¿Cómo reviso una página?", "Creo que me estafaron", "¿Qué significa el candado?"])
    if _matches(text, "estafa", "me enganaron", "transferi dinero", "fraude"):
        return _reply("estafa", "Lo siento. Guarda mensajes, recibos y capturas. Contacta de inmediato a tu banco o al medio de pago para preguntar si pueden detener la operación. No vuelvas a enviar dinero, aunque prometan devolverte lo perdido.", ["¿Qué datos debo guardar?", "Entraron a mi cuenta", "¿Cómo evito otra estafa?"])
    if _matches(text, "acoso", "ciberacoso", "amenaza", "me molestan", "publicaron fotos", "foto intima"):
        return _reply("acoso", "Siento que estés viviendo esto. No respondas a las amenazas ni pagues. Guarda capturas, bloquea y reporta la cuenta, y cuéntaselo a una persona de confianza. Si hay peligro inmediato o publicaron contenido íntimo, busca ayuda de las autoridades de tu país.", ["¿Cómo guardo pruebas?", "¿Cómo bloqueo una cuenta?", "Necesito cuidar mi privacidad"])
    if _matches(text, "nube", "google drive", "onedrive", "dropbox"):
        return _reply("nube", "Guardar archivos en la nube puede ser seguro si proteges la cuenta con una buena contraseña y verificación en dos pasos. Revisa con quién compartes cada carpeta y elimina accesos que ya no hagan falta.", ["¿Cómo comparto un archivo con seguridad?", "¿Qué es la verificación en dos pasos?", "¿Cómo hago una copia de seguridad?"])
    if _matches(text, "cookie", "cookies"):
        return _reply("cookies", "Las cookies son pequeños datos que una página guarda para recordar tu sesión o tus preferencias. Algunas también siguen tu actividad. Puedes rechazar las que no sean necesarias y borrarlas desde la configuración del navegador.", ["¿Cómo cuido mi privacidad?", "¿Qué significa el candado?", "¿Es segura una página?"])
    if _matches(text, "eliminar cuenta", "borrar mis datos", "derechos", "contactar administrador", "soporte"):
        return _reply("soporte", "Para solicitudes sobre tu cuenta o tus datos, contacta al administrador responsable de CyberLey por el canal oficial de tu institución. No envíes contraseñas ni códigos de acceso en la solicitud.", ["¿Quién ve mis respuestas?", "¿Cómo cierro sesión?", "¿Mis datos son privados?"])

    return _reply("ayuda_general", "Perdón, no logré entender bien 😅. ¿Puedes darme un poco más de información? También puedes elegir una de estas opciones.", ["Necesito usar CyberLey", "Quiero cuidar mis cuentas", "Tuve un problema de seguridad"])
