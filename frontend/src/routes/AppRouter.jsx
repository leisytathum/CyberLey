import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";
import { lazy, Suspense } from "react";

import ProtectedRoute from "./ProtectedRoute";
import routeModules from "./routeModules";

// AUTH Y LAYOUTS
const LoginPage=lazy(routeModules.login);
const RegisterPage=lazy(routeModules.register);
const AdminLayout=lazy(routeModules.adminLayout);
const UserLayout=lazy(routeModules.userLayout);

// ADMIN
const DashboardPage=lazy(routeModules.dashboard);
const ParticipantsPage=lazy(routeModules.participants);
const SurveysPage=lazy(routeModules.surveys);
const RiskPage=lazy(routeModules.risk);
const ReportsPage=lazy(routeModules.reports);
const ImportPage=lazy(routeModules.imports);
const CleaningPage=lazy(routeModules.cleaning);
const BackupsPage=lazy(routeModules.backups);
const AdministrationPage=lazy(routeModules.administration);
const GuidesPage=lazy(routeModules.adminGuides);

// USUARIO
const UserHomePage=lazy(routeModules.userHome);
const SurveyPage=lazy(routeModules.userSurvey);
const ResultsPage=lazy(routeModules.userResults);
const UserGuidesPage=lazy(routeModules.userGuides);


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
