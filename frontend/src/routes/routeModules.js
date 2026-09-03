const modules = {
  login: () => import("../pages/auth/LoginPage"),
  register: () => import("../pages/auth/RegisterPage"),
  adminLayout: () => import("../layouts/AdminLayout"),
  userLayout: () => import("../layouts/UserLayout"),
  dashboard: () => import("../pages/admin/DashboardPage"),
  participants: () => import("../pages/admin/ParticipantsPage"),
  surveys: () => import("../pages/admin/SurveysPage"),
  risk: () => import("../pages/admin/RiskPage"),
  adminGuides: () => import("../pages/admin/GuidesPage"),
  reports: () => import("../pages/admin/ReportsPage"),
  imports: () => import("../pages/admin/ImportPage"),
  cleaning: () => import("../pages/admin/CleaningPage"),
  backups: () => import("../pages/admin/BackupsPage"),
  administration: () => import("../pages/admin/AdministrationPage"),
  userHome: () => import("../pages/user/UserOverviewPage"),
  userSurvey: () => import("../pages/user/SurveyPage"),
  userResults: () => import("../pages/user/ResultsPage"),
  userGuides: () => import("../pages/user/UserGuidesPage"),
};

const paths = {
  "/admin": "dashboard",
  "/admin/participantes": "participants",
  "/admin/encuestas": "surveys",
  "/admin/riesgo": "risk",
  "/admin/guias": "adminGuides",
  "/admin/reportes": "reports",
  "/admin/importar": "imports",
  "/admin/limpieza": "cleaning",
  "/admin/respaldos": "backups",
  "/admin/administracion": "administration",
  "/usuario": "userHome",
  "/usuario/encuesta": "userSurvey",
  "/usuario/resultados": "userResults",
  "/usuario/guias": "userGuides",
};

export function preloadRoute(path) {
  const loader = modules[paths[path]];
  if (loader) loader();
}

export default modules;
