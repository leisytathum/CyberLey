import {
  FiBookOpen,
  FiChevronDown,
  FiChevronLeft,
  FiFileText,
  FiHome,
  FiShield,
  FiX,
} from "react-icons/fi";

import { useEffect, useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import { preloadRoute } from "../../routes/routeModules";

const navigationGroups = [
  {
    label: "Principal",
    tone: "violet",
    icon: FiHome,
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
    tone: "purple",
    icon: FiShield,
    items: [
      {
        label: "Evaluación",
        icon: FiFileText,
        to: "/usuario/encuesta",
        guide: "evaluation",
      },
      {
        label: "Mis resultados",
        icon: FiShield,
        to: "/usuario/resultados",
        guide: "results",
      },
    ],
  },

  {
    label: "Contenido",
    tone: "blue",
    icon: FiBookOpen,
    items: [
      {
        label: "Guías",
        icon: FiBookOpen,
        to: "/usuario/guias",
        guide: "guides",
      },
    ],
  },
];

export default function UserSidebar({
  collapsed,
  setCollapsed,
  mobileOpen,
  setMobileOpen,
}) {
  const location = useLocation();
  const activeGroup = navigationGroups.find((group) => group.items.some((item) => item.end ? location.pathname === item.to : location.pathname.startsWith(item.to)))?.label;
  const [openGroup, setOpenGroup] = useState(activeGroup || "Mi seguridad");

  useEffect(() => {
    if (activeGroup && activeGroup !== "Principal") setOpenGroup(activeGroup);
  }, [activeGroup]);

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
            aria-label="Cerrar navegación"
          >
            <FiX />
          </button>
        </div>

        <nav className="sidebarNavigation">
          {navigationGroups.map(
            (group) => {
              const GroupIcon = group.icon;
              return (
              <div
                className={`sidebarGroup sidebarGroup-${group.tone} ${openGroup === group.label ? "sidebarGroupOpen" : ""}`}
                key={group.label}
              >
                {!collapsed && group.label !== "Principal" && <button type="button" className="sidebarGroupToggle" onClick={() => setOpenGroup((current) => current === group.label ? "" : group.label)} aria-expanded={openGroup === group.label}><span className="sidebarGroupTitle"><i><GroupIcon /></i>{group.label}</span><FiChevronDown className="sidebarGroupChevron" /></button>}

                {!collapsed && group.label === "Principal" && <span className="sidebarGroupLabel"><i><GroupIcon /></i>{group.label}</span>}

                <div className={`sidebarGroupItems ${collapsed || group.label === "Principal" || openGroup === group.label ? "sidebarGroupItemsOpen" : ""}`}>
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
                          data-guide={item.guide}
                          onClick={
                            closeMobile
                          }
                          onMouseEnter={() => preloadRoute(item.to)}
                          onFocus={() => preloadRoute(item.to)}
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
            );}
          )}
        </nav>

        <button type="button" className="sidebarEdgeToggle" onClick={() => setCollapsed((current) => !current)} aria-label={collapsed ? "Expandir menú" : "Contraer menú"} title={collapsed ? "Expandir menú" : "Contraer menú"}><FiChevronLeft /></button>
      </aside>
    </>
  );
}
