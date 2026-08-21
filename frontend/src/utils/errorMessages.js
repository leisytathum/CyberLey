export function getFriendlyError(error) {
  const message =
    error?.response?.data?.detail ||
    error?.message ||
    "";

  const normalized =
    message.toLowerCase();

  if (
    normalized.includes(
      "invalid login credentials"
    )
  ) {
    return "Correo o contraseña incorrectos.";
  }

  if (
    normalized.includes(
      "user already registered"
    ) ||
    normalized.includes(
      "already registered"
    )
  ) {
    return "Ya existe una cuenta registrada con este correo.";
  }

  if (
    normalized.includes(
      "password should be"
    )
  ) {
    return "La contraseña no cumple los requisitos de seguridad.";
  }

  if (
    normalized.includes("network")
  ) {
    return "No fue posible conectarse con el servidor. Revisa tu conexión.";
  }

  if (
    normalized.includes("timeout")
  ) {
    return "La solicitud tardó demasiado. Intenta nuevamente.";
  }

  if (
    normalized.includes("session")
  ) {
    return "Tu sesión expiró. Inicia sesión nuevamente.";
  }

  return "Ocurrió un problema inesperado. Intenta nuevamente.";
}