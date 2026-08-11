import { FiMoon, FiSun } from "react-icons/fi";
import { useTheme } from "../../context/ThemeContext";

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      type="button"
      className="iconButton"
      onClick={toggleTheme}
      aria-label={
        theme === "dark"
          ? "Activar modo claro"
          : "Activar modo oscuro"
      }
      title={
        theme === "dark"
          ? "Modo claro"
          : "Modo oscuro"
      }
    >
      {theme === "dark" ? <FiSun /> : <FiMoon />}
    </button>
  );
}