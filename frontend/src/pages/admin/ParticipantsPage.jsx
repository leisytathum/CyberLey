import { useEffect, useMemo, useState } from "react";
import { FiAlertTriangle, FiCheckCircle, FiClock, FiSearch, FiTrendingUp, FiUsers, FiX } from "react-icons/fi";
import api from "../../services/api";
import { State } from "../../components/common/ModuleUI";

const PAGE_SIZE = 8;
const riskLabels = { sin_evaluar: "Sin evaluar", bajo: "Bajo", medio: "Medio", alto: "Alto" };

function initials(name = "") {
  return name.trim().split(/\s+/).slice(0, 2).map((part) => part[0]).join("").toUpperCase() || "P";
}

export default function ParticipantsPage() {
  const [rows, setRows] = useState([]);
  const [stats, setStats] = useState({});
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [education, setEducation] = useState("");
  const [risk, setRisk] = useState("");
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    api.cachedGet("/participantes")
      .then(({ data }) => { setRows(data.items || []); setStats(data.estadisticas || {}); })
      .catch((requestError) => setError(requestError.message))
      .finally(() => setLoading(false));
  }, []);

  const educationOptions = useMemo(
    () => [...new Set(rows.map((item) => item.nivel_educativo).filter(Boolean))].sort(),
    [rows],
  );
  const filtered = useMemo(() => {
    const query = search.trim().toLowerCase();
    return rows.filter((item) => (!query || item.nombre_completo?.toLowerCase().includes(query))
      && (!education || item.nivel_educativo === education)
      && (!risk || item.clasificacion_riesgo === risk));
  }, [rows, search, education, risk]);

  useEffect(() => setPage(1), [search, education, risk]);

  const pageCount = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const visibleRows = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  const firstResult = filtered.length ? (page - 1) * PAGE_SIZE + 1 : 0;
  const lastResult = Math.min(page * PAGE_SIZE, filtered.length);
  const metrics = [
    { label: "Participantes", value: stats.total, note: "Total registrados", icon: FiUsers, tone: "purple" },
    { label: "Evaluados", value: stats.evaluados, note: "Completaron evaluación", icon: FiCheckCircle, tone: "green" },
    { label: "Pendientes", value: stats.pendientes, note: "Aún sin evaluación", icon: FiClock, tone: "amber" },
    { label: "Riesgo alto", value: stats.riesgo_alto, note: "Requieren atención", icon: FiAlertTriangle, tone: "red" },
    { label: "Promedio", value: stats.promedio_riesgo, note: "Puntaje promedio", icon: FiTrendingUp, tone: "blue" },
  ];

  return <>
    <State loading={loading} error={error} />
    {!loading && !error && <>
      <section className="participantMetrics" aria-label="Resumen de participantes">
        {metrics.map(({ label, value, note, icon: Icon, tone }) => <article className="participantMetric" key={label}><div className={`participantMetricIcon ${tone}`}><Icon /></div><span>{label}</span><strong>{value ?? 0}</strong><small>{note}</small></article>)}
      </section>
      <section className="moduleCard participantsCard">
        <div className="participantsToolbar">
          <label className="participantsSearch"><FiSearch /><input aria-label="Buscar participante" placeholder="Buscar por nombre..." value={search} onChange={(event) => setSearch(event.target.value)} /></label>
          <div className="participantsFilters">
            <select value={education} onChange={(event) => setEducation(event.target.value)}><option value="">Todos los niveles</option>{educationOptions.map((option) => <option key={option}>{option}</option>)}</select>
            <select value={risk} onChange={(event) => setRisk(event.target.value)}><option value="">Todos los riesgos</option><option value="sin_evaluar">Sin evaluar</option><option value="bajo">Bajo</option><option value="medio">Medio</option><option value="alto">Alto</option></select>
          </div>
        </div>
        <State empty={!filtered.length} emptyText="No hay participantes que coincidan con los filtros." />
        {!!visibleRows.length && <div className="moduleTableWrap"><table className="moduleTable participantsTable"><thead><tr><th>Nombre</th><th>Edad</th><th>Ciudad</th><th>Nivel educativo</th><th>Encuestas</th><th>Puntaje</th><th>Riesgo</th><th>Acción</th></tr></thead><tbody>
          {visibleRows.map((item) => { const riskKey = item.clasificacion_riesgo || "sin_evaluar"; return <tr key={item.id_participante}><td><div className="participantIdentity"><span>{initials(item.nombre_completo)}</span><strong>{item.nombre_completo}</strong></div></td><td>{item.edad ?? "—"}</td><td>{item.ciudad || "—"}</td><td>{item.nivel_educativo || "—"}</td><td>{item.encuestas_realizadas}</td><td>{item.puntaje_riesgo ?? "—"}</td><td><span className={`riskBadge ${riskKey}`}>{riskLabels[riskKey] || riskKey}</span></td><td><button className="participantDetailButton" onClick={() => setSelected(item)}>Detalle</button></td></tr>; })}
        </tbody></table></div>}
        {!!filtered.length && <footer className="participantsPagination"><span>Mostrando {firstResult} a {lastResult} de {filtered.length} resultados</span><div><button disabled={page === 1} onClick={() => setPage((current) => current - 1)}>‹</button><strong>{page}</strong><button disabled={page === pageCount} onClick={() => setPage((current) => current + 1)}>›</button></div></footer>}
      </section>
    </>}
    {selected && <div className="moduleModal" onClick={() => setSelected(null)}><article className="moduleModalContent participantModal" onClick={(event) => event.stopPropagation()}><button className="participantModalClose" aria-label="Cerrar detalle" onClick={() => setSelected(null)}><FiX /></button><div className="participantIdentity participantModalIdentity"><span>{initials(selected.nombre_completo)}</span><div><h2>{selected.nombre_completo}</h2><p>{selected.ciudad || "Ciudad no registrada"}</p></div></div><div className="participantDetailGrid"><p><span>Género</span><strong>{selected.genero || "No registrado"}</strong></p><p><span>Nivel educativo</span><strong>{selected.nivel_educativo || "No registrado"}</strong></p><p><span>Conocimiento</span><strong>{selected.nivel_conocimiento || "Sin evaluar"}</strong></p><p><span>Reconoce phishing</span><strong>{selected.reconoce_phishing || "Sin evaluar"}</strong></p><p><span>Estado antivirus</span><strong>{selected.estado_antivirus || "Sin evaluar"}</strong></p><p><span>Reutiliza contraseñas</span><strong>{selected.reutiliza_contrasenas || "Sin evaluar"}</strong></p><p><span>Tipo de conexión</span><strong>{selected.tipo_conexion || "Sin evaluar"}</strong></p><p><span>Último riesgo</span><strong>{riskLabels[selected.clasificacion_riesgo] || "Sin evaluar"}</strong></p></div><div className="participantObservation"><span>Observación</span><p>{selected.observacion || "Sin evaluación registrada."}</p></div></article></div>}
  </>;
}
