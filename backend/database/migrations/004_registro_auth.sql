-- Alta reproducible de perfiles y participantes desde Supabase Auth.
-- Ejecutar después de 001, 002 y 003.
CREATE OR REPLACE FUNCTION public.registrar_usuario_cyberley()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  rol_inicial text;
  nombre text;
BEGIN
  -- raw_app_meta_data solo puede establecerlo una operación administrativa.
  -- Los registros realizados desde el navegador siempre quedan como usuario.
  rol_inicial := CASE
    WHEN new.raw_app_meta_data ->> 'seed_role' = 'admin' THEN 'admin'
    ELSE 'usuario'
  END;
  nombre := COALESCE(
    NULLIF(trim(new.raw_user_meta_data ->> 'nombre_completo'), ''),
    split_part(COALESCE(new.email, new.id::text), '@', 1)
  );

  INSERT INTO public.perfiles (id, nombre_completo, rol)
  VALUES (new.id, nombre, rol_inicial)
  ON CONFLICT (id) DO UPDATE
  SET nombre_completo = EXCLUDED.nombre_completo;

  IF rol_inicial = 'usuario' THEN
    INSERT INTO public.participantes (
      id_usuario,
      nombre_completo,
      edad,
      genero,
      departamento,
      ciudad,
      nivel_educativo,
      fecha_nacimiento
    )
    SELECT
      new.id,
      nombre,
      NULLIF(new.raw_user_meta_data ->> 'edad', '')::integer,
      NULLIF(new.raw_user_meta_data ->> 'genero', ''),
      NULLIF(new.raw_user_meta_data ->> 'departamento', ''),
      NULLIF(new.raw_user_meta_data ->> 'ciudad', ''),
      NULLIF(new.raw_user_meta_data ->> 'nivel_educativo', ''),
      NULLIF(new.raw_user_meta_data ->> 'fecha_nacimiento', '')::date
    WHERE NOT EXISTS (
      SELECT 1 FROM public.participantes WHERE id_usuario = new.id
    );
  END IF;

  RETURN new;
END;
$$;

DROP TRIGGER IF EXISTS al_crear_usuario_cyberley ON auth.users;
CREATE TRIGGER al_crear_usuario_cyberley
AFTER INSERT ON auth.users
FOR EACH ROW EXECUTE FUNCTION public.registrar_usuario_cyberley();
