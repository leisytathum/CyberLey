ALTER TABLE public.guias_ciberseguridad
  ADD COLUMN IF NOT EXISTS tipo_recurso varchar NOT NULL DEFAULT 'documento'
    CHECK (tipo_recurso IN ('documento', 'pdf', 'imagen', 'video', 'interactivo')),
  ADD COLUMN IF NOT EXISTS archivo_url text,
  ADD COLUMN IF NOT EXISTS archivo_nombre varchar,
  ADD COLUMN IF NOT EXISTS estado varchar NOT NULL DEFAULT 'borrador'
    CHECK (estado IN ('borrador', 'publicada')),
  ADD COLUMN IF NOT EXISTS creado_por uuid REFERENCES public.perfiles(id);

CREATE TABLE IF NOT EXISTS public.guias_asignadas (
  id_asignacion uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  id_guia uuid NOT NULL REFERENCES public.guias_ciberseguridad(id_guia) ON DELETE CASCADE,
  id_participante uuid NOT NULL REFERENCES public.participantes(id_participante) ON DELETE CASCADE,
  mensaje text,
  fecha_asignacion timestamptz NOT NULL DEFAULT now(),
  UNIQUE (id_guia, id_participante)
);

ALTER TABLE public.guias_asignadas ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS guias_admin_gestion ON public.guias_ciberseguridad;
CREATE POLICY guias_admin_gestion ON public.guias_ciberseguridad FOR ALL TO authenticated
  USING (public.es_admin(auth.uid())) WITH CHECK (public.es_admin(auth.uid()));
DROP POLICY IF EXISTS guias_lectura ON public.guias_ciberseguridad;
CREATE POLICY guias_lectura ON public.guias_ciberseguridad FOR SELECT TO authenticated USING (
  public.es_admin(auth.uid()) OR (estado = 'publicada' AND (
    NOT EXISTS (SELECT 1 FROM public.guias_asignadas ga WHERE ga.id_guia = guias_ciberseguridad.id_guia)
    OR EXISTS (SELECT 1 FROM public.guias_asignadas ga JOIN public.participantes p ON p.id_participante = ga.id_participante WHERE ga.id_guia = guias_ciberseguridad.id_guia AND p.id_usuario = auth.uid())
  ))
);
DROP POLICY IF EXISTS guias_asignadas_admin ON public.guias_asignadas;
CREATE POLICY guias_asignadas_admin ON public.guias_asignadas FOR ALL TO authenticated
  USING (public.es_admin(auth.uid())) WITH CHECK (public.es_admin(auth.uid()));
DROP POLICY IF EXISTS guias_asignadas_usuario ON public.guias_asignadas;
CREATE POLICY guias_asignadas_usuario ON public.guias_asignadas FOR SELECT TO authenticated USING (
  EXISTS (SELECT 1 FROM public.participantes p WHERE p.id_participante = guias_asignadas.id_participante AND p.id_usuario = auth.uid())
);

INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES ('guias', 'guias', true, 52428800, ARRAY['application/pdf','application/msword','application/vnd.openxmlformats-officedocument.wordprocessingml.document','image/jpeg','image/png','image/webp','video/mp4','video/webm'])
ON CONFLICT (id) DO NOTHING;

DROP POLICY IF EXISTS "guias_storage_admin_insert" ON storage.objects;
CREATE POLICY "guias_storage_admin_insert" ON storage.objects FOR INSERT TO authenticated
  WITH CHECK (bucket_id = 'guias' AND public.es_admin(auth.uid()));
DROP POLICY IF EXISTS "guias_storage_public_read" ON storage.objects;
CREATE POLICY "guias_storage_public_read" ON storage.objects FOR SELECT TO authenticated
  USING (bucket_id = 'guias');
