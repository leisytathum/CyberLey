import {
  FiBookOpen,
  FiChevronLeft,
  FiFileText,
  FiHome,
  FiLogOut,
  FiShield,
  FiX,
} from "react-icons/fi";

import {
  NavLink,
  useNavigate,
} from "react-router-dom";

import { toast } from "sonner";

import { supabase } from "../../services/supabaseClient";

const navigationGroups = [
  {
    label: "Principal",
    items: [
      {
        label: "Inicio",
        icon: FiHome,
        to: "/usuario",
        end: true,
      },
    ],
  },

  {
    label: "Mi seguridad",
    items: [
      {
        label: "Evaluación",
        icon: FiFileText,
        to: "/usuario/encuesta",
      },
      {
        label: "Mis resultados",
        icon: FiShield,
        to: "/usuario/resultados",
      },
    ],
  },

  {
    label: "Contenido",
    items: [
      {
        label: "Guías",
        icon: FiBookOpen,
        to: "/usuario/guias",
      },
    ],
  },
];

export default function UserSidebar({
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

      toast.success(
        "Sesión cerrada correctamente."
      );

      navigate("/login", {
        replace: true,
      });
    } catch (error) {
      console.error(
        "[CyberLey logout]",
        error
      );

      toast.error(
        "No pudimos cerrar la sesión."
      );
    }
  }

  function closeMobile() {
    setMobileOpen(false);
  }

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

          collapsed
            ? "sidebarCollapsed"
            : "",

          mobileOpen
            ? "sidebarMobileOpen"
            : "",
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
                <strong>
                  CyberLey
                </strong>

                <span>
                  Seguridad digital
                </span>
              </div>
            )}
          </div>

          <button
            type="button"
            className="sidebarMobileClose"
            onClick={closeMobile}
          >
            <FiX />
          </button>
        </div>

        <nav className="sidebarNavigation">
          {navigationGroups.map(
            (group) => (
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
                  {group.items.map(
                    (item) => {
                      const Icon =
                        item.icon;

                      return (
                        <NavLink
                          key={
                            item.to
                          }
                          to={
                            item.to
                          }
                          end={
                            item.end
                          }
                          onClick={
                            closeMobile
                          }
                          title={
                            collapsed
                              ? item.label
                              : undefined
                          }
                          className={({
                            isActive,
                          }) =>
                            [
                              "sidebarLink",

                              isActive
                                ? "sidebarLinkActive"
                                : "",
                            ]
                              .filter(
                                Boolean
                              )
                              .join(
                                " "
                              )
                          }
                        >
                          <span className="sidebarLinkIcon">
                            <Icon />
                          </span>

                          {!collapsed && (
                            <span className="sidebarLinkText">
                              {
                                item.label
                              }
                            </span>
                          )}
                        </NavLink>
                      );
                    }
                  )}
                </div>
              </div>
            )
          )}
        </nav>

        <div className="sidebarFooter">
          <div className="sidebarProfile">
            <div className="sidebarAvatar">
              {profile
                ?.nombre_completo
                ?.charAt(0)
                ?.toUpperCase() ||
                "U"}
            </div>

            {!collapsed && (
              <div className="sidebarProfileInfo">
                <strong>
                  {profile
                    ?.nombre_completo ||
                    "Usuario"}
                </strong>

                <span>
                  Usuario
                </span>
              </div>
            )}
          </div>

          <button
            type="button"
            className="sidebarLogout"
            onClick={logout}
          >
            <FiLogOut />

            {!collapsed && (
              <span>
                Cerrar sesión
              </span>
            )}
          </button>

          <button
            type="button"
            className="sidebarCollapseButton"
            onClick={() =>
              setCollapsed(
                (current) =>
                  !current
              )
            }
          >
            <FiChevronLeft />

            {!collapsed && (
              <span>
                Contraer menú
              </span>
            )}
          </button>
        </div>
      </aside>
    </>
  );
}