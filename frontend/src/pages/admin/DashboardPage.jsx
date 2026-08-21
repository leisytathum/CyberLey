import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  FiActivity,
  FiAlertTriangle,
  FiArrowRight,
  FiCheckCircle,
  FiFileText,
  FiShield,
  FiUsers,
} from "react-icons/fi";

import {
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

import { useNavigate } from "react-router-dom";

import api from "../../services/api";

import "../../styles/dashboard.css";

const DASHBOARD_CACHE_KEY =
  "cyberley_admin_dashboard";

const DASHBOARD_CACHE_TIME =
  60 * 1000;

const emptyData = {
  participantes: 0,
  encuestas: 0,
  participacion: 0,
  nivel_predominante: "Sin datos",
  riesgo_alto: 0,

  distribucion_riesgo: {
    bajo: {
      cantidad: 0,
      porcentaje: 0,
    },
    medio: {
      cantidad: 0,
      porcentaje: 0,
    },
    alto: {
      cantidad: 0,
      porcentaje: 0,
    },
  },

  habitos: {
    reutiliza_contrasenas: 0,
    no_actualiza_contrasenas: 0,
    dificultad_phishing: 0,
    antivirus_desactualizado: 0,
  },

  evaluaciones_recientes: [],
};

function readDashboardCache() {
  try {
    const saved =
      sessionStorage.getItem(
        DASHBOARD_CACHE_KEY
      );

    if (!saved) {
      return null;
    }

    return JSON.parse(saved);
  } catch {
    return null;
  }
}

function saveDashboardCache(data) {
  try {
    sessionStorage.setItem(
      DASHBOARD_CACHE_KEY,
      JSON.stringify({
        data,
        savedAt: Date.now(),
      })
    );
  } catch {
    // Si el navegador bloquea sessionStorage,
    // el dashboard sigue funcionando.
  }
}

function getRiskClass(value) {
  if (value === "alto") {
    return "riskBadgeHigh";
  }

  if (value === "medio") {
    return "riskBadgeMedium";
  }

  return "riskBadgeLow";
}

function buildDashboardData(responseData) {
  return {
    ...emptyData,
    ...responseData,

    distribucion_riesgo: {
      ...emptyData.distribucion_riesgo,
      ...responseData?.distribucion_riesgo,
    },

    habitos: {
      ...emptyData.habitos,
      ...responseData?.habitos,
    },

    evaluaciones_recientes:
      responseData
        ?.evaluaciones_recientes || [],
  };
}

export default function DashboardPage() {
  const navigate = useNavigate();

  const cachedDashboard =
    readDashboardCache();

  const [data, setData] =
    useState(
      cachedDashboard?.data ||
        emptyData
    );

  const [loading, setLoading] =
    useState(
      !cachedDashboard?.data
    );

  const [error, setError] =
    useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadDashboard() {
      const cached =
        readDashboardCache();

      const cacheIsFresh =
        cached?.data &&
        Date.now() -
          cached.savedAt <
          DASHBOARD_CACHE_TIME;

      /*
       * Si el caché todavía es reciente,
       * no hacemos otra petición.
       */
      if (cacheIsFresh) {
        setData(cached.data);
        setLoading(false);
        return;
      }

      /*
       * Si existe caché pero ya está viejo,
       * lo mostramos mientras actualizamos
       * silenciosamente.
       */
      if (cached?.data) {
        setData(cached.data);
        setLoading(false);
      } else {
        setLoading(true);
      }

      setError("");

      try {
        const response =
          await api.get(
            "/dashboard/summary"
          );

        if (cancelled) {
          return;
        }

        const newData =
          buildDashboardData(
            response.data
          );

        setData(newData);

        saveDashboardCache(
          newData
        );
      } catch (requestError) {
        if (cancelled) {
          return;
        }

        /*
         * Si ya tenemos datos guardados,
         * no reemplazamos todo el dashboard
         * por un error.
         */
        if (!cached?.data) {
          setError(
            requestError.message ||
              "No se pudo cargar el dashboard."
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadDashboard();

    return () => {
      cancelled = true;
    };
  }, []);

  const riskData =
    useMemo(
      () => [
        {
          name: "Bajo",
          value:
            data.distribucion_riesgo
              .bajo.porcentaje,
          className: "riskLow",
        },
        {
          name: "Medio",
          value:
            data.distribucion_riesgo
              .medio.porcentaje,
          className: "riskMedium",
        },
        {
          name: "Alto",
          value:
            data.distribucion_riesgo
              .alto.porcentaje,
          className: "riskHigh",
        },
      ],
      [data]
    );

  const habits =
    useMemo(
      () => [
        {
          label:
            "Reutiliza contraseñas",
          percentage:
            data.habitos
              .reutiliza_contrasenas,
        },
        {
          label:
            "No actualiza contraseñas",
          percentage:
            data.habitos
              .no_actualiza_contrasenas,
        },
        {
          label:
            "Dificultad con phishing",
          percentage:
            data.habitos
              .dificultad_phishing,
        },
        {
          label:
            "Antivirus desactualizado",
          percentage:
            data.habitos
              .antivirus_desactualizado,
        },
      ],
      [data]
    );

  if (loading) {
    return (
      <div className="dashboardPage">
        <section className="dashboardPanel">
          <span className="panelEyebrow">
            CyberLey
          </span>

          <h3>
            Cargando información...
          </h3>

          <p>
            Estamos consultando los datos
            del sistema.
          </p>
        </section>
      </div>
    );
  }

  return (
    <div className="dashboardPage">
      {error && (
        <div className="warningBox">
          {error}
        </div>
      )}

      <section className="dashboardHero">
        <div className="dashboardHeroContent">
          <span className="dashboardEyebrow">
            Resumen general
          </span>

          <h2>
            Conoce lo que está ocurriendo
            en CyberLey
          </h2>

          <p>
            Revisa los principales
            indicadores de hábitos
            digitales, evaluaciones y
            nivel de riesgo de los
            participantes.
          </p>
        </div>

        <div className="dashboardHeroIcon">
          <FiShield />
        </div>
      </section>

      <section className="statsGrid">
        <article className="statCard">
          <div className="statCardTop">
            <div className="statIcon">
              <FiUsers />
            </div>
          </div>

          <strong className="statValue">
            {data.participantes}
          </strong>

          <span className="statLabel">
            Participantes
          </span>

          <small>
            Registrados en el sistema
          </small>
        </article>

        <article className="statCard">
          <div className="statCardTop">
            <div className="statIcon">
              <FiFileText />
            </div>
          </div>

          <strong className="statValue">
            {data.encuestas}
          </strong>

          <span className="statLabel">
            Encuestas completadas
          </span>

          <small>
            {data.participacion}% de
            participación
          </small>
        </article>

        <article className="statCard">
          <div className="statCardTop">
            <div className="statIcon">
              <FiActivity />
            </div>
          </div>

          <strong className="statValue">
            {data.nivel_predominante}
          </strong>

          <span className="statLabel">
            Nivel predominante
          </span>

          <small>
            Según las evaluaciones
          </small>
        </article>

        <article className="statCard statCardAttention">
          <div className="statCardTop">
            <div className="statIcon">
              <FiAlertTriangle />
            </div>
          </div>

          <strong className="statValue">
            {data.riesgo_alto}
          </strong>

          <span className="statLabel">
            Riesgo alto
          </span>

          <small>
            Requieren mayor orientación
          </small>
        </article>
      </section>

      <section className="dashboardGrid">
        <article className="dashboardPanel">
          <div className="panelHeader">
            <div>
              <span className="panelEyebrow">
                Análisis
              </span>

              <h3>
                Distribución de riesgo
              </h3>

              <p>
                Clasificación actual de las
                evaluaciones realizadas.
              </p>
            </div>

            <button
              type="button"
              className="panelAction"
              onClick={() =>
                navigate(
                  "/admin/riesgo"
                )
              }
            >
              Ver análisis
              <FiArrowRight />
            </button>
          </div>

          {data.encuestas === 0 ? (
            <div
              style={{
                padding: "45px 20px",
                textAlign: "center",
              }}
            >
              <strong>
                Aún no hay evaluaciones
              </strong>

              <p>
                Cuando los usuarios
                completen evaluaciones,
                aquí aparecerá la
                distribución de riesgo.
              </p>
            </div>
          ) : (
            <div className="riskContent">
              <div className="riskChart">
                <ResponsiveContainer
                  width="100%"
                  height={240}
                >
                  <PieChart>
                    <Pie
                      data={riskData}
                      dataKey="value"
                      innerRadius={70}
                      outerRadius={95}
                      paddingAngle={4}
                    >
                      <Cell
                        className="chartRiskLow"
                      />

                      <Cell
                        className="chartRiskMedium"
                      />

                      <Cell
                        className="chartRiskHigh"
                      />
                    </Pie>

                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>

                <div className="riskChartCenter">
                  <strong>
                    {data.encuestas}
                  </strong>

                  <span>
                    evaluaciones
                  </span>
                </div>
              </div>

              <div className="riskLegend">
                {riskData.map(
                  (item) => (
                    <div
                      className="riskLegendItem"
                      key={item.name}
                    >
                      <div>
                        <span
                          className={`riskDot ${item.className}`}
                        />

                        <span>
                          {item.name}
                        </span>
                      </div>

                      <strong>
                        {item.value}%
                      </strong>
                    </div>
                  )
                )}
              </div>
            </div>
          )}
        </article>

        <article className="dashboardPanel">
          <div className="panelHeader">
            <div>
              <span className="panelEyebrow">
                Comportamiento
              </span>

              <h3>
                Hábitos que requieren
                atención
              </h3>

              <p>
                Prácticas inseguras
                identificadas con mayor
                frecuencia.
              </p>
            </div>
          </div>

          {data.encuestas === 0 ? (
            <div
              style={{
                padding: "45px 20px",
                textAlign: "center",
              }}
            >
              <strong>
                Sin información todavía
              </strong>

              <p>
                Los hábitos aparecerán
                cuando existan
                evaluaciones.
              </p>
            </div>
          ) : (
            <div className="habitsList">
              {habits.map(
                (habit) => (
                  <div
                    className="habitItem"
                    key={habit.label}
                  >
                    <div className="habitHeader">
                      <span>
                        {habit.label}
                      </span>

                      <strong>
                        {
                          habit.percentage
                        }
                        %
                      </strong>
                    </div>

                    <div className="habitTrack">
                      <span
                        style={{
                          width: `${habit.percentage}%`,
                        }}
                      />
                    </div>
                  </div>
                )
              )}
            </div>
          )}
        </article>
      </section>

      <section className="dashboardBottomGrid">
        <article className="dashboardPanel">
          <div className="panelHeader">
            <div>
              <span className="panelEyebrow">
                Actividad
              </span>

              <h3>
                Evaluaciones recientes
              </h3>
            </div>

            <button
              type="button"
              className="panelAction"
              onClick={() =>
                navigate(
                  "/admin/encuestas"
                )
              }
            >
              Ver todas
              <FiArrowRight />
            </button>
          </div>

          {data.evaluaciones_recientes
            .length === 0 ? (
            <div
              style={{
                padding: "35px 10px",
              }}
            >
              <strong>
                No hay evaluaciones
                recientes.
              </strong>

              <p>
                Las evaluaciones nuevas
                aparecerán aquí.
              </p>
            </div>
          ) : (
            <div className="recentList">
              {data.evaluaciones_recientes.map(
                (evaluation, index) => (
                  <div
                    className="recentItem"
                    key={
                      evaluation.id ||
                      index
                    }
                  >
                    <div className="recentAvatar">
                      {evaluation.nombre
                        ?.charAt(0)
                        ?.toUpperCase() ||
                        "U"}
                    </div>

                    <div className="recentInfo">
                      <strong>
                        {
                          evaluation.nombre
                        }
                      </strong>

                      <span>
                        Evaluación completada
                      </span>
                    </div>

                    <span
                      className={`riskBadge ${getRiskClass(
                        evaluation.clasificacion
                      )}`}
                    >
                      {evaluation
                        .clasificacion ||
                        "Sin clasificar"}
                    </span>
                  </div>
                )
              )}
            </div>
          )}
        </article>

        <article className="dashboardPanel securityTip">
          <div className="securityTipIcon">
            <FiCheckCircle />
          </div>

          <span className="panelEyebrow">
            CyberLey recomienda
          </span>

          <h3>
            Promueve mejores hábitos
            digitales
          </h3>

          <p>
            Utiliza los resultados reales
            de las evaluaciones para
            identificar las áreas donde
            los usuarios requieren mayor
            orientación.
          </p>

          <button
            type="button"
            className="secondaryAction"
            onClick={() =>
              navigate(
                "/admin/guias"
              )
            }
          >
            Gestionar guías
            <FiArrowRight />
          </button>
        </article>
      </section>
    </div>
  );
}