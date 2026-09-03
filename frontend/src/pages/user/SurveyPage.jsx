import { useEffect, useState } from "react";
import { FiArrowLeft, FiArrowRight, FiCheckCircle, FiClipboard, FiClock, FiSend, FiShield } from "react-icons/fi";
import { Link } from "react-router-dom";
import { toast } from "sonner";
import api from "../../services/api";
import { State } from "../../components/common/ModuleUI";

export default function SurveyPage() {
  const [surveys, setSurveys] = useState([]), [selected, setSelected] = useState(null), [answers, setAnswers] = useState({}), [result, setResult] = useState(null), [loading, setLoading] = useState(true), [error, setError] = useState(""), [submitting, setSubmitting] = useState(false);
  useEffect(() => {
    async function load() {
      try {
        const { data } = await api.cachedGet("/encuestas-configurables/disponibles", {}, 0);
        setSurveys(data.items || []);
      } catch (requestError) { setError(requestError.message); }
      finally { setLoading(false); }
    }
    load();
  }, []);
  async function open(item) { if (item.respondida) return; setLoading(true); setError(""); try { const { data } = await api.cachedGet(`/encuestas-configurables/${item.id}`, {}, 0); setSelected(data); setAnswers({}); setResult(null); } catch (requestError) { setError(requestError.message); } finally { setLoading(false); } }
  async function submit(event) {
    event.preventDefault(); setSubmitting(true); setError("");
    try {
      const respuestas = selected.preguntas.filter((question) => answers[question.id] !== undefined && answers[question.id] !== "").map((question) => ({ id_pregunta: question.id, valor: answers[question.id] }));
      const { data } = await api.post(`/encuestas-configurables/${selected.id}/responder`, { respuestas });
      setResult(data); setSurveys((current) => current.map((item) => item.id === selected.id ? { ...item, respondida: true } : item)); toast.success("Encuesta guardada correctamente.");
    } catch (requestError) { setError(requestError.message); toast.error(requestError.message); }
    finally { setSubmitting(false); }
  }
  const questionCount = selected?.preguntas?.length || 0;
  const answeredCount = selected?.preguntas?.filter((question) => answers[question.id] !== undefined && answers[question.id] !== "").length || 0;
  const progress = questionCount ? Math.round(answeredCount * 100 / questionCount) : 0;
  const completedCount = surveys.filter((item) => item.respondida).length;
  if (loading) return <State loading />;
  if (error && !selected) return <State error={error} />;
  if (result) return <section className="dynamicSurveyResult"><div className="userResultSuccess"><FiCheckCircle /></div><span>Evaluación completada</span><h2>{result.porcentaje_riesgo}% de riesgo</h2><strong className={`riskBadge ${result.clasificacion_riesgo}`}>Riesgo {result.clasificacion_riesgo}</strong><p>{result.observacion}</p><div className="dynamicResultActions"><Link className="userPrimaryButton" to="/usuario/resultados">Ver mis resultados <FiArrowRight /></Link><Link className="userSecondaryButton" to="/usuario/guias">Explorar guías</Link><button className="userTextLink" onClick={() => { setSelected(null); setResult(null); }}>Volver a evaluaciones</button></div></section>;
  if (selected) return <form className="dynamicSurveyForm" onSubmit={submit}><button type="button" className="dynamicSurveyBack" onClick={() => { setSelected(null); setError(""); }}><FiArrowLeft /> Mis evaluaciones</button><header className="dynamicSurveyHeader"><div><span>Evaluación disponible</span><h1>{selected.titulo}</h1><p>{selected.descripcion}</p></div><div className="dynamicSurveyCounter"><strong>{answeredCount}/{questionCount}</strong><span>respondidas</span></div></header><div className="dynamicProgress" aria-label={`${progress}% completado`}><span style={{ width: `${progress}%` }} /></div><div className="dynamicProgressText"><span>Tu progreso</span><strong>{progress}%</strong></div>{error && <div className="warningBox">{error}</div>}<div className="dynamicQuestionList">{selected.preguntas.map((question) => <section className="dynamicQuestion" key={question.id}><label htmlFor={question.id}><span>{question.orden}</span>{question.texto}{question.requerida && <em>Obligatoria</em>}</label>{question.tipo === "texto" ? <textarea id={question.id} rows="4" required={question.requerida} value={answers[question.id] || ""} onChange={(event) => setAnswers({ ...answers, [question.id]: event.target.value })} placeholder="Escribe tu respuesta..." /> : <div className="dynamicOptions">{question.opciones.map((option) => <label key={option.etiqueta}><input type="radio" name={question.id} required={question.requerida} checked={answers[question.id] === option.etiqueta} onChange={() => setAnswers({ ...answers, [question.id]: option.etiqueta })} /><span>{option.etiqueta}</span></label>)}</div>}</section>)}</div><button className="surveySubmit" type="submit" disabled={submitting}><FiSend /> {submitting ? "Guardando resultado..." : "Enviar y guardar evaluación"}</button></form>;
  return <div className="availableSurveys"><section className="userPageHero userSurveyHero"><div><span className="userSectionLabel">EVALUACIONES ACTIVAS</span><h2>Descubre cómo están tus hábitos digitales</h2><p>Responde con tranquilidad. Cada evaluación se guarda una sola vez y podrás consultar el resultado en tu historial.</p></div><div className="userHeroStat"><FiShield /><strong>{surveys.length - completedCount}</strong><span>pendientes</span></div></section><div className="surveySummary"><span><FiClipboard /> {surveys.length} disponibles</span><span><FiCheckCircle /> {completedCount} completadas</span><span><FiClock /> A tu propio ritmo</span></div><div className="availableSurveyGrid">{surveys.map((item) => <button key={item.id} className={item.respondida ? "completed" : ""} disabled={item.respondida} onClick={() => open(item)}><span className="availableSurveyIcon"><FiClipboard /></span><div><span className="userSectionLabel">{item.total_preguntas} PREGUNTAS</span><h2>{item.titulo}</h2><p>{item.descripcion}</p></div>{item.respondida ? <strong><FiCheckCircle /> Respondida</strong> : <strong>Comenzar <FiArrowRight /></strong>}</button>)}</div><State empty={!surveys.length} emptyText="No hay evaluaciones publicadas en este momento." /></div>;
}
