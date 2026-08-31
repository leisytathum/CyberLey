import { useEffect, useMemo, useState } from "react";
import { FiActivity, FiAlertTriangle, FiArrowLeft, FiSearch, FiShield, FiTrendingUp, FiUsers, FiX } from "react-icons/fi";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import api from "../../services/api";
import { State } from "../../components/common/ModuleUI";

const PAGE_SIZE = 8;
const riskLabels = { bajo: "Bajo", medio: "Medio", alto: "Alto" };
const riskColors = { bajo: "#16a34a", medio: "#f59e0b", alto: "#ef4444" };
const formatDate = (value) => {
  if (!value) return "—";
  const date = new Date(value);
  return `${String(date.getDate()).padStart(2, "0")} ${date.toLocaleDateString("es-HN", { month: "short" }).replace(".", "")} ${date.getFullYear()}`;
};
const initials = (name) => String(name || "U").trim().split(/\s+/).filter(Boolean).slice(0, 2).map((part) => part[0]).join("").toUpperCase();

export default function RiskPage() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState(null);
  const [showUsers, setShowUsers] = useState(false);

  useEffect(() => {
    let active = true;
    api.cachedGet("/riesgo", {}, 0)
      .then(({ data: response }) => { if (active) setData(response); })
      .catch((requestError) => { if (active) setError(requestError.message); });
    return () => { active = false; };
  }, []);

  const rows = useMemo(() => {
    const query = search.trim().toLowerCase();
    return (data?.items || []).filter((item) => (!filter || item.clasificacion_riesgo === filter)
      && (!query || item.nombre_usuario?.toLowerCase().includes(query) || item.tipo_evaluacion?.toLowerCase().includes(query)));
  }, [data, filter, search]);

  useEffect(() => setPage(1), [filter, search]);
  const pageCount = Math.max(1, Math.ceil(rows.length / PAGE_SIZE));
  const visibleRows = rows.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  const distribution = Object.entries(data?.distribucion || {}).map(([nivel, cantidad]) => ({ nivel: riskLabels[nivel], key: nivel, cantidad }));
  const knowledge = useMemo(() => {
    const grouped = {};
    for (const item of data?.conocimiento_riesgo || []) grouped[item.categoria] = (grouped[item.categoria] || 0) + item.cantidad;
    return Object.entries(grouped).map(([categoria, cantidad]) => ({ categoria, cantidad }));
  }, [data]);
  const knowledgeTotal = knowledge.reduce((total, item) => total + item.cantidad, 0);
  const knowledgeLevels = ["Bajo", "Medio", "Alto"].map((level) => {
    const count = knowledge.find((item) => item.categoria.toLowerCase() === level.toLowerCase())?.cantidad || 0;
    return { level, count, percentage: knowledgeTotal ? Math.round(count * 100 / knowledgeTotal) : 0 };
  });
  const frequentFactors = (data?.factores || []).slice(0, 5);
  const maximumFactor = Math.max(...frequentFactors.map((item) => item.cantidad), 1);
  const metrics = data ? [
    { label: "Evaluaciones", value: data.total, note: "Generales y configurables", icon: FiActivity, tone: "purple" },
    { label: "Promedio de riesgo", value: `${data.promedio_riesgo}%`, note: "Puntaje general", icon: FiTrendingUp, tone: "blue" },
    { label: "Riesgo alto", value: data.distribucion.alto, note: "Requieren atención", icon: FiAlertTriangle, tone: "red" },
    { label: "Riesgo medio", value: data.distribucion.medio, note: "Necesitan seguimiento", icon: FiShield, tone: "amber" },
  ] : [];

  return <div className="riskAnalysisPage">
    <State loading={!data && !error} error={error} />
    {data && <>
      <div className="riskPageActions"><button type="button" onClick={() => setShowUsers(true)}><FiUsers /> Ver riesgo por usuario <span>{data.total}</span></button></div>
      <section className="riskMetrics" aria-label="Resumen general de riesgo">{metrics.map(({ label, value, note, icon: Icon, tone }) => <article className="riskMetric" key={label}><span className={`riskMetricIcon ${tone}`}><Icon /></span><div><small>{label}</small><strong>{value}</strong><p>{note}</p></div></article>)}</section>

      {!data.total ? <State empty emptyText="No hay evaluaciones de riesgo registradas." /> : <>
        <section className="riskOverviewGrid">
          <article className="moduleCard riskDistributionSummary"><header><div><h3>Distribución de riesgo</h3><p>Clasificación general de las evaluaciones</p></div><strong>{data.total} en total</strong></header><div className="riskDistributionBar">{distribution.map((item) => <i key={item.key} style={{ width: `${data.total ? item.cantidad * 100 / data.total : 0}%`, background: riskColors[item.key] }} />)}</div><div className="riskDistributionLevels">{distribution.map((item) => <div key={item.key}><span><i style={{ background: riskColors[item.key] }} />{item.nivel}</span><strong>{item.cantidad}</strong><small>{data.total ? Math.round(item.cantidad * 100 / data.total) : 0}%</small></div>)}</div></article>
          <article className="moduleCard riskTrendCompact"><header><div><h3>Tendencia</h3><p>Evaluaciones registradas por fecha</p></div><FiTrendingUp /></header><ResponsiveContainer width="100%" height={190}><LineChart data={data.tendencia} margin={{ top: 18, right: 20, left: -18, bottom: 0 }}><CartesianGrid strokeDasharray="3 3" vertical={false} /><XAxis dataKey="fecha" tick={{ fontSize: 10 }} /><YAxis allowDecimals={false} tick={{ fontSize: 10 }} /><Tooltip /><Line type="monotone" dataKey="evaluaciones" stroke="#6d28d9" strokeWidth={3} dot={{ fill: "#6d28d9", r: 4 }} /></LineChart></ResponsiveContainer></article>
        </section>

        <section className="moduleCard riskInsightsCard"><div className="riskFactorsCompact"><header><div><h3>Factores más frecuentes</h3><p>Hábitos que aumentan la exposición</p></div><FiAlertTriangle /></header><div>{frequentFactors.map((item) => <div className="riskFactorRow" key={item.nombre}><span>{item.nombre}</span><div><i style={{ width: `${item.cantidad * 100 / maximumFactor}%` }} /></div><strong>{item.cantidad}</strong></div>)}</div></div><div className="riskKnowledgeCompact"><header><div><h3>Conocimiento digital</h3><p>Nivel reportado por los usuarios</p></div><FiUsers /></header><div>{knowledgeLevels.map((item) => <div className={`riskKnowledgeMini ${item.level.toLowerCase()}`} key={item.level}><span><FiShield /> {item.level}</span><div><i style={{ width: `${item.percentage}%` }} /></div><strong>{item.count}</strong><small>{item.percentage}%</small></div>)}</div></div></section>

      </>}
    </>}

    {showUsers && <div className="moduleModal" onClick={() => setShowUsers(false)}><article className="moduleModalContent riskUsersModal" onClick={(event) => event.stopPropagation()}><button className="participantModalClose" onClick={() => setShowUsers(false)} aria-label="Cerrar listado"><FiX /></button><header className="riskUsersModalHeader"><span><FiUsers /></span><div><h2>Riesgo por usuario</h2><p>Resultados generales y de encuestas configurables.</p></div></header><div className="riskTableFilters"><label><FiSearch /><input placeholder="Buscar usuario o encuesta..." value={search} onChange={(event) => setSearch(event.target.value)} /></label><select value={filter} onChange={(event) => setFilter(event.target.value)}><option value="">Todos los niveles</option><option value="bajo">Riesgo bajo</option><option value="medio">Riesgo medio</option><option value="alto">Riesgo alto</option></select></div><State empty={!rows.length} emptyText="No hay resultados que coincidan con los filtros." />{!!visibleRows.length && <div className="moduleTableWrap"><table className="moduleTable riskTable"><thead><tr><th>Usuario</th><th>Evaluación</th><th>Fecha</th><th>Puntaje</th><th>Riesgo</th><th>Detalle</th></tr></thead><tbody>{visibleRows.map((item, index) => <tr key={`${item.id_respuesta || item.id}-${index}`}><td><div className="riskUser"><span>{initials(item.nombre_usuario)}</span><strong>{item.nombre_usuario || "Usuario"}</strong></div></td><td>{item.tipo_evaluacion || "Evaluación general"}</td><td>{formatDate(item.fecha_respuesta)}</td><td><strong>{item.puntaje_riesgo ?? 0}</strong></td><td><span className={`riskBadge ${item.clasificacion_riesgo}`}>{riskLabels[item.clasificacion_riesgo] || "Sin clasificar"}</span></td><td><button className="participantDetailButton" onClick={() => { setShowUsers(false); setSelected(item); }}>Ver detalle</button></td></tr>)}</tbody></table></div>}{!!rows.length && <footer className="participantsPagination"><span>Mostrando {(page - 1) * PAGE_SIZE + 1} a {Math.min(page * PAGE_SIZE, rows.length)} de {rows.length} resultados</span><div><button disabled={page === 1} onClick={() => setPage((current) => current - 1)}>‹</button><strong>{page}</strong><button disabled={page === pageCount} onClick={() => setPage((current) => current + 1)}>›</button></div></footer>}</article></div>}

    {selected && <div className="moduleModal" onClick={() => setSelected(null)}><article className="moduleModalContent riskDetailModal" onClick={(event) => event.stopPropagation()}><button className="riskDetailBack" type="button" onClick={() => { setSelected(null); setShowUsers(true); }}><FiArrowLeft /> Volver a usuarios</button><button className="participantModalClose" onClick={() => setSelected(null)} aria-label="Cerrar detalle"><FiX /></button><div className="riskDetailPerson"><span>{initials(selected.nombre_usuario)}</span><div><small>{selected.tipo_evaluacion || "Evaluación general"}</small><h2>{selected.nombre_usuario}</h2><p>{formatDate(selected.fecha_respuesta)}</p></div><strong className={`riskBadge ${selected.clasificacion_riesgo}`}>{riskLabels[selected.clasificacion_riesgo]}</strong></div><div className="riskDetailScore"><span>Puntaje de riesgo</span><strong>{selected.puntaje_riesgo ?? 0}</strong></div><div className="participantDetailGrid"><p><span>Conocimiento</span><strong>{selected.nivel_conocimiento || "No aplica"}</strong></p><p><span>Reconoce phishing</span><strong>{selected.reconoce_phishing || "No aplica"}</strong></p><p><span>Antivirus</span><strong>{selected.estado_antivirus || "No aplica"}</strong></p><p><span>Reutiliza contraseñas</span><strong>{selected.reutiliza_contrasenas || "No aplica"}</strong></p></div>{Array.isArray(selected.respuestas) && !!selected.respuestas.length && <section className="riskAnswerList"><h3>Respuestas de la encuesta</h3>{selected.respuestas.map((answer) => <div key={`${answer.id_pregunta}-${answer.orden}`}><span>{answer.orden}. {answer.pregunta}</span><strong>{String(answer.valor ?? "Sin respuesta")}</strong><small>{answer.puntos || 0} puntos</small></div>)}</section>}<div className="participantObservation"><span>Resultado</span><p>{selected.observacion || "Evaluación registrada correctamente."}</p></div></article></div>}
  </div>;
}
