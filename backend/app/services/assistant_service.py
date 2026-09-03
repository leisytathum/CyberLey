import re
import unicodedata
from difflib import SequenceMatcher

from app.services.risk_service import user_risk_responses


def _normalize(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.casefold())
    plain = "".join(character for character in normalized if not unicodedata.combining(character))
    return re.sub(r"[^a-z0-9\\s]", " ", plain)


def _response(intent: str, answer: str, suggestions: list[str], action: dict | None = None) -> dict:
    return {"intent": intent, "respuesta": answer, "sugerencias": suggestions[:3], "accion": action}


def _matches(text: str, *expressions: str) -> bool:
    """Recognise phrases and tolerate small spelling mistakes in longer words."""
    if any(expression in text for expression in expressions):
        return True
    words = text.split()
    candidates = [expression for expression in expressions if " " not in expression and len(expression) >= 6]
    return any(SequenceMatcher(None, word, candidate).ratio() >= 0.84 for word in words for candidate in candidates)


def _legacy_answer_user_question(token: str, user_id: str, question: str) -> dict:
    text = _normalize(question)
    if any(word in text for word in ("hola", "buenas", "quien eres", "que eres")):
        return _response("saludo", "¡Hola! Soy Ciby, tu guía dentro de CyberLey. Puedo explicarte las evaluaciones, tus resultados y prácticas de seguridad digital.", ["¿Qué hago primero?", "¿Mis datos son privados?", "¿Qué es el phishing?"])
    if any(word in text for word in ("primero", "empezar", "comenzar", "como funciona", "que hago")) and not any(word in text for word in ("abri", "enlace", "hack", "robaron", "incidente")):
        return _response("inicio", "Empieza en Evaluación y responde con sinceridad. Cuando termines, revisa Mis resultados y luego abre las guías recomendadas para mejorar paso a paso.", ["¿Cómo funciona la evaluación?", "¿Qué significa mi puntaje?"], {"label": "Ir a Evaluación", "path": "/usuario/encuesta"})
    if any(word in text for word in ("evaluacion", "encuesta", "preguntas")):
        return _response("evaluacion", "Cada evaluación analiza hábitos concretos, como contraseñas, phishing y protección del dispositivo. Sólo puede responderse una vez y el resultado se guarda en tu historial.", ["¿Qué significa riesgo alto?", "¿Dónde veo mis resultados?"], {"label": "Ver evaluaciones", "path": "/usuario/encuesta"})
    if any(word in text for word in ("mi riesgo", "mi puntaje", "mi resultado")):
        results = user_risk_responses(token, user_id)
        if not results:
            return _response("resultado_personal", "Todavía no tienes un resultado. Completa una evaluación y podré ayudarte a interpretarlo.", ["¿Qué hago primero?"], {"label": "Evaluarme", "path": "/usuario/encuesta"})
        latest = results[0]
        return _response("resultado_personal", f"Tu resultado más reciente es {latest.get('puntaje_riesgo')} puntos, clasificado como riesgo {latest.get('clasificacion_riesgo')}. {latest.get('observacion') or ''}".strip(), ["¿Cómo puedo mejorar?", "Muéstrame las guías"], {"label": "Abrir mi historial", "path": "/usuario/resultados"})
    if any(word in text for word in ("puntaje", "riesgo alto", "riesgo medio", "riesgo bajo", "resultado")):
        return _response("riesgo", "El puntaje representa exposición al riesgo: bajo indica hábitos generalmente seguros; medio señala aspectos por fortalecer; alto requiere atender varias prácticas cuanto antes. No es una calificación académica.", ["¿Cómo puedo mejorar?", "¿Qué es el phishing?"], {"label": "Ver resultados", "path": "/usuario/resultados"})
    if any(word in text for word in ("mejorar", "guia", "aprender", "recomendacion")):
        return _response("guias", "Las guías convierten tu resultado en acciones sencillas. Empieza por contraseñas y autenticación en dos pasos, continúa con phishing y termina revisando la seguridad de tus dispositivos.", ["¿Cómo creo una contraseña segura?", "¿Qué es el doble factor?"], {"label": "Explorar guías", "path": "/usuario/guias"})
    if any(word in text for word in ("phishing", "correo sospechoso", "enlace sospechoso")):
        return _response("phishing", "El phishing intenta engañarte para robar contraseñas o datos. Desconfía de mensajes urgentes, revisa el remitente, no abras enlaces inesperados y entra al sitio escribiendo su dirección directamente.", ["¿Qué hago si abrí un enlace?", "¿Cómo protejo mi contraseña?"])
    if any(word in text for word in ("contrasena", "clave", "password")):
        return _response("contrasenas", "Usa una contraseña distinta para cada cuenta, larga y difícil de adivinar. Un gestor de contraseñas puede crearlas y guardarlas por ti. Activa también la autenticación en dos pasos.", ["¿Qué es el doble factor?", "¿Cómo puedo mejorar?"])
    if any(word in text for word in ("doble factor", "dos pasos", "2fa", "autenticacion")):
        return _response("doble_factor", "La autenticación en dos pasos añade una segunda comprobación además de tu contraseña. Siempre que sea posible, utiliza una aplicación autenticadora en lugar de códigos por SMS.", ["¿Cómo protejo mi contraseña?", "Muéstrame las guías"])
    if any(word in text for word in ("antivirus", "actualizar", "dispositivo")):
        return _response("dispositivos", "Mantén el sistema, navegador y aplicaciones actualizados. Activa las actualizaciones automáticas y utiliza la protección integrada o un antivirus confiable.", ["¿Cómo puedo mejorar?", "¿Qué es el phishing?"])
    if any(word in text for word in ("privado", "privacidad", "mis datos", "quien ve")):
        return _response("privacidad", "Tus resultados están protegidos por tu sesión y las políticas de seguridad de la base de datos. Otros usuarios no pueden consultar tus respuestas; el administrador sólo accede a información necesaria para el análisis del proyecto.", ["¿Cómo funciona la evaluación?", "¿Qué hago primero?"])
    if any(word in text for word in ("cerrar sesion", "salir", "logout")):
        return _response("sesion", "Para cerrar sesión, selecciona tu nombre en la esquina superior derecha y luego elige “Cerrar sesión”.", ["¿Mis datos son privados?", "¿Qué hago primero?"])
    if any(word in text for word in ("cerre", "abrí", "abri", "hack", "robaron", "incidente")):
        return _response("incidente", "Si sospechas de un incidente, cambia de inmediato la contraseña afectada desde un dispositivo confiable, cierra sesiones abiertas, activa el doble factor y revisa movimientos o mensajes desconocidos.", ["¿Cómo protejo mi contraseña?", "¿Qué es el phishing?"])
    return _response("ayuda_general", "Puedo ayudarte con el uso de CyberLey, resultados, contraseñas, phishing, doble factor, privacidad y protección de dispositivos. Prueba preguntándome por uno de esos temas.", ["¿Qué hago primero?", "¿Qué significa mi puntaje?", "¿Cómo creo una contraseña segura?"])


def answer_user_question(token: str, user_id: str, question: str) -> dict:
    """Public entry point for Ciby's expanded conversational knowledge base."""
    from app.services.assistant_knowledge import answer_from_knowledge

    return answer_from_knowledge(token, user_id, question)
