import { useEffect, useMemo, useRef, useState } from "react";
import { FiArrowLeft, FiArrowRight, FiCompass, FiHelpCircle, FiSend, FiX } from "react-icons/fi";
import { useLocation, useNavigate } from "react-router-dom";

import api from "../../services/api";

const steps = [
  {
    title: "¡Hola! Soy Ciby",
    text: "Seré tu guía en CyberLey. En menos de un minuto te mostraré cómo conocer y mejorar tu seguridad digital.",
  },
  {
    title: "Primero, evalúa tus hábitos",
    text: "Responde una evaluación con sinceridad. No hay respuestas buenas o malas y tu información se mantiene privada.",
    path: "/usuario/encuesta",
    target: "evaluation",
    screen: ".userSurveyHero, .dynamicSurveyHeader",
  },
  {
    title: "Después, comprende tu resultado",
    text: "Aquí encontrarás tu nivel de riesgo, observaciones y evolución. Un puntaje mayor significa que hay más hábitos por fortalecer.",
    path: "/usuario/resultados",
    target: "results",
    screen: ".userResultsHero",
  },
  {
    title: "Finalmente, mejora paso a paso",
    text: "Consulta guías breves y marca las que completes. Puedes volver a abrir este recorrido desde mi botón cuando quieras.",
    path: "/usuario/guias",
    target: "guides",
    screen: ".userGuidesHero",
  },
];

export default function CyberGuide({ profile }) {
  const navigate = useNavigate();
  const location = useLocation();
  const messagesEndRef = useRef(null);
  const [open, setOpen] = useState(false);
  const [step, setStep] = useState(0);
  const [mode, setMode] = useState("tour");
  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);
  const [focusRect, setFocusRect] = useState(null);
  const [messages, setMessages] = useState([{ role: "assistant", text: `¡Hola${profile?.nombre ? `, ${profile.nombre.split(" ")[0]}` : ""}! Soy Ciby 😊 Puedo ayudarte a usar CyberLey, entender tus resultados y cuidarte en internet. ¿Qué necesitas?`, suggestions: ["¿Qué puedes hacer?", "¿Qué hago primero?", "Explícame mi resultado", "Dame un consejo rápido"] }]);
  const storageKey = useMemo(() => profile?.id ? `cyberley_onboarding_${profile.id}` : "", [profile?.id]);
  const current = steps[step];

  useEffect(() => {
    if (!storageKey || profile?.rol !== "usuario" || profile?.onboarding_completado || localStorage.getItem(storageKey) === "completed") return undefined;
    const timer = window.setTimeout(() => { setMode("tour"); setOpen(true); }, 500);
    return () => window.clearTimeout(timer);
  }, [profile?.onboarding_completado, profile?.rol, storageKey]);

  useEffect(() => {
    if (!open || mode !== "tour" || !current.target) {
      setFocusRect(null);
      return undefined;
    }

    let observedElement;
    let frame;
    const updateFocus = () => {
      const screenElement = current.screen ? document.querySelector(current.screen) : null;
      const menuElement = document.querySelector(`[data-guide="${current.target}"]`);
      observedElement = screenElement || menuElement;
      if (!observedElement) return;
      const rect = observedElement.getBoundingClientRect();
      const padding = window.innerWidth < 700 ? 7 : 11;
      setFocusRect({
        top: Math.max(8, rect.top - padding),
        left: Math.max(8, rect.left - padding),
        width: Math.min(window.innerWidth - Math.max(8, rect.left - padding) - 8, rect.width + padding * 2),
        height: Math.min(window.innerHeight - Math.max(8, rect.top - padding) - 8, rect.height + padding * 2),
      });
      menuElement?.classList.add("cyberGuideSpotlight");
    };

    const timer = window.setTimeout(() => {
      const screenElement = current.screen ? document.querySelector(current.screen) : null;
      screenElement?.scrollIntoView({ behavior: "smooth", block: "center" });
      frame = window.requestAnimationFrame(updateFocus);
    }, 180);
    const observer = new ResizeObserver(updateFocus);
    window.addEventListener("resize", updateFocus);
    window.addEventListener("scroll", updateFocus, true);
    const observeTimer = window.setTimeout(() => observedElement && observer.observe(observedElement), 350);

    return () => {
      window.clearTimeout(timer);
      window.clearTimeout(observeTimer);
      window.cancelAnimationFrame(frame);
      observer.disconnect();
      window.removeEventListener("resize", updateFocus);
      window.removeEventListener("scroll", updateFocus, true);
      document.querySelectorAll(".cyberGuideSpotlight").forEach((element) => element.classList.remove("cyberGuideSpotlight"));
      setFocusRect(null);
    };
  }, [current.screen, current.target, location.pathname, mode, open]);

  useEffect(() => {
    if (open && mode === "chat") messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [asking, messages, mode, open]);

  function persistCompletion() {
    if (storageKey) localStorage.setItem(storageKey, "completed");
    api.post("/usuario/onboarding/completar").catch(() => {});
  }

  function closeTour() {
    persistCompletion();
    setOpen(false);
    setStep(0);
  }

  function next() {
    if (step === steps.length - 1) {
      closeTour();
      navigate("/usuario/encuesta");
      return;
    }
    const nextStep = step + 1;
    setStep(nextStep);
    if (steps[nextStep].path) navigate(steps[nextStep].path);
  }

  function previous() {
    const previousStep = Math.max(0, step - 1);
    setStep(previousStep);
    if (steps[previousStep].path) navigate(steps[previousStep].path);
  }

  function restart() {
    setStep(0);
    setMode("tour");
    setOpen(true);
  }

  function openChat() {
    setMode("chat");
    setOpen(true);
  }

  async function ask(event, preset = "") {
    event?.preventDefault();
    const value = (preset || question).trim();
    if (value.length < 2 || asking) return;
    setMessages((currentMessages) => [...currentMessages, { role: "user", text: value }]);
    setQuestion("");
    setAsking(true);
    try {
      const history = messages.slice(-8).map((message) => ({ rol: message.role === "user" ? "usuario" : "ciby", texto: message.text.slice(0, 500) }));
      const request = api.post("/usuario/asistente", { pregunta: value, historial: history })
        .then((response) => ({ response }))
        .catch((error) => ({ error }));
      const [{ response, error }] = await Promise.all([
        request,
        new Promise((resolve) => window.setTimeout(resolve, 850)),
      ]);
      if (error) throw error;
      const { data } = response;
      setMessages((currentMessages) => [...currentMessages, { role: "assistant", text: data.respuesta, suggestions: data.sugerencias || [], action: data.accion }]);
    } catch {
      setMessages((currentMessages) => [...currentMessages, { role: "assistant", text: "Uy, no pude responder en este momento 😕. Tus datos están bien; espera un momento e inténtalo otra vez.", suggestions: ["Necesito usar CyberLey", "¿Qué hago primero?"] }]);
    } finally {
      setAsking(false);
    }
  }

  return <>
    {!open && <button type="button" className="cyberGuideLauncher" onClick={openChat} aria-label="Preguntarle a Ciby"><img src="/cyberley-assistant.png" alt="" /><span><FiHelpCircle /> Pregúntame</span></button>}
    {open && <div className={`cyberGuideLayer ${mode === "chat" ? "chat" : step === 0 ? "welcome" : "tour"}`}>
      {mode === "tour" && step === 0 && <button type="button" className="cyberGuideScrim" onClick={closeTour} aria-label="Omitir recorrido" />}
      {mode === "tour" && focusRect && <div className="cyberGuideFocus" style={focusRect} aria-hidden="true"><span>Ciby te muestra esta sección</span></div>}
      {mode === "chat" ? <section className="cyberGuideChat" role="dialog" aria-label="Chat con Ciby">
        <header><div><img src="/cyberley-assistant.png" alt="" /><span><strong>Ciby</strong><small>Guía digital de CyberLey</small></span></div><div><button type="button" onClick={restart} title="Ver recorrido"><FiCompass /></button><button type="button" onClick={() => setOpen(false)} aria-label="Cerrar chat"><FiX /></button></div></header>
        <div className="cyberGuideChatMessages" aria-live="polite">{messages.map((message, index) => <div className={`cyberGuideBubble ${message.role}`} key={`${message.role}-${index}`}><p>{message.text}</p>{message.action && <button type="button" onClick={() => { navigate(message.action.path); setOpen(false); }}>{message.action.label}<FiArrowRight /></button>}{message.suggestions?.length > 0 && index === messages.length - 1 && <div className="cyberGuideSuggestions">{message.suggestions.map((suggestion) => <button type="button" onClick={() => ask(null, suggestion)} key={suggestion}>{suggestion}</button>)}</div>}</div>)}{asking && <div className="cyberGuideTyping" role="status"><img src="/cyberley-assistant.png" alt="" /><span>Ciby está escribiendo</span><div><i /><i /><i /></div></div>}<span ref={messagesEndRef} /></div>
        <form className="cyberGuideChatInput" onSubmit={ask}><input value={question} onChange={(event) => setQuestion(event.target.value)} maxLength="300" placeholder="Pregúntale algo a Ciby..." aria-label="Pregunta para Ciby" /><button type="submit" disabled={asking || question.trim().length < 2} aria-label="Enviar pregunta"><FiSend /></button></form>
      </section> : <section className="cyberGuidePanel" role="dialog" aria-modal={step === 0} aria-labelledby="cyber-guide-title">
        <button type="button" className="cyberGuideClose" onClick={closeTour} aria-label="Cerrar asistente"><FiX /></button>
        <div className="cyberGuideMascot"><span className="cyberGuideGlow" /><img src="/cyberley-assistant.png" alt="Ciby, asistente de CyberLey" /></div>
        <div className="cyberGuideMessage"><span className="cyberGuideName">CIBY · GUÍA DIGITAL</span><h2 id="cyber-guide-title">{current.title}</h2><p>{current.text}</p><div className="cyberGuideProgress" aria-label={`Paso ${step + 1} de ${steps.length}`}>{steps.map((_, index) => <i className={index <= step ? "active" : ""} key={index} />)}</div><div className="cyberGuideActions">{step > 0 ? <button type="button" className="cyberGuideBack" onClick={previous}><FiArrowLeft /> Atrás</button> : <button type="button" className="cyberGuideSkip" onClick={closeTour}>Ahora no</button>}<button type="button" className="cyberGuideNext" onClick={next}>{step === 0 ? "Muéstrame" : step === steps.length - 1 ? "Empezar" : "Siguiente"}<FiArrowRight /></button></div></div>
      </section>}
    </div>}
  </>;
}
