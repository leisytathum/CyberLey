import {
  Navigate,
  Outlet,
  useLocation,
} from "react-router-dom";

import { useAuth } from "../context/AuthContext";


export default function ProtectedRoute({
  roles,
}) {
  const {
    user,
    profile,
    loading,
  } = useAuth();

  const location = useLocation();


  /*
   * Mientras Supabase comprueba si existe
   * una sesión activa.
   */
  if (loading) {
    return (
      <div className="routeLoader">
        <div className="routeLoaderSpinner" />

        <p>
          Preparando tu espacio...
        </p>
      </div>
    );
  }


  /*
   * No existe sesión.
   */
  if (!user) {
    return (
      <Navigate
        to="/login"
        replace
        state={{
          from: location.pathname,
        }}
      />
    );
  }


  /*
   * Todavía tenemos usuario de Supabase,
   * pero no se ha encontrado el perfil.
   */
  if (!profile) {
    return (
      <div className="routeLoader">
        <p>
          No fue posible cargar tu perfil.
        </p>
      </div>
    );
  }


  /*
   * Verificación del rol.
   */
  if (
    roles?.length &&
    !roles.includes(profile.rol)
  ) {
    if (profile.rol === "admin") {
      return (
        <Navigate
          to="/admin"
          replace
        />
      );
    }

    return (
      <Navigate
        to="/usuario"
        replace
      />
    );
  }


  return <Outlet />;
}