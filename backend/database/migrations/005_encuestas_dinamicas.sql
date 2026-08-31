-- Encuestas configurables, aplicaciones por usuario y respuestas inmutables.
CREATE TABLE IF NOT EXISTS public.encuestas_dinamicas (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  titulo text NOT NULL CHECK (length(trim(titulo)) >= 3),
  descripcion text NOT NULL DEFAULT '' CHECK (char_length(descripcion) <= 500),
  estado text NOT NULL DEFAULT 'borrador' CHECK (estado IN ('borrador','publicada','cerrada')),
  creada_por uuid NOT NULL REFERENCES public.perfiles(id),
  fecha_creacion timestamptz NOT NULL DEFAULT now(),
  fecha_publicacion timestamptz
);

CREATE TABLE IF NOT EXISTS public.preguntas_dinamicas (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  id_encuesta uuid NOT NULL REFERENCES public.encuestas_dinamicas(id) ON DELETE CASCADE,
  texto text NOT NULL CHECK (length(trim(texto)) >= 3),
  tipo text NOT NULL CHECK (tipo IN ('opcion','escala','si_no','texto')),
  requerida boolean NOT NULL DEFAULT true,
  orden integer NOT NULL CHECK (orden > 0),
  opciones jsonb NOT NULL DEFAULT '[]'::jsonb,
  UNIQUE (id_encuesta, orden)
);

CREATE TABLE IF NOT EXISTS public.aplicaciones_encuesta (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  id_encuesta uuid NOT NULL REFERENCES public.encuestas_dinamicas(id),
  id_usuario uuid NOT NULL REFERENCES public.perfiles(id),
  fecha_respuesta timestamptz NOT NULL DEFAULT now(),
  respuestas jsonb NOT NULL,
  puntaje integer NOT NULL DEFAULT 0 CHECK (puntaje >= 0),
  puntaje_maximo integer NOT NULL DEFAULT 0 CHECK (puntaje_maximo >= 0),
  porcentaje_riesgo numeric(5,2) NOT NULL DEFAULT 0,
  clasificacion_riesgo text NOT NULL CHECK (clasificacion_riesgo IN ('bajo','medio','alto')),
  observacion text NOT NULL,
  UNIQUE (id_encuesta, id_usuario)
);

ALTER TABLE public.encuestas_dinamicas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.preguntas_dinamicas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.aplicaciones_encuesta ENABLE ROW LEVEL SECURITY;

CREATE POLICY encuestas_dinamicas_admin ON public.encuestas_dinamicas FOR ALL TO authenticated USING (public.es_admin(auth.uid())) WITH CHECK (public.es_admin(auth.uid()));
CREATE POLICY encuestas_dinamicas_usuario_lectura ON public.encuestas_dinamicas FOR SELECT TO authenticated USING (estado = 'publicada');
CREATE POLICY preguntas_dinamicas_admin ON public.preguntas_dinamicas FOR ALL TO authenticated USING (public.es_admin(auth.uid())) WITH CHECK (public.es_admin(auth.uid()));
CREATE POLICY preguntas_dinamicas_usuario_lectura ON public.preguntas_dinamicas FOR SELECT TO authenticated USING (EXISTS (SELECT 1 FROM public.encuestas_dinamicas e WHERE e.id = id_encuesta AND e.estado = 'publicada'));
CREATE POLICY aplicaciones_encuesta_admin_lectura ON public.aplicaciones_encuesta FOR SELECT TO authenticated USING (public.es_admin(auth.uid()));
CREATE POLICY aplicaciones_encuesta_usuario_lectura ON public.aplicaciones_encuesta FOR SELECT TO authenticated USING (id_usuario = auth.uid());
CREATE POLICY aplicaciones_encuesta_usuario_inserta ON public.aplicaciones_encuesta FOR INSERT TO authenticated WITH CHECK (id_usuario = auth.uid() AND EXISTS (SELECT 1 FROM public.encuestas_dinamicas e WHERE e.id = id_encuesta AND e.estado = 'publicada'));

CREATE INDEX IF NOT EXISTS idx_preguntas_dinamicas_encuesta ON public.preguntas_dinamicas(id_encuesta, orden);
CREATE INDEX IF NOT EXISTS idx_aplicaciones_encuesta ON public.aplicaciones_encuesta(id_encuesta, fecha_respuesta DESC);
