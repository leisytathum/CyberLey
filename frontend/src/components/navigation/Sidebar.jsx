import {
  FiBarChart2,
  FiBookOpen,
  FiChevronLeft,
  FiDatabase,
  FiFileText,
  FiHome,
  FiLogOut,
  FiPieChart,
  FiRefreshCw,
  FiSettings,
  FiShield,
  FiUploadCloud,
  FiUsers,
  FiX,
} from "react-icons/fi";

import { NavLink, useNavigate } from "react-router-dom";
import { toast } from "sonner";

import { supabase } from "../../services/supabaseClient";
import { preloadRoute } from "../../routes/routeModules";

const navigationGroups = [
  {
    label: "Principal",
    items: [
      {
        label: "Inicio",
        icon: FiHome,
        to: "/admin",
        end: true,
      },
    ],
  },

  {
    label: "Análisis",
    items: [
      {
        label: "Participantes",
        icon: FiUsers,
        to: "/admin/participantes",
      },
      {
        label: "Encuestas",
        icon: FiFileText,
        to: "/admin/encuestas",
      },
      {
        label: "Riesgo",
        icon: FiShield,
        to: "/admin/riesgo",
      },
      {
        label: "Dashboards",
        icon: FiBarChart2,
        to: "/admin/dashboards",
      },
    ],
  },

  {
    label: "Contenido",
    items: [
      {
        label: "Guías",
        icon: FiBookOpen,
        to: "/admin/guias",
      },
      {
        label: "Reportes",
        icon: FiPieChart,
        to: "/admin/reportes",
      },
    ],
  },

  {
    label: "Datos",
    items: [
      {
        label: "Importar datos",
        icon: FiUploadCloud,
        to: "/admin/importar",
      },
      {
        label: "Limpieza",
        icon: FiRefreshCw,
        to: "/admin/limpieza",
      },
      {
        label: "Respaldos",
        icon: FiDatabase,
        to: "/admin/respaldos",
      },
    ],
  },

  {
    label: "Sistema",
    items: [
      {
        label: "Administración",
        icon: FiSettings,
        to: "/admin/administracion",
      },
    ],
  },
];

export default function Sidebar({
  collapsed,
  setCollapsed,
  mobileOpen,
  setMobileOpen,
  profile,
}) {
  const navigate = useNavigate();

  async function logout() {
    try {
      await supabase.auth.signOut();

      toast.success("Sesión cerrada correctamente.");

      navigate("/login", {
        replace: true,
      });
    } catch (error) {
      console.error("[CyberLey logout]", error);

      toast.error(
        "No pudimos cerrar la sesión. Intenta nuevamente."
      );
    }
  }

  const closeMobile = () => {
    setMobileOpen(false);
  };

  return (
    <>
      {mobileOpen && (
        <button
          type="button"
          className="sidebarOverlay"
          aria-label="Cerrar menú"
          onClick={closeMobile}
        />
      )}

      <aside
        className={[
          "sidebar",
          collapsed ? "sidebarCollapsed" : "",
          mobileOpen ? "sidebarMobileOpen" : "",
        ]
          .filter(Boolean)
          .join(" ")}
      >
        <div className="sidebarHeader">
          <div className="sidebarBrand">
            <div className="sidebarLogoWrapper">
              <img
                src="/logo.png"
                alt="CyberLey"
                className="sidebarLogo"
              />
            </div>

            {!collapsed && (
              <div className="sidebarBrandText">
                <strong>CyberLey</strong>
                <span>Seguridad digital</span>
              </div>
            )}
          </div>

          <button
            type="button"
            className="sidebarMobileClose"
            onClick={closeMobile}
            aria-label="Cerrar navegación"
          >
            <FiX />
          </button>
        </div>

        <nav className="sidebarNavigation">
          {navigationGroups.map((group) => (
            <div
              className="sidebarGroup"
              key={group.label}
            >
              {!collapsed && (
                <span className="sidebarGroupLabel">
                  {group.label}
                </span>
              )}

              <div className="sidebarGroupItems">
                {group.items.map((item) => {
                  const Icon = item.icon;

                  return (
                    <NavLink
                      key={item.to}
                      to={item.to}
                      end={item.end}
                      onClick={closeMobile}
                      onMouseEnter={() => preloadRoute(item.to)}
                      onFocus={() => preloadRoute(item.to)}
                      title={
                        collapsed
                          ? item.label
                          : undefined
                      }
                      className={({ isActive }) =>
                        [
                          "sidebarLink",
                          isActive
                            ? "sidebarLinkActive"
                            : "",
                        ]
                          .filter(Boolean)
                          .join(" ")
                      }
                    >
                      <span className="sidebarLinkIcon">
                        <Icon />
                      </span>

                      {!collapsed && (
                        <span className="sidebarLinkText">
                          {item.label}
                        </span>
                      )}
                    </NavLink>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        <div className="sidebarFooter">
          <div className="sidebarProfile">
            <div className="sidebarAvatar">
              {profile?.nombre_completo
                ?.charAt(0)
                ?.toUpperCase() || "A"}
            </div>

            {!collapsed && (
              <div className="sidebarProfileInfo">
                <strong>
                  {profile?.nombre_completo ||
                    "Administrador"}
                </strong>

                <span>
                  {profile?.rol === "admin"
                    ? "Administrador"
                    : profile?.rol || ""}
                </span>
              </div>
            )}
          </div>

          <button
            type="button"
            className="sidebarLogout"
            onClick={logout}
            title="Cerrar sesión"
          >
            <FiLogOut />

            {!collapsed && (
              <span>Cerrar sesión</span>
            )}
          </button>

          <button
            type="button"
            className="sidebarCollapseButton"
            onClick={() =>
              setCollapsed((current) => !current)
            }
          >
            <FiChevronLeft />

            {!collapsed && (
              <span>Contraer menú</span>
            )}
          </button>
        </div>
      </aside>
    </>
  );
}
