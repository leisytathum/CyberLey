import { useEffect, useState } from "react";
import { FiArrowRight, FiBookOpen, FiCheck, FiClipboard, FiShield } from "react-icons/fi";
import { Link } from "react-router-dom";

import { State } from "../../components/common/ModuleUI";
import { useAuth } from "../../context/AuthContext";
import api from "../../services/api";

function formatDate(value) {
  return value ? new Date(value).toLocaleDateString("es-HN", { day: "2-digit", month: "long", year: "numeric" }) : "Sin fecha";
}

export default function UserOverviewPage() {
  const { profile } = useAuth();
  const [summary, setSummary] = useState(null), [error, setError] = useState("");
  useEffect(() => {
    async function load() {
      try {
        const { data } = await api.cachedGet("/usuario/resumen", {}, 30000);
        setSummary(data);
      } catch (requestError) {
        if (requestError.status !== 404) {
          setError(requestError.message);
          return;
        }
        try {
          const [resultsResponse, surveysResponse, guidesResponse] = await Promise.all([
            api.cachedGet("/riesgo/mis-resultados", {}, 0),
            api.cachedGet("/encuestas-configurables/disponibles", {}, 0),
            api.cachedGet("/guias", {}, 0),
          ]);
          const results = resultsResponse.data.items || [];
          const surveys = surveysResponse.data.items || [];
          const guides = guidesResponse.data.items || [];
          setSummary({
            ultimo_resultado: results[0] || null,
            resultados_recientes: results.slice(0, 5),
            guias_sugeridas: guides.filter((guide) => !guide.completada).slice(0, 3),
            metricas: {
              evaluaciones: results.length,
              encuestas_disponibles: surveys.length,
              encuestas_pendientes: surveys.filter((survey) => !survey.respondida).length,
              guias_disponibles: guides.length,
              guias_completadas: guides.filter((guide) => guide.completada).length,
            },
          });
        } catch (fallbackError) {
          setError(fallbackError.message);
        }
      }
    }
    load();
  }, []);
  if (!summary && !error) return <State loading />;
  if (error) return <State error={error} />;

  const latest = summary.ultimo_resultado;
  const metrics = summary.metricas;
  const firstName = profile?.nombre_completo?.trim().split(" ")[0] || "Usuario";
  return <div className="userOverviewPage">
    <section className="userEditorialHero">
      <div><span>MI ESPACIO DE SEGURIDAD</span><h1>Hola, {firstName}.</h1><p>Un recorrido simple para entender tus hábitos y proteger mejor tu vida digital.</p><Link to="/usuario/encuesta">Continuar mi evaluación <FiArrowRight /></Link></div>
      <div className="userHeroSignal"><FiShield /><span>Estado actual</span><strong>{latest ? `Riesgo ${latest.clasificacion_riesgo}` : "Pendiente"}</strong><small>{latest ? `Actualizado el ${formatDate(latest.fecha_respuesta)}` : "Completa tu primera evaluación"}</small></div>
    </section>

    <nav className="userJourney" aria-label="Tu recorrido de seguridad">
      <Link to="/usuario/encuesta"><i>01</i><FiClipboard /><span><strong>Evalúa</strong><small>{metrics.encuestas_pendientes} evaluaciones pendientes</small></span><FiArrowRight /></Link>
      <Link to="/usuario/resultados"><i>02</i><FiShield /><span><strong>Comprende</strong><small>{metrics.evaluaciones} resultados en tu historial</small></span><FiArrowRight /></Link>
      <Link to="/usuario/guias"><i>03</i><FiBookOpen /><span><strong>Mejora</strong><small>{metrics.guias_disponibles} guías para aprender</small></span><FiArrowRight /></Link>
    </nav>

    <section className="userEditorialBody">
      <div className="userLatestStory">
        <span className="userSectionLabel">TU ÚLTIMO RESULTADO</span>
        {latest ? <><div className={`userEditorialScore ${latest.clasificacion_riesgo}`}><strong>{latest.puntaje_riesgo}</strong><span>puntos de riesgo</span></div><h2>{latest.tipo_evaluacion || "Evaluación general"}</h2><p>{latest.observacion}</p><Link to="/usuario/resultados">Consultar todo mi historial <FiArrowRight /></Link></> : <><h2>Empieza conociendo tus hábitos</h2><p>Tu evaluación genera un resultado privado y recomendaciones concretas. No necesitas conocimientos técnicos.</p><Link to="/usuario/encuesta">Realizar mi primera evaluación <FiArrowRight /></Link></>}
      </div>
      <aside className="userLearningList"><header><span className="userSectionLabel">PRÓXIMAS LECTURAS</span><Link to="/usuario/guias">Ver todas</Link></header>{summary.guias_sugeridas.length ? summary.guias_sugeridas.map((guide) => <Link to="/usuario/guias" key={guide.id_guia}><FiCheck /><span><strong>{guide.titulo}</strong><small>{guide.categoria || "Ciberseguridad"}</small></span><FiArrowRight /></Link>) : <p>Ya completaste todas las guías disponibles.</p>}</aside>
    </section>
  </div>;
}
