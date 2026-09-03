import { useEffect, useMemo, useState } from "react";
import { FiActivity, FiArrowRight, FiCalendar, FiClipboard, FiShield, FiTrendingDown } from "react-icons/fi";
import { Link } from "react-router-dom";
import { State } from "../../components/common/ModuleUI";
import api from "../../services/api";

function formatDate(value) { return value ? new Date(value).toLocaleDateString("es-HN", { day: "2-digit", month: "long", year: "numeric" }) : "Fecha no disponible"; }
function riskLabel(value) { return value ? `Riesgo ${value}` : "Sin clasificación"; }

export default function ResultsPage() {
  const [rows, setRows] = useState([]), [loading, setLoading] = useState(true), [error, setError] = useState(""), [filter, setFilter] = useState("todos");
  useEffect(() => { api.cachedGet("/riesgo/mis-resultados", {}, 0).then(({ data }) => setRows(data.items || [])).catch((requestError) => setError(requestError.message)).finally(() => setLoading(false)); }, []);
  const scores = useMemo(() => rows.map((item) => Number(item.puntaje_riesgo)).filter(Number.isFinite), [rows]);
  const visibleRows = filter === "todos" ? rows : rows.filter((item) => item.clasificacion_riesgo === filter);
  const latest = rows[0], average = scores.length ? Math.round(scores.reduce((total, score) => total + score, 0) / scores.length) : null;
  const previousScore = rows.length > 1 ? Number(rows[1].puntaje_riesgo) : null;
  const change = latest && Number.isFinite(previousScore) ? Math.round(Number(latest.puntaje_riesgo) - previousScore) : null;
  if (loading) return <State loading />;
  if (error) return <State error={error} />;
  return <div className="userResultsPage">
    <section className="userPageHero userResultsHero"><div><span className="userSectionLabel">MI EVOLUCIÓN</span><h2>Tu seguridad, explicada con claridad</h2><p>Revisa todas tus evaluaciones, identifica cambios y continúa mejorando tus hábitos digitales.</p></div><Link to="/usuario/encuesta" className="userHeroButton">Nueva evaluación <FiArrowRight /></Link></section>
    {!rows.length ? <section className="userEmptyState"><div className="userEmptyIcon"><FiClipboard /></div><div><span className="userSectionLabel">AÚN SIN RESULTADOS</span><h2>Realiza tu primera evaluación</h2><p>Al terminar podrás consultar aquí tu nivel de riesgo, puntaje y recomendaciones.</p><Link to="/usuario/encuesta" className="userPrimaryButton">Comenzar ahora</Link></div></section> : <>
      <section className="userOverviewGrid">
        <article className="userStatCard"><div className="userStatHeader"><span>Evaluaciones</span><FiClipboard /></div><strong className="userBigNumber">{rows.length}</strong><span className="userStatDescription">Historial completo</span></article>
        <article className="userStatCard"><div className="userStatHeader"><span>Último puntaje</span><FiActivity /></div><strong className="userBigNumber">{latest.puntaje_riesgo}</strong><span className="userStatDescription">Registrado el {formatDate(latest.fecha_respuesta)}</span></article>
        <article className="userStatCard"><div className="userStatHeader"><span>Nivel actual</span><FiShield /></div><strong className={`userRiskText ${latest.clasificacion_riesgo}`}>{riskLabel(latest.clasificacion_riesgo)}</strong><span className="userStatDescription">Según tu evaluación más reciente</span></article>
        <article className="userStatCard"><div className="userStatHeader"><span>Promedio</span><FiTrendingDown /></div><strong className="userBigNumber">{average ?? "—"}</strong><span className="userStatDescription">{change === null ? "Completa otra evaluación para comparar" : `${change > 0 ? "+" : ""}${change} puntos frente a la anterior`}</span></article>
      </section>
      <section className="userHistoryCard userResultsCard"><div className="userCardHeading"><div><span className="userSectionLabel">HISTORIAL</span><h2>Todas tus evaluaciones</h2></div><div className="userFilterPills" aria-label="Filtrar resultados">{["todos", "bajo", "medio", "alto"].map((value) => <button type="button" className={filter === value ? "active" : ""} onClick={() => setFilter(value)} key={value}>{value === "todos" ? "Todos" : riskLabel(value)}</button>)}</div></div>
        <div className="userResultTimeline">{visibleRows.map((item, index) => <article className="userResultRow" key={item.id_respuesta || `${item.fecha_respuesta}-${index}`}><div className={`userTimelineIcon ${item.clasificacion_riesgo}`}><FiShield /></div><div className="userResultRowMain"><span><FiCalendar /> {formatDate(item.fecha_respuesta)}</span><h3>{item.tipo_evaluacion || "Evaluación general"}</h3><p>{item.observacion || "Esta evaluación no incluye una observación adicional."}</p></div><div className="userResultScore"><strong>{item.puntaje_riesgo}</strong><span>puntos</span><em className={`userRiskBadge ${item.clasificacion_riesgo}`}>{riskLabel(item.clasificacion_riesgo)}</em></div></article>)}{!visibleRows.length && <div className="moduleState">No tienes evaluaciones con este nivel.</div>}</div>
      </section>
    </>}
  </div>;
}
