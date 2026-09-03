import {
  FiChevronDown,
  FiLogOut,
  FiMenu,
} from "react-icons/fi";
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

import ThemeToggle from "../common/ThemeToggle";
import { useAuth } from "../../context/AuthContext";

export default function Topbar({
  title,
  description,
  setMobileOpen,
  profile,
}) {
  const navigate = useNavigate();
  const { signOut } = useAuth();
  const menuRef = useRef(null);
  const [profileOpen, setProfileOpen] = useState(false);
  const firstName =
    profile?.nombre_completo
      ?.trim()
      ?.split(" ")[0] || "Administrador";

  useEffect(() => {
    const close = (event) => {
      if (!menuRef.current?.contains(event.target)) setProfileOpen(false);
    };
    document.addEventListener("pointerdown", close);
    return () => document.removeEventListener("pointerdown", close);
  }, []);

  async function logout() {
    try {
      await signOut();
      toast.success("Sesión cerrada correctamente.");
      navigate("/login", { replace: true });
    } catch (error) {
      console.error("[CyberLey logout]", error);
      toast.error("No pudimos cerrar la sesión. Intenta nuevamente.");
    }
  }

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

        <div className="topbarProfileMenu" ref={menuRef}>
          <button type="button" className="topbarUser" onClick={() => setProfileOpen((current) => !current)} aria-expanded={profileOpen}>
            <div className="topbarAvatar">{firstName.charAt(0).toUpperCase()}</div>
            <div className="topbarUserInfo"><strong>{firstName}</strong><span>Administrador</span></div>
            <FiChevronDown className="topbarUserChevron" />
          </button>
          {profileOpen && <div className="topbarProfileDropdown"><div><strong>{profile?.nombre_completo || firstName}</strong><span>Administrador</span></div><button type="button" onClick={logout}><FiLogOut /> Cerrar sesión</button></div>}
        </div>
      </div>
    </header>
  );
}
