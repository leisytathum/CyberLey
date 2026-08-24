import {
  useEffect,
  useMemo,
  useState,
} from "react";

import api from "../../services/api";

function formatDate(value) {
  if (!value) {
    return "—";
  }

  return new Date(value).toLocaleString(
    "es-HN",
    {
      dateStyle: "medium",
      timeStyle: "short",
    }
  );
}

function RiskBadge({ value }) {
  return (
    <span
      style={{
        textTransform: "capitalize",
        fontWeight: 700,
      }}
    >
      {value || "—"}
    </span>
  );
}

export default function SurveysPage() {
  const [rows, setRows] = useState([]);

  const [statistics, setStatistics] =
    useState({
      total: 0,
      riesgo_bajo: 0,
      riesgo_medio: 0,
      riesgo_alto: 0,
      promedio_riesgo: 0,
    });

  const [search, setSearch] =
    useState("");

  const [riskFilter, setRiskFilter] =
    useState("todos");
  const [knowledgeFilter, setKnowledgeFilter] = useState("todos");
  const [phishingFilter, setPhishingFilter] = useState("todos");

  const [selected, setSelected] =
    useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  async function loadSurveys() {
    setLoading(true);
    setError("");

    try {
      const response =
        await api.cachedGet("/encuestas");

      setRows(
        response.data.items || []
      );

      setStatistics(
        response.data.estadisticas || {
          total: 0,
          riesgo_bajo: 0,
          riesgo_medio: 0,
          riesgo_alto: 0,
          promedio_riesgo: 0,
        }
      );
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadSurveys();
  }, []);

  const filteredRows =
    useMemo(() => {
      const normalizedSearch =
        search
          .trim()
          .toLowerCase();

      return rows.filter((row) => {
        const matchesRisk =
          riskFilter === "todos" ||
          row.clasificacion_riesgo ===
            riskFilter;

        if (!matchesRisk) {
          return false;
        }
        if (knowledgeFilter !== "todos" && row.nivel_conocimiento !== knowledgeFilter) return false;
        if (phishingFilter !== "todos" && row.reconoce_phishing !== phishingFilter) return false;

        if (!normalizedSearch) {
          return true;
        }

        const searchable = [
          row.nombre_usuario,
          row.nivel_conocimiento,
          row.clasificacion_riesgo,
          row.tipo_conexion,
          row.plataforma_nube,
        ]
          .filter(Boolean)
          .join(" ")
          .toLowerCase();

        return searchable.includes(
          normalizedSearch
        );
      });
    }, [
      rows,
      search,
      riskFilter,
      knowledgeFilter,
      phishingFilter,
    ]);

  return (
    <>
      <div className="pageTitle">
        <div>
          <span className="eyebrow">
            CyberLey
          </span>

          <h1>Encuestas</h1>

          <p>
            Consulta y analiza las respuestas de
            las evaluaciones de ciberseguridad.
          </p>
        </div>
      </div>

      {error && (
        <div className="warningBox">
          {error}
        </div>
      )}

      <section
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fit, minmax(160px, 1fr))",
          gap: "16px",
          marginBottom: "20px",
        }}
      >
        <div className="panel">
          <span className="eyebrow">
            Total
          </span>

          <h2>
            {statistics.total}
          </h2>
        </div>

        <div className="panel">
          <span className="eyebrow">
            Riesgo bajo
          </span>

          <h2>
            {statistics.riesgo_bajo}
          </h2>
        </div>

        <div className="panel">
          <span className="eyebrow">
            Riesgo medio
          </span>

          <h2>
            {statistics.riesgo_medio}
          </h2>
        </div>

        <div className="panel">
          <span className="eyebrow">
            Riesgo alto
          </span>

          <h2>
            {statistics.riesgo_alto}
          </h2>
        </div>

        <div className="panel">
          <span className="eyebrow">
            Promedio
          </span>

          <h2>
            {statistics.promedio_riesgo}
          </h2>
        </div>
      </section>

      <section className="panel">
        <div
          style={{
            display: "flex",
            gap: "12px",
            flexWrap: "wrap",
            marginBottom: "20px",
          }}
        >
          <input
            type="text"
            placeholder="Buscar por usuario, riesgo, conexión..."
            value={search}
            onChange={(event) =>
              setSearch(
                event.target.value
              )
            }
            style={{
              flex: "1 1 260px",
            }}
          />

          <select
            value={riskFilter}
            onChange={(event) =>
              setRiskFilter(
                event.target.value
              )
            }
          >
            <option value="todos">
              Todos los riesgos
            </option>

            <option value="bajo">
              Riesgo bajo
            </option>

            <option value="medio">
              Riesgo medio
            </option>

            <option value="alto">
              Riesgo alto
            </option>
          </select>
          <select value={knowledgeFilter} onChange={event=>setKnowledgeFilter(event.target.value)}>
            <option value="todos">Todo conocimiento</option>
            {[...new Set(rows.map(row=>row.nivel_conocimiento).filter(Boolean))].map(value=><option key={value}>{value}</option>)}
          </select>
          <select value={phishingFilter} onChange={event=>setPhishingFilter(event.target.value)}>
            <option value="todos">Todo reconocimiento de phishing</option>
            {[...new Set(rows.map(row=>row.reconoce_phishing).filter(Boolean))].map(value=><option key={value}>{value}</option>)}
          </select>
        </div>

        {loading ? (
          <div className="moduleSkeleton" aria-label="Actualizando encuestas">
            <span /><span /><span />
          </div>
        ) : filteredRows.length === 0 ? (
          <p>
            No hay encuestas que coincidan
            con los filtros.
          </p>
        ) : (
          <div
            style={{
              overflowX: "auto",
            }}
          >
            <table
              style={{
                width: "100%",
                borderCollapse:
                  "collapse",
              }}
            >
              <thead>
                <tr>
                  <th>Usuario</th>
                  <th>Fecha</th>
                  <th>Conocimiento</th>
                  <th>Ciudad</th>
                  <th>Puntaje</th>
                  <th>Riesgo</th>
                  <th></th>
                </tr>
              </thead>

              <tbody>
                {filteredRows.map(
                  (row) => (
                    <tr
                      key={
                        row.id_respuesta
                      }
                    >
                      <td>
                        {row.nombre_usuario}
                      </td>

                      <td>
                        {formatDate(
                          row.fecha_respuesta
                        )}
                      </td>

                      <td>
                        {
                          row.nivel_conocimiento
                        }
                      </td>
                      <td>{row.ciudad || "—"}</td>

                      <td>
                        {
                          row.puntaje_riesgo
                        }
                      </td>

                      <td>
                        <RiskBadge
                          value={
                            row.clasificacion_riesgo
                          }
                        />
                      </td>

                      <td>
                        <button
                          type="button"
                          onClick={() =>
                            setSelected(
                              row
                            )
                          }
                        >
                          Ver detalle
                        </button>
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {selected && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background:
              "rgba(0, 0, 0, .55)",
            display: "grid",
            placeItems: "center",
            padding: "20px",
            zIndex: 1000,
          }}
          onClick={(event) => {
            if (
              event.target ===
              event.currentTarget
            ) {
              setSelected(null);
            }
          }}
        >
          <section
            className="panel"
            style={{
              width: "min(720px, 100%)",
              maxHeight: "85vh",
              overflowY: "auto",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent:
                  "space-between",
                gap: "16px",
                alignItems: "start",
              }}
            >
              <div>
                <span className="eyebrow">
                  Detalle de evaluación
                </span>

                <h2>
                  {
                    selected.nombre_usuario
                  }
                </h2>

                <p>
                  {formatDate(
                    selected.fecha_respuesta
                  )}
                </p>
              </div>

              <button
                type="button"
                onClick={() =>
                  setSelected(null)
                }
              >
                Cerrar
              </button>
            </div>

            <hr />

            <div
              style={{
                display: "grid",
                gap: "14px",
              }}
            >
              <p>
                <strong>Ciudad:</strong>{" "}{selected.ciudad || "No disponible"}
              </p>
              <p>
                <strong>Nivel educativo:</strong>{" "}{selected.nivel_educativo || "No disponible"}
              </p>
              <p>
                <strong>
                  Nivel de conocimiento:
                </strong>{" "}
                {
                  selected.nivel_conocimiento
                }
              </p>

              <p>
                <strong>
                  Manejo de ciberseguridad:
                </strong>{" "}
                {
                  selected.manejo_ciberseguridad
                }
                /5
              </p>

              <p>
                <strong>
                  Reconoce phishing:
                </strong>{" "}
                {
                  selected.reconoce_phishing
                }
              </p>

              <p>
                <strong>
                  Herramientas de seguridad:
                </strong>{" "}
                {
                  selected.identifica_herramientas_seguridad
                }
              </p>

              <p>
                <strong>
                  Antivirus:
                </strong>{" "}
                {
                  selected.estado_antivirus
                }
              </p>

              <p>
                <strong>
                  Conexión:
                </strong>{" "}
                {
                  selected.tipo_conexion
                }
              </p>

              <p>
                <strong>
                  Estabilidad:
                </strong>{" "}
                {
                  selected.estabilidad_conexion
                }
                /5
              </p>

              <p>
                <strong>
                  Cambio de contraseñas:
                </strong>{" "}
                {
                  selected.cambio_contrasenas_anual
                }
              </p>

              <p>
                <strong>
                  Reutiliza contraseñas:
                </strong>{" "}
                {
                  selected.reutiliza_contrasenas
                }
              </p>

              <p>
                <strong>
                  Puntaje:
                </strong>{" "}
                {
                  selected.puntaje_riesgo
                }
              </p>

              <p>
                <strong>
                  Clasificación:
                </strong>{" "}
                <RiskBadge
                  value={
                    selected.clasificacion_riesgo
                  }
                />
              </p>

              <p>
                <strong>
                  Observación:
                </strong>
              </p>

              <p>
                {selected.observacion}
              </p>
            </div>
          </section>
        </div>
      )}
    </>
  );
}
