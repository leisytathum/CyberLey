import {
  FiMenu,
} from "react-icons/fi";

import ThemeToggle from "../common/ThemeToggle";

export default function Topbar({
  title,
  description,
  setMobileOpen,
  profile,
}) {
  const firstName =
    profile?.nombre_completo
      ?.trim()
      ?.split(" ")[0] || "Administrador";

  return (
    <header className="topbar">
      <div className="topbarMain">
        <button
          type="button"
          className="topbarMenuButton"
          onClick={() => setMobileOpen(true)}
          aria-label="Abrir navegación"
        >
          <FiMenu />
        </button>

        <div className="topbarHeading">
          <h1>{title}</h1>

          {description && (
            <p>{description}</p>
          )}
        </div>
      </div>

      <div className="topbarActions">
        <ThemeToggle />

        <div className="topbarUser">
          <div className="topbarAvatar">
            {firstName.charAt(0).toUpperCase()}
          </div>

          <div className="topbarUserInfo">
            <strong>{firstName}</strong>
            <span>Administrador</span>
          </div>
        </div>
      </div>
    </header>
  );
}
