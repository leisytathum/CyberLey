import re
import unicodedata
from difflib import SequenceMatcher

from app.services.risk_service import user_risk_responses


def _normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.casefold())
    value = "".join(character for character in value if not unicodedata.combining(character))
    return re.sub(r"[^a-z0-9\s]", " ", value)


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


def answer_from_knowledge(token: str, user_id: str, question: str) -> dict:
    text = _normalize(question)

    # Las urgencias se evalúan primero para no confundirlas con dudas generales.
    if _matches(text, "abri un enlace", "hice clic", "di mis datos", "me hackearon", "robaron mi cuenta", "cuenta comprometida", "actividad extrana", "incidente"):
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
        observation = latest.get("observacion") or "Revisa las recomendaciones para elegir tu próximo hábito."
        return _reply("resultado_personal", f"Tu resultado más reciente es de {score} puntos y corresponde a un riesgo {level}. No es una nota ni un diagnóstico: orienta sobre hábitos que puedes fortalecer. {observation}", ["¿Cómo puedo mejorar?", "Muéstrame las guías", "¿Cómo se calcula?"], {"label": "Ver el resultado completo", "path": "/usuario/resultados"})
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
    if _matches(text, "contrasena", "clave", "password", "misma clave"):
        return _reply("contrasenas", "Una buena contraseña es larga, única y difícil de adivinar. Usa una frase de varias palabras o deja que un gestor genere una clave aleatoria; nunca la reutilices. El gestor puede guardarla cifrada para que no debas memorizar todas.", ["¿Es seguro un gestor?", "¿Cómo activo el doble factor?", "¿Qué hago si filtraron mi clave?"])
    if _matches(text, "doble factor", "dos pasos", "2fa", "autenticacion", "codigo de verificacion"):
        return _reply("doble_factor", "La verificación en dos pasos agrega una segunda barrera después de tu contraseña. Por ejemplo, puede pedirte un código desde el teléfono. Así, aunque alguien descubra tu clave, le será más difícil entrar. Nunca compartas un código que tú no pediste.", ["¿Dónde guardo códigos de recuperación?", "¿Qué pasa si pierdo el teléfono?", "¿Cómo protejo mi contraseña?"])
    if _matches(text, "codigo de recuperacion", "codigos de respaldo", "backup codes"):
        return _reply("codigos_recuperacion", "Guárdalos fuera del teléfono donde usas el autenticador: impresos en un lugar privado o dentro de un gestor confiable. Cada código suele funcionar una sola vez y jamás debes enviárselo a otra persona.", ["¿Qué es el doble factor?", "¿Qué hago si pierdo mi teléfono?", "¿Es seguro un gestor?"])
    if _matches(text, "wifi publico", "wifi gratis", "red publica", "cafeteria", "aeropuerto"):
        return _reply("wifi_publico", "El Wi‑Fi gratis puede ser útil, pero evita revisar el banco o enviar información importante. Confirma el nombre de la red con el lugar, desactiva la conexión automática y, si puedes, usa los datos de tu teléfono.", ["¿Necesito una VPN?", "¿Cómo protejo mi teléfono?", "¿Qué significa el candado de una página?"])
    if _matches(text, "vpn"):
        return _reply("vpn", "Una VPN es una aplicación que ayuda a proteger tu conexión, especialmente en redes públicas. Aun así, no evita mensajes falsos, virus ni páginas engañosas. Si vas a usar una, elige un servicio conocido y confiable.", ["¿Es seguro el Wi-Fi público?", "¿Qué significa el candado?", "¿Cómo reconozco un mensaje falso?"])
    if _matches(text, "virus", "malware", "ransomware", "computadora rara", "ventanas emergentes"):
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
    if _matches(text, "eliminar cuenta", "borrar mis datos", "derechos", "contactar administrador", "soporte"):
        return _reply("soporte", "Para solicitudes sobre tu cuenta o tus datos, contacta al administrador responsable de CyberLey por el canal oficial de tu institución. No envíes contraseñas ni códigos de acceso en la solicitud.", ["¿Quién ve mis respuestas?", "¿Cómo cierro sesión?", "¿Mis datos son privados?"])

    return _reply("ayuda_general", "Perdón, no logré entender bien 😅. ¿Puedes darme un poco más de información? También puedes elegir una de estas opciones.", ["Necesito usar CyberLey", "Quiero cuidar mis cuentas", "Tuve un problema de seguridad"])
