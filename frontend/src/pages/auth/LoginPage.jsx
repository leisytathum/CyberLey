import { useState } from "react";
import {
  FiEye,
  FiEyeOff,
  FiLock,
  FiMail,
  FiShield,
} from "react-icons/fi";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";

import ThemeToggle from "../../components/common/ThemeToggle";
import { supabase } from "../../services/supabaseClient";
import { useAuth } from "../../context/AuthContext";

export default function LoginPage() {
  const navigate = useNavigate();
  const { refreshProfile } = useAuth();

  const [form, setForm] = useState({
    email: "",
    password: "",
  });

  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const [errors, setErrors] = useState({});

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

  const validate = () => {
    const nextErrors = {};

    if (!form.email.trim()) {
      nextErrors.email = "Ingresa tu correo electrónico.";
    } else if (
      !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim())
    ) {
      nextErrors.email = "Ingresa un correo electrónico válido.";
    }

    if (!form.password) {
      nextErrors.password = "Ingresa tu contraseña.";
    }

    setErrors(nextErrors);

    return Object.keys(nextErrors).length === 0;
  };

  async function submit(event) {
    event.preventDefault();

    if (!validate()) {
      toast.error("Revisa los campos marcados.");
      return;
    }

    try {
      setLoading(true);

      const { data, error } =
        await supabase.auth.signInWithPassword({
          email: form.email.trim().toLowerCase(),
          password: form.password,
        });

      if (error) {
        throw error;
      }

      const profile = await refreshProfile(data.user);

      if (!profile) {
        throw new Error(
          "No encontramos el perfil asociado a esta cuenta."
        );
      }

      toast.success(
        `Bienvenido${profile.nombre_completo
          ? `, ${profile.nombre_completo.split(" ")[0]}`
          : ""
        }.`
      );

      navigate(
        profile.rol === "admin"
          ? "/admin"
          : "/usuario",
        {
          replace: true,
        }
      );
    } catch (error) {
      console.error("[CyberLey login]", error);

      setErrors({
        general:
          "No pudimos iniciar sesión. Verifica tu correo y contraseña.",
      });

      toast.error("No fue posible iniciar sesión.");
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
            <FiShield />
            Seguridad digital al alcance de todos
          </span>

          <h1>
            Comprende tus hábitos.
            <span> Protege tu vida digital.</span>
          </h1>

          <p>
            Analiza tu comportamiento en línea, identifica
            riesgos y descubre prácticas que pueden ayudarte
            a navegar con mayor seguridad.
          </p>
        </div>

        <div className="authDecoration authDecorationOne" />
        <div className="authDecoration authDecorationTwo" />
      </section>

      <main className="authFormArea">
        <form className="authCard" onSubmit={submit} noValidate>
          <div className="authCardHeader">
            <span className="eyebrow">Bienvenido</span>
            <h2>Iniciar sesión</h2>
            <p>
              Ingresa tus datos para continuar en CyberLey.
            </p>
          </div>

          <div className="fieldGroup">
            <label htmlFor="email">
              Correo electrónico
            </label>

            <div
              className={`inputWrapper ${
                errors.email ? "inputError" : ""
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

          <div className="fieldGroup">
            <label htmlFor="password">
              Contraseña
            </label>

            <div
              className={`inputWrapper ${
                errors.password ? "inputError" : ""
              }`}
            >
              <FiLock />

              <input
                id="password"
                name="password"
                type={showPassword ? "text" : "password"}
                placeholder="Ingresa tu contraseña"
                autoComplete="current-password"
                value={form.password}
                onChange={change}
              />

              <button
                type="button"
                className="passwordToggle"
                onClick={() =>
                  setShowPassword((current) => !current)
                }
                aria-label={
                  showPassword
                    ? "Ocultar contraseña"
                    : "Mostrar contraseña"
                }
              >
                {showPassword ? <FiEyeOff /> : <FiEye />}
              </button>
            </div>

            {errors.password && (
              <span className="fieldError">
                {errors.password}
              </span>
            )}
          </div>

          {errors.general && (
            <div className="formAlert error">
              {errors.general}
            </div>
          )}

          <button
            className="primaryButton"
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="buttonSpinner" />
                Iniciando sesión...
              </>
            ) : (
              "Iniciar sesión"
            )}
          </button>

          <div className="authDivider">
            <span />
            <p>¿Primera vez en CyberLey?</p>
            <span />
          </div>

          <Link
            to="/registro"
            className="secondaryButton"
          >
            Crear una cuenta
          </Link>
        </form>
      </main>
    </div>
  );
}
