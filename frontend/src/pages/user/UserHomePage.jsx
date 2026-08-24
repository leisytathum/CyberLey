import {
  useEffect,
  useMemo,
  useState,
} from "react";

import { Link } from "react-router-dom";

import api from "../../services/api";
import { useAuth } from "../../context/AuthContext";

function formatDate(value) {
  if (!value) return "Sin fecha";

  return new Date(value).toLocaleDateString(
    "es-HN",
    {
      day: "2-digit",
      month: "short",
      year: "numeric",
    }
  );
}

function riskLabel(value) {
  if (value === "alto") return "Riesgo alto";
  if (value === "medio") return "Riesgo medio";
  if (value === "bajo") return "Riesgo bajo";

  return "Sin evaluar";
}

export default function UserHomePage() {
  const { user, profile } = useAuth();

  const [evaluations, setEvaluations] =
    useState([]);

  const [loading, setLoading] =
    useState(true);
  const [error, setError] = useState("");

  const firstName =
    profile?.nombre_completo?.split(" ")[0] ||
    "usuario";

  useEffect(() => {
    async function loadEvaluations() {
      if (!user) {
        setLoading(false);
        return;
      }

      try {
        const { data } = await api.cachedGet("/riesgo/mis-resultados");
        setEvaluations((data.items || []).slice(0, 5));
      } catch (requestError) {
        setError(requestError.message);
      } finally { setLoading(false); }
    }

    loadEvaluations();
  }, [user]);

  const lastEvaluation =
    evaluations[0] || null;

  const averageScore =
    useMemo(() => {
      if (!evaluations.length) {
        return null;
      }

      const scores =
        evaluations
          .map(
            (item) =>
              item.puntaje_riesgo
          )
          .filter(
            (value) =>
              typeof value === "number"
          );

      if (!scores.length) {
        return null;
      }

      return Math.round(
        scores.reduce(
          (total, current) =>
            total + current,
          0
        ) / scores.length
      );
    }, [evaluations]);

  return (
    <div className="userDashboard">
      <section className="userWelcome">
        <div className="userWelcomeContent">
          <span className="userWelcomeBadge">
            MI ESPACIO CYBERLEY
          </span>

          <h1>
            Hola, {firstName} 👋
          </h1>

          <p>
            Conoce cómo tus hábitos digitales
            influyen en tu seguridad y recibe
            recomendaciones para proteger mejor
            tu información.
          </p>

          <div className="userWelcomeActions">
            <Link
              to="/usuario/encuesta"
              className="userPrimaryButton"
            >
              Realizar evaluación
            </Link>

            {lastEvaluation && (
              <a
                href="#ultimo-resultado"
                className="userSecondaryButton"
              >
                Ver mi resultado
              </a>
            )}
          </div>
        </div>

        <div className="userWelcomeVisual">
          <div className="securityOrb">
            <div className="securityShield">
              ✓
            </div>
          </div>

          <span>
            Tu seguridad digital empieza
            con conocer tus hábitos.
          </span>
        </div>
      </section>

      {loading ? (
        <div className="moduleSkeleton" aria-label="Actualizando resultados">
          <span /><span /><span />
        </div>
      ) : error ? <div className="warningBox">{error}</div> : !lastEvaluation ? (
        <section className="userEmptyState">
          <div className="userEmptyIcon">
            ?
          </div>

          <div>
            <span className="userSectionLabel">
              PRIMER PASO
            </span>

            <h2>
              Aún no conocemos tu nivel de riesgo
            </h2>

            <p>
              Completa tu primera evaluación de
              hábitos digitales. Te tomará pocos
              minutos y al finalizar recibirás tu
              nivel de riesgo y recomendaciones.
            </p>

            <Link
              to="/usuario/encuesta"
              className="userPrimaryButton"
            >
              Comenzar evaluación
            </Link>
          </div>
        </section>
      ) : (
        <>
          <section
            id="ultimo-resultado"
            className="userOverviewGrid"
          >
            <article className="userStatCard">
              <div className="userStatHeader">
                <span>
                  Último puntaje
                </span>

                <span className="userStatIcon">
                  ↗
                </span>
              </div>

              <strong className="userBigNumber">
                {
                  lastEvaluation.puntaje_riesgo
                }
              </strong>

              <span className="userStatDescription">
                Puntaje de riesgo digital
              </span>
            </article>

            <article className="userStatCard">
              <div className="userStatHeader">
                <span>
                  Nivel actual
                </span>

                <span
                  className={`userRiskDot ${
                    lastEvaluation
                      .clasificacion_riesgo ||
                    ""
                  }`}
                />
              </div>

              <strong
                className={`userRiskText ${
                  lastEvaluation
                    .clasificacion_riesgo ||
                  ""
                }`}
              >
                {riskLabel(
                  lastEvaluation
                    .clasificacion_riesgo
                )}
              </strong>

              <span className="userStatDescription">
                Según tu última evaluación
              </span>
            </article>

            <article className="userStatCard">
              <div className="userStatHeader">
                <span>
                  Evaluaciones
                </span>

                <span className="userStatIcon">
                  ✓
                </span>
              </div>

              <strong className="userBigNumber">
                {evaluations.length}
              </strong>

              <span className="userStatDescription">
                Evaluaciones recientes
              </span>
            </article>

            <article className="userStatCard">
              <div className="userStatHeader">
                <span>
                  Promedio
                </span>

                <span className="userStatIcon">
                  ≈
                </span>
              </div>

              <strong className="userBigNumber">
                {averageScore ?? "—"}
              </strong>

              <span className="userStatDescription">
                Promedio de riesgo reciente
              </span>
            </article>
          </section>

          <section className="userContentGrid">
            <article className="userResultCard">
              <div className="userCardHeading">
                <div>
                  <span className="userSectionLabel">
                    ÚLTIMA EVALUACIÓN
                  </span>

                  <h2>
                    Tu resultado más reciente
                  </h2>
                </div>

                <span
                  className={`userRiskBadge ${
                    lastEvaluation
                      .clasificacion_riesgo
                  }`}
                >
                  {riskLabel(
                    lastEvaluation
                      .clasificacion_riesgo
                  )}
                </span>
              </div>

              <div className="userRiskScoreArea">
                <div
                  className={`userRiskCircle ${
                    lastEvaluation
                      .clasificacion_riesgo
                  }`}
                >
                  <strong>
                    {
                      lastEvaluation
                        .puntaje_riesgo
                    }
                  </strong>

                  <span>
                    puntos
                  </span>
                </div>

                <div>
                  <p className="userResultObservation">
                    {
                      lastEvaluation
                        .observacion
                    }
                  </p>

                  <span className="userResultDate">
                    Evaluación realizada el{" "}
                    {formatDate(
                      lastEvaluation
                        .fecha_respuesta
                    )}
                  </span>
                </div>
              </div>

              <div className="userCardFooter">
                <Link
                  to="/usuario/encuesta"
                  className="userTextLink"
                >
                  Realizar nueva evaluación →
                </Link>
              </div>
            </article>

            <article className="userTipsCard">
              <span className="userSectionLabel">
                RECOMENDACIONES
              </span>

              <h2>
                Mejora tu seguridad
              </h2>

              <p>Consulta las guías disponibles y elige recursos acordes con tu nivel de riesgo.</p>
              <Link to="/usuario/guias" className="userTextLink">Ver guías de ciberseguridad →</Link>
            </article>
          </section>

          <section className="userHistoryCard">
            <div className="userCardHeading">
              <div>
                <span className="userSectionLabel">
                  TUS RESPUESTAS
                </span>
                <h2>Resumen de la última evaluación</h2>
              </div>
            </div>
            <div className="moduleGrid">
              {[
                ["Conocimiento", "nivel_conocimiento"],
                ["Reconoce phishing", "reconoce_phishing"],
                ["Antivirus", "estado_antivirus"],
                ["Reutiliza contraseñas", "reutiliza_contrasenas"],
                ["Usa nube", "usa_nube"],
                ["Plataforma", "plataforma_nube"],
                ["Conexión", "tipo_conexion"],
                ["Fallas de internet", "frecuencia_fallas_internet"],
              ].map(([label, field]) => (
                <article className="moduleCard" key={field}>
                  <span className="userSectionLabel">{label}</span>
                  <h3>{lastEvaluation[field] || "No disponible"}</h3>
                </article>
              ))}
            </div>
          </section>

          <section className="userHistoryCard">
            <div className="userCardHeading">
              <div>
                <span className="userSectionLabel">
                  HISTORIAL
                </span>

                <h2>
                  Evaluaciones recientes
                </h2>
              </div>
            </div>

            <div className="userHistoryList">
              {evaluations.map(
                (evaluation) => (
                  <div
                    className="userHistoryItem"
                    key={
                      evaluation.id_respuesta
                    }
                  >
                    <div>
                      <strong>
                        Evaluación de
                        ciberseguridad
                      </strong>

                      <span>
                        {formatDate(
                          evaluation
                            .fecha_respuesta
                        )}
                      </span>
                    </div>

                    <div className="userHistoryResult">
                      <strong>
                        {
                          evaluation
                            .puntaje_riesgo
                        }
                      </strong>

                      <span
                        className={`userRiskBadge ${
                          evaluation
                            .clasificacion_riesgo
                        }`}
                      >
                        {riskLabel(
                          evaluation
                            .clasificacion_riesgo
                        )}
                      </span>
                    </div>
                  </div>
                )
              )}
            </div>
          </section>
        </>
      )}
    </div>
  );
}
