import {
  Suspense,
  useEffect,
  useState,
} from "react";

import {
  Outlet,
  useLocation,
} from "react-router-dom";

import UserSidebar from "../components/navigation/UserSidebar";
import UserTopBar from "../components/navigation/UserTopBar";
import { useAuth } from "../context/AuthContext";
import ModuleErrorBoundary from "../components/common/ModuleErrorBoundary";
import CyberGuide from "../components/user/CyberGuide";

import "../styles/admin-layout.css";
import "../styles/modules.css";

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
  const { profile } = useAuth();

  const [
    collapsed,
    setCollapsed,
  ] = useState(false);

  const [
    mobileOpen,
    setMobileOpen,
  ] = useState(false);

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
      className={`adminShell userShell ${
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
      />

      <div className="adminWorkspace">
        <UserTopBar
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
            <ModuleErrorBoundary key={location.pathname}>
              <Suspense fallback={<div className="moduleSkeleton"><span /><span /><span /></div>}>
                <Outlet />
              </Suspense>
            </ModuleErrorBoundary>
          </div>
        </main>
      </div>
      <CyberGuide profile={profile} />
    </div>
  );
}
