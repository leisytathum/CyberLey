import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";
import { lazy, Suspense } from "react";

import ProtectedRoute from "./ProtectedRoute";

// AUTH Y LAYOUTS
const LoginPage=lazy(()=>import("../pages/auth/LoginPage"));
const RegisterPage=lazy(()=>import("../pages/auth/RegisterPage"));
const AdminLayout=lazy(()=>import("../layouts/AdminLayout"));
const UserLayout=lazy(()=>import("../layouts/UserLayout"));

// ADMIN
const DashboardPage=lazy(()=>import("../pages/admin/DashboardPage"));
const ParticipantsPage=lazy(()=>import("../pages/admin/ParticipantsPage"));
const SurveysPage=lazy(()=>import("../pages/admin/SurveysPage"));
const RiskPage=lazy(()=>import("../pages/admin/RiskPage"));
const ReportsPage=lazy(()=>import("../pages/admin/ReportsPage"));
const ImportPage=lazy(()=>import("../pages/admin/ImportPage"));
const CleaningPage=lazy(()=>import("../pages/admin/CleaningPage"));
const BackupsPage=lazy(()=>import("../pages/admin/BackupsPage"));
const AdministrationPage=lazy(()=>import("../pages/admin/AdministrationPage"));
const AnalyticsPage=lazy(()=>import("../pages/admin/AnalyticsPage"));
const GuidesPage=lazy(()=>import("../pages/admin/GuidesPage"));

// USUARIO
const UserHomePage=lazy(()=>import("../pages/user/UserHomePage"));
const SurveyPage=lazy(()=>import("../pages/user/SurveyPage"));
const ResultsPage=lazy(()=>import("../pages/user/ResultsPage"));
const UserGuidesPage=lazy(()=>import("../pages/user/UserGuidesPage"));


export default function AppRouter() {
  return (
    <BrowserRouter>
      <Suspense fallback={<div className="routeSkeleton" aria-label="Abriendo módulo" />}>
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
              element={<AnalyticsPage />}
            />

            {/* Contenido */}
            <Route
              path="guias"
              element={<GuidesPage />}
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
            <Route path="resultados" element={<ResultsPage />} />
            <Route path="guias" element={<UserGuidesPage />} />
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
      </Suspense>
    </BrowserRouter>
  );
}
