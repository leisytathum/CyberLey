import { useEffect, useState } from "react";
import { Outlet, useLocation } from "react-router-dom";

import Sidebar from "../components/navigation/Sidebar";
import Topbar from "../components/navigation/Topbar";

import { supabase } from "../services/supabaseClient";

import "../styles/admin-layout.css";

const pageInformation = {
  "/admin": {
    title: "Inicio",
    description:
      "Una vista general de los datos y la actividad de CyberLey.",
  },

  "/admin/participantes": {
    title: "Participantes",
    description:
      "Consulta y administra las personas registradas en el estudio.",
  },

  "/admin/encuestas": {
    title: "Encuestas",
    description:
      "Explora las respuestas recopiladas en las evaluaciones.",
  },

  "/admin/riesgo": {
    title: "Análisis de riesgo",
    description:
      "Consulta la clasificación y comportamiento de riesgo digital.",
  },

  "/admin/dashboards": {
    title: "Dashboards",
    description:
      "Visualiza tendencias, patrones y métricas relevantes.",
  },

  "/admin/guias": {
    title: "Guías de ciberseguridad",
    description:
      "Administra los recursos educativos disponibles para los usuarios.",
  },

  "/admin/reportes": {
    title: "Reportes",
    description:
      "Genera y consulta resultados del análisis de datos.",
  },

  "/admin/importar": {
    title: "Importar datos",
    description:
      "Incorpora nuevos registros de forma controlada.",
  },

  "/admin/limpieza": {
    title: "Limpieza de datos",
    description:
      "Identifica inconsistencias y prepara los datos para su análisis.",
  },

  "/admin/respaldos": {
    title: "Respaldos",
    description:
      "Administra copias de seguridad de la información.",
  },

  "/admin/administracion": {
    title: "Administración",
    description:
      "Gestiona configuraciones y usuarios del sistema.",
  },
};

export default function AdminLayout() {
  const location = useLocation();

  const [collapsed, setCollapsed] =
    useState(false);

  const [mobileOpen, setMobileOpen] =
    useState(false);

  const [profile, setProfile] =
    useState(null);

  useEffect(() => {
    async function loadProfile() {
      const {
        data: { user },
      } = await supabase.auth.getUser();

      if (!user) return;

      const { data } = await supabase
        .from("perfiles")
        .select(
          "nombre_completo, rol, foto_url"
        )
        .eq("id", user.id)
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
    pageInformation[location.pathname] ||
    {
      title: "CyberLey",
      description:
        "Sistema de análisis y educación en ciberseguridad.",
    };

  return (
    <div
      className={`adminShell ${
        collapsed ? "adminShellCollapsed" : ""
      }`}
    >
      <Sidebar
        collapsed={collapsed}
        setCollapsed={setCollapsed}
        mobileOpen={mobileOpen}
        setMobileOpen={setMobileOpen}
        profile={profile}
      />

      <div className="adminWorkspace">
        <Topbar
          title={page.title}
          description={page.description}
          setMobileOpen={setMobileOpen}
          profile={profile}
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