import { useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../../services/api";

const initialForm = {
  usa_nube: "Sí",
  plataforma_nube: "Google Drive",
  contenido_nube: "Documentos personales",

  nivel_conocimiento: "Medio",
  manejo_ciberseguridad: 3,
  frecuencia_info_seguridad: "A veces",
  reconoce_phishing: "A veces",
  identifica_herramientas_seguridad: "A veces",
  estado_antivirus: "No sé",

  tipo_conexion: "Wi-Fi",
  estabilidad_conexion: 3,
  frecuencia_fallas_internet: "A veces",

  cambio_contrasenas_anual: "Una vez al año",
  reutiliza_contrasenas: "A veces",
  importancia_actualizar_contrasenas: 3,
};

function SelectField({
  label,
  name,
  value,
  onChange,
  options,
  full = false,
}) {
  return (
    <div
      className={`surveyField ${
        full ? "surveyFieldFull" : ""
      }`}
    >
      <label htmlFor={name}>
        {label}
      </label>

      <select
        id={name}
        name={name}
        value={value}
        onChange={onChange}
      >
        {options.map((option) => (
          <option
            key={option}
            value={option}
          >
            {option}
          </option>
        ))}
      </select>
    </div>
  );
}

function ScaleField({
  label,
  name,
  value,
  onChange,
  full = false,
}) {
  return (
    <div
      className={`surveyField ${
        full ? "surveyFieldFull" : ""
      }`}
    >
      <label htmlFor={name}>
        {label}
      </label>

      <select
        id={name}
        name={name}
        value={value}
        onChange={onChange}
      >
        {[1, 2, 3, 4, 5].map(
          (number) => (
            <option
              key={number}
              value={number}
            >
              {number}
            </option>
          )
        )}
      </select>
    </div>
  );
}

export default function SurveyPage() {
  const navigate = useNavigate();

  const [form, setForm] =
    useState(initialForm);

  const [result, setResult] =
    useState(null);

  const [error, setError] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  function handleChange(event) {
    const {
      name,
      value,
    } = event.target;

    const numericFields = [
      "manejo_ciberseguridad",
      "estabilidad_conexion",
      "importancia_actualizar_contrasenas",
    ];

    setForm((previous) => ({
      ...previous,

      [name]:
        numericFields.includes(name)
          ? Number(value)
          : value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setLoading(true);
    setError("");

    try {
      const response =
        await api.post(
          "/riesgo/evaluar",
          form
        );

      setResult(response.data);
    } catch (requestError) {
      setError(
        requestError.message ||
          "No se pudo guardar la evaluación."
      );
    } finally {
      setLoading(false);
    }
  }

  function resetSurvey() {
    setForm(initialForm);
    setResult(null);
    setError("");
  }

  function getRiskClass(value) {
    if (value === "alto") return "riskHigh";
    if (value === "medio") return "riskMedium";
    return "riskLow";
  }

  function getRiskLabel(value) {
    if (value === "alto") return "Riesgo alto";
    if (value === "medio") return "Riesgo medio";
    return "Riesgo bajo";
  }

  if (result) {
    const riskClass = getRiskClass(
      result.clasificacion
    );

    return (
      <section className="dashboardPanel surveyResultPanel">
        <div className="surveyResultTop">
          <div>
            <span className="panelEyebrow">
              EVALUACIÓN COMPLETADA
            </span>

            <h2 className="surveyResultTitle">
              Tu resultado de seguridad digital
            </h2>

            <p className="surveyResultSubtitle">
              Analizamos tus hábitos actuales
              para estimar tu nivel de riesgo y
              darte una recomendación clara.
            </p>
          </div>
        </div>

        <div className="surveyResultCards">
          <article className="surveyMetricCard">
            <span className="surveyMetricLabel">
              Puntaje obtenido
            </span>

            <strong className="surveyMetricValue">
              {result.puntaje}
            </strong>

            <small className="surveyMetricHelper">
              puntos de riesgo
            </small>
          </article>

          <article
            className={`surveyMetricCard surveyMetricCardAccent ${riskClass}`}
          >
            <span className="surveyMetricLabel">
              Clasificación
            </span>

            <strong className="surveyMetricRisk">
              {getRiskLabel(
                result.clasificacion
              )}
            </strong>

            <small className="surveyMetricHelper">
              según tus respuestas
            </small>
          </article>
        </div>

        <section className="surveyObservationCard">
          <span className="panelEyebrow">
            RECOMENDACIÓN
          </span>

          <p className="surveyObservationText">
            {result.observacion}
          </p>
        </section>

        <section className="surveyNextStepCard">
          <div>
            <span className="panelEyebrow">
              SIGUIENTE PASO
            </span>

            <h3>
              Sigue fortaleciendo tu seguridad
              digital
            </h3>

            <p>
              Puedes realizar una nueva
              evaluación cuando quieras para
              comparar cambios en tus hábitos y
              revisar tu progreso.
            </p>
          </div>
        </section>

        <div className="surveyActions surveyActionsBetween">
          <button
            type="button"
            className="surveySecondaryButton"
            onClick={() => navigate("/usuario")}
          >
            Volver al inicio
          </button>

          <button
            type="button"
            className="surveySubmit"
            onClick={resetSurvey}
          >
            Realizar otra evaluación
          </button>
        </div>
      </section>
    );
  }

  return (
    <form
      className="dashboardPanel surveyForm"
      onSubmit={handleSubmit}
    >
      <section className="surveyIntro">
        <span className="panelEyebrow">
          EVALUACIÓN CYBERLEY
        </span>

        <h2>
          Encuesta de hábitos digitales y
          ciberseguridad
        </h2>

        <p>
          Responde según tus hábitos actuales.
          La información se utilizará para
          calcular tu nivel de riesgo digital.
        </p>
      </section>

      <section className="surveySection">
        <div className="surveySectionHeader">
          <span className="panelEyebrow">
            SECCIÓN 1
          </span>

          <h2>
            Uso de servicios digitales
          </h2>

          <p>
            Cuéntanos cómo utilizas servicios
            y plataformas de almacenamiento.
          </p>
        </div>

        <div className="surveyFieldsGrid">
          <SelectField
            label="¿Utilizas almacenamiento en la nube?"
            name="usa_nube"
            value={form.usa_nube}
            onChange={handleChange}
            options={[
              "Sí",
              "No",
            ]}
          />

          {form.usa_nube === "Sí" && (
            <>
              <SelectField
                label="¿Qué plataforma utilizas principalmente?"
                name="plataforma_nube"
                value={
                  form.plataforma_nube
                }
                onChange={
                  handleChange
                }
                options={[
                  "Google Drive",
                  "OneDrive",
                  "Dropbox",
                  "iCloud",
                  "Mega",
                  "Otra",
                ]}
              />

              <SelectField
                label="¿Qué contenido guardas principalmente?"
                name="contenido_nube"
                value={
                  form.contenido_nube
                }
                onChange={
                  handleChange
                }
                options={[
                  "Documentos personales",
                  "Fotos o videos",
                  "Archivos académicos",
                  "Archivos laborales",
                  "Contraseñas o información sensible",
                  "Otro",
                ]}
                full
              />
            </>
          )}
        </div>
      </section>

      <section className="surveySection">
        <div className="surveySectionHeader">
          <span className="panelEyebrow">
            SECCIÓN 2
          </span>

          <h2>
            Conocimientos y seguridad
          </h2>

          <p>
            Estas preguntas evalúan qué tan
            familiarizado estás con prácticas
            de ciberseguridad.
          </p>
        </div>

        <div className="surveyFieldsGrid">
          <SelectField
            label="¿Cuál consideras que es tu nivel de conocimiento sobre ciberseguridad?"
            name="nivel_conocimiento"
            value={
              form.nivel_conocimiento
            }
            onChange={
              handleChange
            }
            options={[
              "Bajo",
              "Medio",
              "Alto",
            ]}
          />

          <ScaleField
            label="¿Cómo calificas tu manejo de temas de ciberseguridad? (1–5)"
            name="manejo_ciberseguridad"
            value={
              form.manejo_ciberseguridad
            }
            onChange={
              handleChange
            }
          />

          <SelectField
            label="¿Con qué frecuencia buscas información sobre seguridad digital?"
            name="frecuencia_info_seguridad"
            value={
              form.frecuencia_info_seguridad
            }
            onChange={
              handleChange
            }
            options={[
              "Nunca",
              "Rara vez",
              "A veces",
              "Frecuentemente",
            ]}
          />

          <SelectField
            label="¿Reconoces intentos de phishing?"
            name="reconoce_phishing"
            value={
              form.reconoce_phishing
            }
            onChange={
              handleChange
            }
            options={[
              "No",
              "A veces",
              "Sí",
            ]}
          />

          <SelectField
            label="¿Identificas herramientas de seguridad digital?"
            name="identifica_herramientas_seguridad"
            value={
              form.identifica_herramientas_seguridad
            }
            onChange={
              handleChange
            }
            options={[
              "No",
              "A veces",
              "Sí",
            ]}
          />

          <SelectField
            label="¿Cuál es el estado de tu antivirus?"
            name="estado_antivirus"
            value={
              form.estado_antivirus
            }
            onChange={
              handleChange
            }
            options={[
              "No tengo antivirus",
              "Tengo antivirus, pero no está actualizado",
              "No sé",
              "Tengo antivirus actualizado",
            ]}
          />
        </div>
      </section>

      <section className="surveySection">
        <div className="surveySectionHeader">
          <span className="panelEyebrow">
            SECCIÓN 3
          </span>

          <h2>
            Conexión a internet
          </h2>

          <p>
            Cuéntanos cómo es tu conexión y qué
            tan estable suele ser.
          </p>
        </div>

        <div className="surveyFieldsGrid">
          <SelectField
            label="¿Cuál es tu tipo de conexión principal?"
            name="tipo_conexion"
            value={
              form.tipo_conexion
            }
            onChange={
              handleChange
            }
            options={[
              "Wi-Fi",
              "Router",
              "Datos móviles",
              "Fibra óptica",
              "ADSL",
              "Satelital",
              "Otro",
            ]}
          />

          <ScaleField
            label="¿Qué tan estable consideras tu conexión? (1–5)"
            name="estabilidad_conexion"
            value={
              form.estabilidad_conexion
            }
            onChange={
              handleChange
            }
          />

          <SelectField
            label="¿Con qué frecuencia tienes fallas de internet?"
            name="frecuencia_fallas_internet"
            value={
              form.frecuencia_fallas_internet
            }
            onChange={
              handleChange
            }
            options={[
              "Nunca",
              "Rara vez",
              "A veces",
              "Frecuentemente",
            ]}
            full
          />
        </div>
      </section>

      <section className="surveySection">
        <div className="surveySectionHeader">
          <span className="panelEyebrow">
            SECCIÓN 4
          </span>

          <h2>
            Contraseñas y protección
          </h2>

          <p>
            Estas preguntas permiten identificar
            hábitos relacionados con el manejo
            de contraseñas.
          </p>
        </div>

        <div className="surveyFieldsGrid">
          <SelectField
            label="¿Con qué frecuencia cambias tus contraseñas?"
            name="cambio_contrasenas_anual"
            value={
              form.cambio_contrasenas_anual
            }
            onChange={
              handleChange
            }
            options={[
              "Nunca",
              "Una vez al año",
              "Cada 6 meses",
              "Cada 3 meses o menos",
            ]}
          />

          <SelectField
            label="¿Reutilizas la misma contraseña en diferentes servicios?"
            name="reutiliza_contrasenas"
            value={
              form.reutiliza_contrasenas
            }
            onChange={
              handleChange
            }
            options={[
              "Sí",
              "A veces",
              "No",
            ]}
          />

          <ScaleField
            label="¿Qué tan importante consideras actualizar las contraseñas? (1–5)"
            name="importancia_actualizar_contrasenas"
            value={
              form.importancia_actualizar_contrasenas
            }
            onChange={
              handleChange
            }
            full
          />
        </div>
      </section>

      {error && (
        <div className="errorBox">
          {error}
        </div>
      )}

      <div className="surveyActions">
        <button
          type="submit"
          className="surveySubmit"
          disabled={loading}
        >
          {loading
            ? "Calculando..."
            : "Calcular mi riesgo"}
        </button>
      </div>
    </form>
  );
}