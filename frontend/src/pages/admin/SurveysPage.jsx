import { useCallback, useEffect, useState } from "react";
import { FiArrowLeft, FiCheck, FiClipboard, FiEdit3, FiFileText, FiInfo, FiList, FiMove, FiPlus, FiSend, FiTrash2, FiUsers, FiX } from "react-icons/fi";
import { toast } from "sonner";
import api from "../../services/api";
import { State } from "../../components/common/ModuleUI";

const blankQuestion = () => ({ texto: "", tipo: "opcion", requerida: true, opciones: [{ etiqueta: "", puntos: 0 }, { etiqueta: "", puntos: 0 }] });
const blankSurvey = () => ({ titulo: "", descripcion: "", preguntas: [blankQuestion()] });
const formatDate = (value) => value ? new Date(value).toLocaleString("es-HN", { dateStyle: "medium", timeStyle: "short" }) : "—";
const stateLabel = (value) => value === "publicada" ? "Activa" : value === "cerrada" ? "Inactiva" : "Borrador";

export default function SurveysPage() {
  const [surveys, setSurveys] = useState([]);
  const [selected, setSelected] = useState(null);
  const [mode, setMode] = useState("list");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState(blankSurvey);
  const schemaMissing = error.includes("encuestas_dinamicas") || error.includes("schema cache");

  const load = useCallback(async () => {
    setLoading(true); setError("");
    try { const { data } = await api.cachedGet("/encuestas-configurables", {}, 0); setSurveys(data.items || []); }
    catch (requestError) { setError(requestError.message); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const open = async (id) => {
    setLoading(true); setError("");
    try { const { data } = await api.cachedGet(`/encuestas-configurables/${id}`, {}, 0); setSelected(data); setMode("detail"); }
    catch (requestError) { setError(requestError.message); }
    finally { setLoading(false); }
  };

  const updateQuestion = (questionIndex, values) => setForm((current) => ({
    ...current,
    preguntas: current.preguntas.map((item, index) => index === questionIndex ? { ...item, ...values } : item),
  }));

  const updateOption = (questionIndex, optionIndex, values) => setForm((current) => ({
    ...current,
    preguntas: current.preguntas.map((item, index) => index === questionIndex ? {
      ...item,
      opciones: item.opciones.map((answer, answerIndex) => answerIndex === optionIndex ? { ...answer, ...values } : answer),
    } : item),
  }));

  const changeType = (index, tipo) => {
    const opciones = tipo === "si_no"
      ? [{ etiqueta: "Sí", puntos: 0 }, { etiqueta: "No", puntos: 0 }]
      : tipo === "escala"
        ? [1, 2, 3, 4, 5].map((value) => ({ etiqueta: String(value), puntos: value - 1 }))
        : tipo === "texto" ? [] : [{ etiqueta: "", puntos: 0 }, { etiqueta: "", puntos: 0 }];
    updateQuestion(index, { tipo, opciones });
  };

  const removeQuestion = (questionIndex) => setForm((current) => ({ ...current, preguntas: current.preguntas.filter((_, index) => index !== questionIndex) }));
  const removeOption = (questionIndex, optionIndex) => setForm((current) => ({
    ...current,
    preguntas: current.preguntas.map((item, index) => index === questionIndex ? { ...item, opciones: item.opciones.filter((_, answerIndex) => answerIndex !== optionIndex) } : item),
  }));

  async function create(event) {
    event.preventDefault(); setSaving(true);
    try {
      const payload = { ...form, preguntas: form.preguntas.map((item) => ({ ...item, opciones: item.opciones.filter((value) => value.etiqueta.trim()) })) };
      const invalidOptionQuestion = payload.preguntas.find((item) => item.tipo === "opcion" && item.opciones.length < 2);
      if (form.titulo.trim().length < 3) throw new Error("El título debe contener al menos 3 caracteres.");
      if (payload.preguntas.some((item) => item.texto.trim().length < 3)) throw new Error("Cada pregunta debe contener al menos 3 caracteres.");
      if (invalidOptionQuestion) throw new Error("Cada pregunta de opción única necesita al menos dos respuestas.");
      await api.post("/encuestas-configurables", payload);
      toast.success("Encuesta creada como borrador."); setForm(blankSurvey()); setMode("list"); await load();
    } catch (requestError) { toast.error(requestError.message); }
    finally { setSaving(false); }
  }

  async function changeState(value) {
    try { await api.patch(`/encuestas-configurables/${selected.id}/estado`, { estado: value }); toast.success(value === "publicada" ? "Encuesta activa." : "Encuesta inactiva."); await open(selected.id); await load(); }
    catch (requestError) { toast.error(requestError.message); }
  }

  if (mode === "create") return (
    <form className="surveyBuilder" onSubmit={create}>
      <header className="surveyBuilderHeader">
        <button className="surveyBackButton" type="button" onClick={() => setMode("list")}><FiArrowLeft /> Volver a encuestas</button>
        <div className="surveyBuilderIdentity"><div className="surveyBuilderIcon"><FiEdit3 /></div><div className="surveyBuilderHeading"><span>Constructor de encuesta</span><h2>Crear encuesta</h2><p>Organiza las preguntas y asigna el puntaje de riesgo de cada respuesta.</p></div></div>
        <button className="surveySaveButton" type="submit" disabled={saving}><FiClipboard /> {saving ? "Guardando..." : "Guardar borrador"}</button>
      </header>

      <section className="moduleCard surveyBuilderMeta">
        <div className="surveySectionIntro"><div className="surveyInfoIcon"><FiInfo /></div><div><strong>Información general</strong><p>Estos datos ayudarán al participante a entender el propósito de la encuesta.</p></div></div>
        <div className="surveyMetaFields">
          <label><span>Título de la encuesta <b>*</b></span><input value={form.titulo} onChange={(event) => setForm((current) => ({ ...current, titulo: event.target.value }))} placeholder="Ej. Evaluación de hábitos digitales" minLength="3" maxLength="180" required /></label>
          <label><span>Descripción</span><div className="surveyDescriptionField"><textarea value={form.descripcion} onChange={(event) => setForm((current) => ({ ...current, descripcion: event.target.value }))} placeholder="Explica brevemente qué se evaluará..." maxLength="500" rows="3" /><small className={form.descripcion.length === 500 ? "limit" : ""}>{form.descripcion.length}/500</small></div></label>
        </div>
      </section>

      <div className="surveyQuestionsHeading"><div><span>Preguntas</span><strong>{form.preguntas.length}</strong></div><p>El participante las verá en este mismo orden.</p></div>
      <div className="surveyQuestionList">
        {form.preguntas.map((item, index) => <section className="moduleCard surveyQuestionEditor" key={index}>
          <header className="surveyQuestionHeader">
            <div className="surveyQuestionTitle"><span className="surveyQuestionNumber">{index + 1}</span><div><strong>Pregunta {index + 1}</strong><small>Configura el enunciado y las respuestas</small></div></div>
            <button className="surveyQuestionRemove" type="button" disabled={form.preguntas.length === 1} onClick={() => removeQuestion(index)} aria-label={`Eliminar pregunta ${index + 1}`}><FiTrash2 /></button>
          </header>
          <div className="surveyQuestionBody">
            <label className="surveyQuestionPrompt"><span>Enunciado <b>*</b></span><input value={item.texto} onChange={(event) => updateQuestion(index, { texto: event.target.value })} placeholder="Escribe aquí la pregunta..." minLength="3" maxLength="500" required /></label>
            <div className="surveyQuestionSettings">
              <label><span>Tipo de respuesta</span><div className="surveySelectWrap"><FiList /><select value={item.tipo} onChange={(event) => changeType(index, event.target.value)}><option value="opcion">Opción única</option><option value="si_no">Sí / No</option><option value="escala">Escala 1–5</option><option value="texto">Respuesta abierta</option></select></div></label>
              <button className={`surveyRequiredToggle ${item.requerida ? "active" : ""}`} type="button" role="switch" aria-checked={item.requerida} onClick={() => updateQuestion(index, { requerida: !item.requerida })}><span className="surveyToggleTrack"><i><FiCheck /></i></span><span><strong>{item.requerida ? "Obligatoria" : "Opcional"}</strong><small>{item.requerida ? "Debe responderse" : "Puede omitirse"}</small></span></button>
            </div>
            {!!item.opciones.length && <div className="surveyOptions">
              <div className="surveyOptionsHeader"><span>Opciones de respuesta</span><small>Puntos de riesgo</small></div>
              {item.opciones.map((answer, answerIndex) => <div className="surveyOptionRow" key={answerIndex}>
                <FiMove className="surveyOptionGrip" aria-hidden="true" />
                <span className="surveyOptionIndex">{answerIndex + 1}</span>
                <input aria-label={`Opción ${answerIndex + 1}`} placeholder={`Escribe la opción ${answerIndex + 1}`} value={answer.etiqueta} disabled={item.tipo === "si_no" || item.tipo === "escala"} onChange={(event) => updateOption(index, answerIndex, { etiqueta: event.target.value })} maxLength="160" required />
                <input className="surveyPointsInput" aria-label={`Puntos de la opción ${answerIndex + 1}`} type="number" min="0" max="100" value={answer.puntos} onChange={(event) => updateOption(index, answerIndex, { puntos: Number(event.target.value) })} />
                {item.tipo === "opcion" && <button type="button" className="surveyOptionRemove" disabled={item.opciones.length <= 2} onClick={() => removeOption(index, answerIndex)} aria-label={`Eliminar opción ${answerIndex + 1}`}><FiX /></button>}
              </div>)}
              {item.tipo === "opcion" && <button className="surveyAddOption" type="button" onClick={() => updateQuestion(index, { opciones: [...item.opciones, { etiqueta: "", puntos: 0 }] })}><FiPlus /> Añadir otra opción</button>}
            </div>}
          </div>
        </section>)}
      </div>
      <button className="surveyAddQuestion" type="button" onClick={() => setForm((current) => ({ ...current, preguntas: [...current.preguntas, blankQuestion()] }))}><FiPlus /> Añadir pregunta</button>
    </form>
  );

  if (mode === "detail" && selected) {
    const applications = selected.aplicaciones || [];
    return <div className="surveyDetailPage">
      <header className="surveyDetailHero">
        <button className="surveyDetailBack" onClick={() => setMode("list")}><FiArrowLeft /> Volver a encuestas</button>
        <div className="surveyDetailIdentity"><span className={`surveyState ${selected.estado}`}>{stateLabel(selected.estado)}</span><h2>{selected.titulo}</h2><p>{selected.descripcion || "Esta encuesta no tiene descripción."}</p></div>
        <div className="surveyDetailActions">{selected.estado === "borrador" && <button className="surveyPublishButton" onClick={() => changeState("publicada")}><FiSend /> Publicar encuesta</button>}{selected.estado !== "borrador" && <button className={`surveyActivationToggle ${selected.estado === "publicada" ? "active" : ""}`} type="button" role="switch" aria-checked={selected.estado === "publicada"} onClick={() => changeState(selected.estado === "publicada" ? "cerrada" : "publicada")}><span><i /></span>{selected.estado === "publicada" ? "Activa" : "Inactiva"}</button>}</div>
      </header>
      <section className="surveyDefinitionGrid"><article className="moduleCard"><span className="surveyMetricIcon"><FiEdit3 /></span><div><strong>{selected.preguntas?.length || 0}</strong><span>Preguntas ordenadas</span><small>Estructura de la encuesta</small></div></article><article className="moduleCard"><span className="surveyMetricIcon users"><FiUsers /></span><div><strong>{applications.length}</strong><span>Personas encuestadas</span><small>Respuestas recibidas</small></div></article></section>
      <section className="moduleCard participantsCard surveyResponsesCard"><div className="surveyResponsesTitle"><div><h3>Personas que respondieron</h3><p>Ordenadas por fecha de aplicación.</p></div><span>{applications.length} {applications.length === 1 ? "respuesta" : "respuestas"}</span></div>{!applications.length && <div className="surveyResponsesEmpty"><div className="surveyEmptyIllustration"><i /><FiFileText /><span>+</span><span>+</span></div><h3>Aún no hay respuestas para esta encuesta.</h3><p>{selected.estado === "borrador" ? "Publica la encuesta para que los participantes puedan comenzar a responder." : selected.estado === "publicada" ? "La encuesta está activa y esperando las primeras respuestas." : "Activa la encuesta cuando quieras volver a recibir respuestas."}</p>{selected.estado === "borrador" && <button className="surveyPublishButton" onClick={() => changeState("publicada")}><FiSend /> Publicar encuesta</button>}</div>}{!!applications.length && <div className="moduleTableWrap"><table className="moduleTable participantsTable"><thead><tr><th>Orden</th><th>Usuario</th><th>Fecha</th><th>Puntaje</th><th>Riesgo</th><th>Evaluación</th></tr></thead><tbody>{applications.map((row, index) => <tr key={row.id}><td>#{index + 1}</td><td><strong>{row.nombre_usuario}</strong></td><td>{formatDate(row.fecha_respuesta)}</td><td>{row.puntaje}/{row.puntaje_maximo}</td><td><span className={`riskBadge ${row.clasificacion_riesgo}`}>{row.clasificacion_riesgo}</span></td><td><button className="participantDetailButton" onClick={() => setSelected((current) => ({ ...current, activeApplication: row }))}>Ver respuestas</button></td></tr>)}</tbody></table></div>}</section>
      {selected.activeApplication && <div className="moduleModal" onClick={() => setSelected((current) => ({ ...current, activeApplication: null }))}><article className="moduleModalContent participantModal" onClick={(event) => event.stopPropagation()}><button className="participantModalClose" onClick={() => setSelected((current) => ({ ...current, activeApplication: null }))}><FiX /></button><h2>{selected.activeApplication.nombre_usuario}</h2><p>{selected.activeApplication.observacion}</p><div className="participantDetailGrid">{(selected.activeApplication.respuestas || []).map((answer) => <p key={answer.id_pregunta}><span>{answer.orden}. {answer.pregunta}</span><strong>{String(answer.valor ?? "Sin respuesta")}</strong><small>{answer.puntos} puntos</small></p>)}</div></article></div>}
    </div>;
  }

  return <><section className="surveysHero"><div><span>Encuestas configurables</span><h2>Crea, publica y analiza</h2><p>Cada encuesta conserva sus preguntas, participantes y evaluaciones en orden.</p></div><button className="surveyCreateButton" disabled={schemaMissing} onClick={() => setMode("create")}><FiPlus /> Crear encuesta</button></section>{schemaMissing ? <section className="surveySetupNotice"><strong>Configuración pendiente en Supabase</strong><p>Ejecuta la migración 005_encuestas_dinamicas.sql para habilitar la creación y aplicación de encuestas.</p></section> : <State loading={loading} error={error} />}{!error && <><section className="surveyDefinitionCards">{surveys.map((item) => <button className="surveyDefinitionCard" key={item.id} onClick={() => open(item.id)}><span className={`surveyState ${item.estado}`}>{stateLabel(item.estado)}</span><h3>{item.titulo}</h3><p>{item.descripcion || "Sin descripción"}</p><footer><span>{item.total_preguntas} preguntas</span><span>{item.total_respuestas} respuestas</span></footer></button>)}</section><State empty={!loading && !surveys.length} emptyText="No hay encuestas creadas. Comienza creando la primera." /></>}</>;
}
