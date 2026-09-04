-- Retira únicamente las cuatro guías de demostración originales.
DELETE FROM public.guias_ciberseguridad
WHERE titulo IN (
  'Cómo crear contraseñas seguras',
  'Cómo identificar phishing',
  'Seguridad en redes WiFi públicas',
  'Seguridad en redes Wi-Fi públicas',
  'Verificación en dos pasos'
);
