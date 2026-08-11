import { useState } from "react";
import {
  FiEye,
  FiEyeOff,
  FiLock,
  FiMail,
  FiUser,
  FiMapPin,
} from "react-icons/fi";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";

import PasswordStrength from "../../components/forms/PasswordStrength";
import ThemeToggle from "../../components/common/ThemeToggle";

import {
  hondurasLocations,
} from "../../data/hondurasLocations";

import {
  isStrongPassword,
  isValidEmail,
  validateAge,
} from "../../utils/validators";

import {
  getFriendlyError,
} from "../../utils/errorMessages";

import { supabase } from "../../services/supabaseClient";

export default function RegisterPage() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    nombre: "",
    edad: "",
    genero: "",
    departamento: "Atlántida",
    ciudad: "",
    nivel_educativo: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const [showPassword, setShowPassword] =
    useState(false);

  const [showConfirmPassword, setShowConfirmPassword] =
    useState(false);

  const change = (event) => {
    const { name, value } = event.target;

    setForm((current) => ({
      ...current,
      [name]: value,
    }));

    setErrors((current) => ({
      ...current,
      [name]: "",
      general: "",
    }));
  };

  const changeDepartment = (event) => {
    const department = event.target.value;

    setForm((current) => ({
      ...current,
      departamento: department,
      ciudad: "",
    }));

    setErrors((current) => ({
      ...current,
      departamento: "",
      ciudad: "",
    }));
  };

  const validate = () => {
    const nextErrors = {};

    if (form.nombre.trim().length < 3) {
      nextErrors.nombre =
        "Ingresa tu nombre completo.";
    }

    const ageError = validateAge(form.edad);

    if (ageError) {
      nextErrors.edad = ageError;
    }

    if (!form.genero) {
      nextErrors.genero =
        "Selecciona tu género.";
    }

    if (!form.departamento) {
      nextErrors.departamento =
        "Selecciona tu departamento.";
    }

    if (!form.ciudad) {
      nextErrors.ciudad =
        "Selecciona tu ciudad.";
    }

    if (!form.nivel_educativo) {
      nextErrors.nivel_educativo =
        "Selecciona tu nivel educativo.";
    }

    if (!form.email.trim()) {
      nextErrors.email =
        "Ingresa tu correo electrónico.";
    } else if (!isValidEmail(form.email)) {
      nextErrors.email =
        "Ingresa un correo electrónico válido.";
    }

    if (!form.password) {
      nextErrors.password =
        "Ingresa una contraseña.";
    } else if (!isStrongPassword(form.password)) {
      nextErrors.password =
        "La contraseña aún no cumple todos los requisitos.";
    }

    if (!form.confirmPassword) {
      nextErrors.confirmPassword =
        "Confirma tu contraseña.";
    } else if (
      form.password !== form.confirmPassword
    ) {
      nextErrors.confirmPassword =
        "Las contraseñas no coinciden.";
    }

    setErrors(nextErrors);

    return Object.keys(nextErrors).length === 0;
  };

  async function submit(event) {
    event.preventDefault();

    if (!validate()) {
      toast.error(
        "Revisa los campos marcados antes de continuar."
      );
      return;
    }

    try {
      setLoading(true);

      const {
        data,
        error,
      } = await supabase.auth.signUp({
        email: form.email
          .trim()
          .toLowerCase(),

        password: form.password,

        options: {
          data: {
            nombre_completo: form.nombre.trim(),
            edad: Number(form.edad),
            genero: form.genero,
            departamento: form.departamento,
            ciudad: form.ciudad,
            nivel_educativo:
              form.nivel_educativo,
          },
        },
      });

      if (error) {
        throw error;
      }

      /*
       * Si Supabase devuelve sesión inmediatamente,
       * significa que el proyecto no exige confirmación
       * de correo.
       */
      if (data.session) {
        toast.success(
          "Cuenta creada correctamente. Ya puedes iniciar sesión."
        );
      } else {
        toast.success(
          "Cuenta creada. Revisa tu correo para confirmar el registro."
        );
      }

      setTimeout(() => {
        navigate("/login", {
          replace: true,
        });
      }, 1200);
    } catch (error) {
      console.error(
        "[CyberLey registro]",
        error
      );

      const friendlyMessage =
        getFriendlyError(error);

      setErrors({
        general: friendlyMessage,
      });

      toast.error(friendlyMessage);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="authPage">
      <div className="authTheme">
        <ThemeToggle />
      </div>

      <section className="authIntro">
        <div className="authBrand">
          <img
            src="/logo.png"
            alt="CyberLey"
            className="authLogo"
          />

          <span>CyberLey</span>
        </div>

        <div className="authHeroContent">
          <span className="authBadge">
            Seguridad digital desde el inicio
          </span>

          <h1>
            Conoce tus hábitos.
            <span>
              {" "}
              Fortalece tu seguridad.
            </span>
          </h1>

          <p>
            Crea tu cuenta para evaluar tus
            prácticas digitales, identificar
            riesgos y acceder a recursos de
            ciberseguridad.
          </p>
        </div>

        <div className="authDecoration authDecorationOne" />
        <div className="authDecoration authDecorationTwo" />
      </section>

      <main className="authFormArea">
        <form
          className="authCard authCardLarge"
          onSubmit={submit}
          noValidate
        >
          <div className="authCardHeader">
            <span className="eyebrow">
              Crear cuenta
            </span>

            <h2>Únete a CyberLey</h2>

            <p>
              Completa tus datos para comenzar.
            </p>
          </div>

          {/* NOMBRE */}

          <div className="fieldGroup">
            <label htmlFor="nombre">
              Nombre completo
            </label>

            <div
              className={`inputWrapper ${
                errors.nombre
                  ? "inputError"
                  : ""
              }`}
            >
              <FiUser />

              <input
                id="nombre"
                name="nombre"
                type="text"
                placeholder="Ej. Leisy Tathum"
                value={form.nombre}
                onChange={change}
              />
            </div>

            {errors.nombre && (
              <span className="fieldError">
                {errors.nombre}
              </span>
            )}
          </div>

          {/* EDAD */}

          <div className="fieldGroup">
            <label htmlFor="edad">
              Edad
            </label>

            <input
              id="edad"
              name="edad"
              type="number"
              min="10"
              max="100"
              placeholder="Ej. 20"
              value={form.edad}
              onChange={change}
              className={
                errors.edad
                  ? "standaloneInput inputError"
                  : "standaloneInput"
              }
            />

            {errors.edad && (
              <span className="fieldError">
                {errors.edad}
              </span>
            )}

            <span className="fieldHint">
              Edad permitida: entre 10 y 100 años.
            </span>
          </div>

          {/* GÉNERO */}

          <div className="fieldGroup">
            <label htmlFor="genero">
              Género
            </label>

            <select
              id="genero"
              name="genero"
              value={form.genero}
              onChange={change}
              className={
                errors.genero
                  ? "standaloneInput inputError"
                  : "standaloneInput"
              }
            >
              <option value="">
                Selecciona una opción
              </option>

              <option value="Femenino">
                Femenino
              </option>

              <option value="Masculino">
                Masculino
              </option>

              <option value="Prefiero no decirlo">
                Prefiero no decirlo
              </option>

              <option value="Otro">
                Otro
              </option>
            </select>

            {errors.genero && (
              <span className="fieldError">
                {errors.genero}
              </span>
            )}
          </div>

          {/* DEPARTAMENTO */}

          <div className="fieldGroup">
            <label htmlFor="departamento">
              Departamento
            </label>

            <div
              className={`inputWrapper ${
                errors.departamento
                  ? "inputError"
                  : ""
              }`}
            >
              <FiMapPin />

              <select
                id="departamento"
                name="departamento"
                value={form.departamento}
                onChange={changeDepartment}
              >
                <option value="">
                  Selecciona un departamento
                </option>

                {Object.keys(
                  hondurasLocations
                ).map((department) => (
                  <option
                    key={department}
                    value={department}
                  >
                    {department}
                  </option>
                ))}
              </select>
            </div>

            {errors.departamento && (
              <span className="fieldError">
                {errors.departamento}
              </span>
            )}
          </div>

          {/* CIUDAD */}

          <div className="fieldGroup">
            <label htmlFor="ciudad">
              Ciudad / municipio
            </label>

            <select
              id="ciudad"
              name="ciudad"
              value={form.ciudad}
              onChange={change}
              disabled={!form.departamento}
              className={
                errors.ciudad
                  ? "standaloneInput inputError"
                  : "standaloneInput"
              }
            >
              <option value="">
                {form.departamento
                  ? "Selecciona tu ciudad"
                  : "Selecciona primero un departamento"}
              </option>

              {(
                hondurasLocations[
                  form.departamento
                ] || []
              ).map((city) => (
                <option
                  key={city}
                  value={city}
                >
                  {city}
                </option>
              ))}
            </select>

            {errors.ciudad && (
              <span className="fieldError">
                {errors.ciudad}
              </span>
            )}
          </div>

          {/* NIVEL EDUCATIVO */}

          <div className="fieldGroup">
            <label htmlFor="nivel_educativo">
              Nivel educativo
            </label>

            <select
              id="nivel_educativo"
              name="nivel_educativo"
              value={form.nivel_educativo}
              onChange={change}
              className={
                errors.nivel_educativo
                  ? "standaloneInput inputError"
                  : "standaloneInput"
              }
            >
              <option value="">
                Selecciona una opción
              </option>

              <option value="Primaria">
                Primaria
              </option>

              <option value="Secundaria">
                Secundaria
              </option>

              <option value="Universitario">
                Universitario
              </option>

              <option value="Posgrado">
                Posgrado
              </option>

              <option value="Otro">
                Otro
              </option>
            </select>

            {errors.nivel_educativo && (
              <span className="fieldError">
                {errors.nivel_educativo}
              </span>
            )}
          </div>

          {/* CORREO */}

          <div className="fieldGroup">
            <label htmlFor="email">
              Correo electrónico
            </label>

            <div
              className={`inputWrapper ${
                errors.email
                  ? "inputError"
                  : ""
              }`}
            >
              <FiMail />

              <input
                id="email"
                name="email"
                type="email"
                placeholder="correo@ejemplo.com"
                autoComplete="email"
                value={form.email}
                onChange={change}
              />
            </div>

            {errors.email && (
              <span className="fieldError">
                {errors.email}
              </span>
            )}
          </div>

          {/* CONTRASEÑA */}

          <div className="fieldGroup">
            <label htmlFor="password">
              Contraseña
            </label>

            <div
              className={`inputWrapper ${
                errors.password
                  ? "inputError"
                  : ""
              }`}
            >
              <FiLock />

              <input
                id="password"
                name="password"
                type={
                  showPassword
                    ? "text"
                    : "password"
                }
                placeholder="Crea una contraseña segura"
                autoComplete="new-password"
                value={form.password}
                onChange={change}
              />

              <button
                type="button"
                className="passwordToggle"
                onClick={() =>
                  setShowPassword(
                    (current) => !current
                  )
                }
                aria-label={
                  showPassword
                    ? "Ocultar contraseña"
                    : "Mostrar contraseña"
                }
              >
                {showPassword ? (
                  <FiEyeOff />
                ) : (
                  <FiEye />
                )}
              </button>
            </div>

            <PasswordStrength
              password={form.password}
            />

            {errors.password && (
              <span className="fieldError">
                {errors.password}
              </span>
            )}
          </div>

          {/* CONFIRMAR CONTRASEÑA */}

          <div className="fieldGroup">
            <label htmlFor="confirmPassword">
              Confirmar contraseña
            </label>

            <div
              className={`inputWrapper ${
                errors.confirmPassword
                  ? "inputError"
                  : ""
              }`}
            >
              <FiLock />

              <input
                id="confirmPassword"
                name="confirmPassword"
                type={
                  showConfirmPassword
                    ? "text"
                    : "password"
                }
                placeholder="Repite tu contraseña"
                autoComplete="new-password"
                value={form.confirmPassword}
                onChange={change}
              />

              <button
                type="button"
                className="passwordToggle"
                onClick={() =>
                  setShowConfirmPassword(
                    (current) => !current
                  )
                }
                aria-label={
                  showConfirmPassword
                    ? "Ocultar contraseña"
                    : "Mostrar contraseña"
                }
              >
                {showConfirmPassword ? (
                  <FiEyeOff />
                ) : (
                  <FiEye />
                )}
              </button>
            </div>

            {errors.confirmPassword && (
              <span className="fieldError">
                {errors.confirmPassword}
              </span>
            )}
          </div>

          {/* ERROR GENERAL */}

          {errors.general && (
            <div className="formAlert error">
              {errors.general}
            </div>
          )}

          {/* BOTÓN */}

          <button
            type="submit"
            className="primaryButton"
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="buttonSpinner" />
                Creando cuenta...
              </>
            ) : (
              "Crear cuenta"
            )}
          </button>

          <p className="authFooterText">
            ¿Ya tienes una cuenta?{" "}
            <Link to="/login">
              Inicia sesión
            </Link>
          </p>
        </form>
      </main>
    </div>
  );
}