import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import ProtectedRoute from "./ProtectedRoute";

// AUTH
import LoginPage from "../pages/auth/LoginPage";
import RegisterPage from "../pages/auth/RegisterPage";

// LAYOUTS
import AdminLayout from "../layouts/AdminLayout";
import UserLayout from "../layouts/UserLayout";

// ADMIN
import DashboardPage from "../pages/admin/DashboardPage";
import ParticipantsPage from "../pages/admin/ParticipantsPage";
import SurveysPage from "../pages/admin/SurveysPage";
import RiskPage from "../pages/admin/RiskPage";
import ReportsPage from "../pages/admin/ReportsPage";
import ImportPage from "../pages/admin/ImportPage";
import CleaningPage from "../pages/admin/CleaningPage";
import BackupsPage from "../pages/admin/BackupsPage";
import AdministrationPage from "../pages/admin/AdministrationPage";

// USUARIO
import UserHomePage from "../pages/user/UserHomePage";
import SurveyPage from "../pages/user/SurveyPage";


/*
|--------------------------------------------------------------------------
| Páginas temporales
|--------------------------------------------------------------------------
|
| Estas dos se utilizan mientras construimos los módulos completos de
| Dashboards y Guías. Evitan que el Sidebar mande al usuario al login
| por una ruta inexistente.
|
*/

function DashboardsPlaceholder() {
  return (
    <section className="dashboardPanel">
      <span className="panelEyebrow">
        Próximamente
      </span>

      <h2>Dashboards analíticos</h2>

      <p>
        Esta sección concentrará las visualizaciones
        avanzadas y comparaciones de los datos de CyberLey.
      </p>
    </section>
  );
}

function GuidesPlaceholder() {
  return (
    <section className="dashboardPanel">
      <span className="panelEyebrow">
        Contenido educativo
      </span>

      <h2>Guías de ciberseguridad</h2>

      <p>
        Desde aquí se administrarán las guías y recursos
        educativos disponibles para los usuarios.
      </p>
    </section>
  );
}


export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>

        {/* =====================================================
            RUTAS PÚBLICAS
        ===================================================== */}

        <Route
          path="/login"
          element={<LoginPage />}
        />

        <Route
          path="/registro"
          element={<RegisterPage />}
        />


        {/* =====================================================
            ADMINISTRADOR
        ===================================================== */}

        <Route
          element={
            <ProtectedRoute roles={["admin"]} />
          }
        >
          <Route
            path="/admin"
            element={<AdminLayout />}
          >
            {/* Inicio */}
            <Route
              index
              element={<DashboardPage />}
            />

            {/* Análisis */}
            <Route
              path="participantes"
              element={<ParticipantsPage />}
            />

            <Route
              path="encuestas"
              element={<SurveysPage />}
            />

            <Route
              path="riesgo"
              element={<RiskPage />}
            />

            <Route
              path="dashboards"
              element={<DashboardsPlaceholder />}
            />

            {/* Contenido */}
            <Route
              path="guias"
              element={<GuidesPlaceholder />}
            />

            <Route
              path="reportes"
              element={<ReportsPage />}
            />

            {/* Datos */}
            <Route
              path="importar"
              element={<ImportPage />}
            />

            <Route
              path="limpieza"
              element={<CleaningPage />}
            />

            <Route
              path="respaldos"
              element={<BackupsPage />}
            />

            {/* Sistema */}
            <Route
              path="administracion"
              element={<AdministrationPage />}
            />
          </Route>
        </Route>


        {/* =====================================================
            USUARIO
        ===================================================== */}

        <Route
          element={
            <ProtectedRoute
              roles={["usuario", "admin"]}
            />
          }
        >
          <Route
            path="/usuario"
            element={<UserLayout />}
          >
            <Route
              index
              element={<UserHomePage />}
            />

            <Route
              path="encuesta"
              element={<SurveyPage />}
            />
          </Route>
        </Route>


        {/* =====================================================
            REDIRECCIONES
        ===================================================== */}

        <Route
          path="/"
          element={
            <Navigate
              to="/login"
              replace
            />
          }
        />

        <Route
          path="*"
          element={
            <Navigate
              to="/login"
              replace
            />
          }
        />

      </Routes>
    </BrowserRouter>
  );
}