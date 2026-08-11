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

import "../../styles/dashboard.css";

const riskData = [
  {
    name: "Bajo",
    value: 46,
    className: "riskLow",
  },
  {
    name: "Medio",
    value: 38,
    className: "riskMedium",
  },
  {
    name: "Alto",
    value: 16,
    className: "riskHigh",
  },
];

const habits = [
  {
    label: "Reutiliza contraseñas",
    percentage: 68,
  },
  {
    label: "No actualiza contraseñas",
    percentage: 57,
  },
  {
    label: "Dificultad con phishing",
    percentage: 42,
  },
  {
    label: "Antivirus desactualizado",
    percentage: 31,
  },
];

export default function DashboardPage() {
  return (
    <div className="dashboardPage">
      {/* WELCOME */}

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
            Revisa los principales indicadores
            de hábitos digitales, evaluaciones
            y nivel de riesgo de los participantes.
          </p>
        </div>

        <div className="dashboardHeroIcon">
          <FiShield />
        </div>
      </section>

      {/* METRICS */}

      <section className="statsGrid">
        <article className="statCard">
          <div className="statCardTop">
            <div className="statIcon">
              <FiUsers />
            </div>

            <span className="statTrend positive">
              +12%
            </span>
          </div>

          <strong className="statValue">
            248
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

            <span className="statTrend positive">
              +8%
            </span>
          </div>

          <strong className="statValue">
            214
          </strong>

          <span className="statLabel">
            Encuestas completadas
          </span>

          <small>
            86% de participación
          </small>
        </article>

        <article className="statCard">
          <div className="statCardTop">
            <div className="statIcon">
              <FiActivity />
            </div>
          </div>

          <strong className="statValue">
            Medio
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
            34
          </strong>

          <span className="statLabel">
            Riesgo alto
          </span>

          <small>
            Requieren mayor orientación
          </small>
        </article>
      </section>

      {/* MAIN */}

      <section className="dashboardGrid">
        {/* RISK */}

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
            >
              Ver análisis
              <FiArrowRight />
            </button>
          </div>

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
                <strong>214</strong>
                <span>evaluaciones</span>
              </div>
            </div>

            <div className="riskLegend">
              {riskData.map((item) => (
                <div
                  className="riskLegendItem"
                  key={item.name}
                >
                  <div>
                    <span
                      className={`riskDot ${item.className}`}
                    />

                    <span>{item.name}</span>
                  </div>

                  <strong>
                    {item.value}%
                  </strong>
                </div>
              ))}
            </div>
          </div>
        </article>

        {/* HABITS */}

        <article className="dashboardPanel">
          <div className="panelHeader">
            <div>
              <span className="panelEyebrow">
                Comportamiento
              </span>

              <h3>
                Hábitos que requieren atención
              </h3>

              <p>
                Prácticas inseguras identificadas
                con mayor frecuencia.
              </p>
            </div>
          </div>

          <div className="habitsList">
            {habits.map((habit) => (
              <div
                className="habitItem"
                key={habit.label}
              >
                <div className="habitHeader">
                  <span>{habit.label}</span>

                  <strong>
                    {habit.percentage}%
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
            ))}
          </div>
        </article>
      </section>

      {/* BOTTOM */}

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
            >
              Ver todas
              <FiArrowRight />
            </button>
          </div>

          <div className="recentList">
            <div className="recentItem">
              <div className="recentAvatar">
                M
              </div>

              <div className="recentInfo">
                <strong>
                  María López
                </strong>

                <span>
                  Evaluación completada
                </span>
              </div>

              <span className="riskBadge riskBadgeMedium">
                Medio
              </span>
            </div>

            <div className="recentItem">
              <div className="recentAvatar">
                C
              </div>

              <div className="recentInfo">
                <strong>
                  Carlos Martínez
                </strong>

                <span>
                  Evaluación completada
                </span>
              </div>

              <span className="riskBadge riskBadgeLow">
                Bajo
              </span>
            </div>

            <div className="recentItem">
              <div className="recentAvatar">
                A
              </div>

              <div className="recentInfo">
                <strong>
                  Andrea Reyes
                </strong>

                <span>
                  Evaluación completada
                </span>
              </div>

              <span className="riskBadge riskBadgeHigh">
                Alto
              </span>
            </div>
          </div>
        </article>

        <article className="dashboardPanel securityTip">
          <div className="securityTipIcon">
            <FiCheckCircle />
          </div>

          <span className="panelEyebrow">
            CyberLey recomienda
          </span>

          <h3>
            Promueve mejores hábitos digitales
          </h3>

          <p>
            Los datos muestran oportunidades
            de mejora principalmente en
            contraseñas, phishing y actualización
            de herramientas de seguridad.
          </p>

          <button
            type="button"
            className="secondaryAction"
          >
            Gestionar guías
            <FiArrowRight />
          </button>
        </article>
      </section>
    </div>
  );
}