import {
  useEffect,
  useState,
} from "react";

import {
  Outlet,
  useLocation,
} from "react-router-dom";

import UserSidebar from "../components/navigation/UserSidebar";
import UserTopbar from "../components/navigation/UserTopbar";

import { supabase } from "../services/supabaseClient";

import "../styles/admin-layout.css";

const pageInformation = {
  "/usuario": {
    title: "Inicio",
    description:
      "Conoce tu nivel de seguridad digital y revisa tus evaluaciones.",
  },

  "/usuario/encuesta": {
    title: "Evaluación",
    description:
      "Responde la evaluación de hábitos digitales y ciberseguridad.",
  },

  "/usuario/resultados": {
    title: "Mis resultados",
    description:
      "Consulta el historial y evolución de tus evaluaciones.",
  },

  "/usuario/guias": {
    title: "Guías de ciberseguridad",
    description:
      "Consulta recomendaciones para mejorar tus hábitos digitales.",
  },
};

export default function UserLayout() {
  const location =
    useLocation();

  const [
    collapsed,
    setCollapsed,
  ] = useState(false);

  const [
    mobileOpen,
    setMobileOpen,
  ] = useState(false);

  const [
    profile,
    setProfile,
  ] = useState(null);

  useEffect(() => {
    async function loadProfile() {
      const {
        data: { user },
      } =
        await supabase.auth.getUser();

      if (!user) return;

      const { data } =
        await supabase
          .from("perfiles")
          .select(
            "nombre_completo, rol, foto_url"
          )
          .eq(
            "id",
            user.id
          )
          .maybeSingle();

      if (data) {
        setProfile(data);
      }
    }

    loadProfile();
  }, []);

  useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname]);

  const page =
    pageInformation[
      location.pathname
    ] || {
      title: "CyberLey",
      description:
        "Tu espacio de seguridad digital.",
    };

  return (
    <div
      className={`adminShell ${
        collapsed
          ? "adminShellCollapsed"
          : ""
      }`}
    >
      <UserSidebar
        collapsed={collapsed}
        setCollapsed={
          setCollapsed
        }
        mobileOpen={
          mobileOpen
        }
        setMobileOpen={
          setMobileOpen
        }
        profile={profile}
      />

      <div className="adminWorkspace">
        <UserTopbar
          title={
            page.title
          }
          description={
            page.description
          }
          setMobileOpen={
            setMobileOpen
          }
          profile={
            profile
          }
        />

        <main className="adminContent">
          <div className="pageEnter">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}