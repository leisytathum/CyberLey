-- Persistencia segura del recorrido inicial del portal de usuario.
ALTER TABLE public.perfiles
  ADD COLUMN IF NOT EXISTS onboarding_completado boolean NOT NULL DEFAULT false,
  ADD COLUMN IF NOT EXISTS onboarding_fecha timestamptz;

CREATE OR REPLACE FUNCTION public.completar_onboarding_usuario()
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  usuario_id uuid := auth.uid();
BEGIN
  IF usuario_id IS NULL THEN
    RAISE EXCEPTION 'Sesión requerida';
  END IF;

  UPDATE public.perfiles
  SET onboarding_completado = true,
      onboarding_fecha = COALESCE(onboarding_fecha, now())
  WHERE id = usuario_id AND rol = 'usuario';

  IF NOT FOUND THEN
    RAISE EXCEPTION 'Perfil de usuario no encontrado';
  END IF;

  RETURN jsonb_build_object(
    'onboarding_completado', true,
    'onboarding_fecha', (SELECT onboarding_fecha FROM public.perfiles WHERE id = usuario_id)
  );
END;
$$;

REVOKE ALL ON FUNCTION public.completar_onboarding_usuario() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.completar_onboarding_usuario() TO authenticated;
