import { useEffect, useState } from "react";
import { FiArrowLeft, FiCheckCircle, FiClipboard, FiSend } from "react-icons/fi";
import { toast } from "sonner";
import api from "../../services/api";
import { State } from "../../components/common/ModuleUI";

export default function SurveyPage() {
  const [surveys, setSurveys] = useState([]), [selected, setSelected] = useState(null), [answers, setAnswers] = useState({}), [result, setResult] = useState(null), [loading, setLoading] = useState(true), [error, setError] = useState("");
  useEffect(() => {
    async function load() {
      try {
        const { data } = await api.cachedGet("/encuestas-configurables/disponibles", {}, 0);
        const items = data.items || [];
        setSurveys(items);
        const pending = items.find((item) => !item.respondida);
        if (pending) {
          const { data: detail } = await api.cachedGet(`/encuestas-configurables/${pending.id}`, {}, 0);
          setSelected(detail);
        }
      } catch (requestError) { setError(requestError.message); }
      finally { setLoading(false); }
    }
    load();
  }, []);
  async function open(item) { if (item.respondida) return; setLoading(true); try { const { data } = await api.cachedGet(`/encuestas-configurables/${item.id}`, {}, 0); setSelected(data); setAnswers({}); setResult(null); } catch (e) { setError(e.message); } finally { setLoading(false); } }
  async function submit(event) { event.preventDefault(); try { const respuestas = selected.preguntas.filter((question) => answers[question.id] !== undefined && answers[question.id] !== "").map((question) => ({ id_pregunta: question.id, valor: answers[question.id] })); const { data } = await api.post(`/encuestas-configurables/${selected.id}/responder`, { respuestas }); setResult(data); setSurveys((current) => current.map((item) => item.id === selected.id ? { ...item, respondida: true } : item)); toast.success("Encuesta guardada correctamente."); } catch (e) { toast.error(e.message); } }
  if (loading) return <State loading />;
  if (error) return <State error={error} />;
  if (result) return <section className="dynamicSurveyResult"><FiCheckCircle /><span>Evaluación completada</span><h2>{result.porcentaje_riesgo}% de riesgo</h2><strong className={`riskBadge ${result.clasificacion_riesgo}`}>{result.clasificacion_riesgo}</strong><p>{result.observacion}</p><button className="userPrimaryButton" onClick={() => { setSelected(null); setResult(null); }}>Volver a mis encuestas</button></section>;
  if (selected) return <form className="dynamicSurveyForm" onSubmit={submit}><button type="button" className="dynamicSurveyBack" onClick={() => setSelected(null)}><FiArrowLeft /> Mis encuestas</button><header><span>Evaluación disponible</span><h1>{selected.titulo}</h1><p>{selected.descripcion}</p></header><div className="dynamicQuestionList">{selected.preguntas.map((question) => <section className="dynamicQuestion" key={question.id}><label htmlFor={question.id}><span>{question.orden}</span>{question.texto}{question.requerida && <em>Obligatoria</em>}</label>{question.tipo === "texto" ? <textarea id={question.id} rows="4" required={question.requerida} value={answers[question.id] || ""} onChange={(e) => setAnswers({ ...answers, [question.id]: e.target.value })} /> : <div className="dynamicOptions">{question.opciones.map((option) => <label key={option.etiqueta}><input type="radio" name={question.id} required={question.requerida} checked={answers[question.id] === option.etiqueta} onChange={() => setAnswers({ ...answers, [question.id]: option.etiqueta })} /><span>{option.etiqueta}</span></label>)}</div>}</section>)}</div><button className="surveySubmit" type="submit"><FiSend /> Enviar y guardar evaluación</button></form>;
  return <div className="availableSurveys"><header><span>Mis evaluaciones</span><h1>Encuestas disponibles</h1><p>Responde cada encuesta una vez. Tus respuestas y resultado quedarán guardados.</p></header><div>{surveys.map((item) => <button key={item.id} disabled={item.respondida} onClick={() => open(item)}><FiClipboard /><div><h2>{item.titulo}</h2><p>{item.descripcion}</p><span>{item.total_preguntas} preguntas</span></div>{item.respondida ? <strong><FiCheckCircle /> Respondida</strong> : <strong>Comenzar</strong>}</button>)}</div><State empty={!surveys.length} emptyText="No hay encuestas publicadas en este momento." /></div>;
}
