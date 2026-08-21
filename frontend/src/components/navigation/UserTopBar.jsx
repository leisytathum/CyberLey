import {
  FiBell,
  FiMenu,
  FiSearch,
} from "react-icons/fi";

import ThemeToggle from "../common/ThemeToggle";

export default function UserTopbar({
  title,
  description,
  setMobileOpen,
  profile,
}) {
  const firstName =
    profile?.nombre_completo
      ?.trim()
      ?.split(" ")[0] ||
    "Usuario";

  return (
    <header className="topbar">
      <div className="topbarMain">
        <button
          type="button"
          className="topbarMenuButton"
          onClick={() =>
            setMobileOpen(true)
          }
          aria-label="Abrir navegación"
        >
          <FiMenu />
        </button>

        <div className="topbarHeading">
          <h1>
            {title}
          </h1>

          {description && (
            <p>
              {description}
            </p>
          )}
        </div>
      </div>

      <div className="topbarActions">
        <div className="topbarSearch">
          <FiSearch />

          <input
            type="search"
            placeholder="Buscar en CyberLey..."
          />
        </div>

        <ThemeToggle />

        <button
          type="button"
          className="notificationButton"
        >
          <FiBell />

          <span className="notificationDot" />
        </button>

        <div className="topbarUser">
          <div className="topbarAvatar">
            {firstName
              .charAt(0)
              .toUpperCase()}
          </div>

          <div className="topbarUserInfo">
            <strong>
              {firstName}
            </strong>

            <span>
              Usuario
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}