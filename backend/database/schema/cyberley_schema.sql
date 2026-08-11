-- =========================================================
-- CYBERLEY - ESQUEMA DE BASE DE DATOS
-- =========================================================
--
-- Archivo de referencia de la estructura actualmente
-- utilizada en Supabase.
--
-- IMPORTANTE:
-- Este archivo documenta el esquema del proyecto.
-- No debe ejecutarse directamente como una migración.
--
-- Las modificaciones futuras deben colocarse en:
-- backend/database/migrations/
-- =========================================================
CREATE TABLE public.perfiles (
  id uuid NOT NULL,
  nombre_completo character varying NOT NULL,
  rol character varying NOT NULL CHECK (rol::text = ANY (ARRAY['admin'::character varying, 'usuario'::character varying]::text[])),
  foto_url text,
  fecha_creacion timestamp without time zone DEFAULT now(),
  CONSTRAINT perfiles_pkey PRIMARY KEY (id),
  CONSTRAINT perfiles_id_fkey FOREIGN KEY (id) REFERENCES auth.users(id)
);
CREATE TABLE public.participantes (
  id_participante uuid NOT NULL DEFAULT gen_random_uuid(),
  id_usuario uuid,
  nombre_completo character varying NOT NULL,
  edad integer CHECK (edad >= 10 AND edad <= 100),
  genero character varying,
  ciudad character varying,
  nivel_educativo character varying,
  fecha_registro timestamp without time zone DEFAULT now(),
  CONSTRAINT participantes_pkey PRIMARY KEY (id_participante),
  CONSTRAINT participantes_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.perfiles(id)
);
CREATE TABLE public.encuestas (
  id_encuesta uuid NOT NULL DEFAULT gen_random_uuid(),
  id_participante uuid,
  fecha_aplicacion timestamp without time zone DEFAULT now(),
  estado character varying DEFAULT 'completada'::character varying,
  CONSTRAINT encuestas_pkey PRIMARY KEY (id_encuesta),
  CONSTRAINT encuestas_id_participante_fkey FOREIGN KEY (id_participante) REFERENCES public.participantes(id_participante)
);
CREATE TABLE public.respuestas_encuesta (
  id_respuesta uuid NOT NULL DEFAULT gen_random_uuid(),
  id_encuesta uuid,
  usa_misma_contrasena boolean NOT NULL,
  usa_wifi_publico boolean NOT NULL,
  reconoce_phishing character varying NOT NULL CHECK (reconoce_phishing::text = ANY (ARRAY['si'::character varying, 'no'::character varying, 'a_veces'::character varying]::text[])),
  usa_doble_factor boolean NOT NULL,
  tiene_antivirus boolean NOT NULL,
  actualiza_contrasenas boolean NOT NULL,
  comparte_info_redes boolean NOT NULL,
  nivel_conocimiento character varying NOT NULL CHECK (nivel_conocimiento::text = ANY (ARRAY['bajo'::character varying, 'medio'::character varying, 'alto'::character varying]::text[])),
  CONSTRAINT respuestas_encuesta_pkey PRIMARY KEY (id_respuesta),
  CONSTRAINT respuestas_encuesta_id_encuesta_fkey FOREIGN KEY (id_encuesta) REFERENCES public.encuestas(id_encuesta)
);
CREATE TABLE public.resultados_riesgo (
  id_resultado uuid NOT NULL DEFAULT gen_random_uuid(),
  id_encuesta uuid,
  puntaje_riesgo numeric NOT NULL,
  clasificacion_riesgo character varying NOT NULL CHECK (clasificacion_riesgo::text = ANY (ARRAY['bajo'::character varying, 'medio'::character varying, 'alto'::character varying]::text[])),
  observacion text,
  fecha_calculo timestamp without time zone DEFAULT now(),
  CONSTRAINT resultados_riesgo_pkey PRIMARY KEY (id_resultado),
  CONSTRAINT resultados_riesgo_id_encuesta_fkey FOREIGN KEY (id_encuesta) REFERENCES public.encuestas(id_encuesta)
);
CREATE TABLE public.guias_ciberseguridad (
  id_guia uuid NOT NULL DEFAULT gen_random_uuid(),
  titulo character varying NOT NULL,
  categoria character varying NOT NULL,
  descripcion text,
  contenido text,
  nivel_recomendado character varying CHECK (nivel_recomendado::text = ANY (ARRAY['bajo'::character varying, 'medio'::character varying, 'alto'::character varying, 'general'::character varying]::text[])),
  fecha_creacion timestamp without time zone DEFAULT now(),
  CONSTRAINT guias_ciberseguridad_pkey PRIMARY KEY (id_guia)
);
CREATE TABLE public.recomendaciones (
  id_recomendacion uuid NOT NULL DEFAULT gen_random_uuid(),
  id_participante uuid,
  id_guia uuid,
  titulo character varying NOT NULL,
  descripcion text,
  estado character varying DEFAULT 'pendiente'::character varying CHECK (estado::text = ANY (ARRAY['pendiente'::character varying, 'completada'::character varying]::text[])),
  fecha_creacion timestamp without time zone DEFAULT now(),
  CONSTRAINT recomendaciones_pkey PRIMARY KEY (id_recomendacion),
  CONSTRAINT recomendaciones_id_participante_fkey FOREIGN KEY (id_participante) REFERENCES public.participantes(id_participante),
  CONSTRAINT recomendaciones_id_guia_fkey FOREIGN KEY (id_guia) REFERENCES public.guias_ciberseguridad(id_guia)
);
CREATE TABLE public.reportes (
  id_reporte uuid NOT NULL DEFAULT gen_random_uuid(),
  generado_por uuid,
  tipo_reporte character varying NOT NULL,
  descripcion text,
  fecha_generacion timestamp without time zone DEFAULT now(),
  CONSTRAINT reportes_pkey PRIMARY KEY (id_reporte),
  CONSTRAINT reportes_generado_por_fkey FOREIGN KEY (generado_por) REFERENCES public.perfiles(id)
);
CREATE TABLE public.notificaciones (
  id_notificacion uuid NOT NULL DEFAULT gen_random_uuid(),
  id_usuario uuid,
  titulo character varying NOT NULL,
  mensaje text NOT NULL,
  leida boolean DEFAULT false,
  fecha_creacion timestamp without time zone DEFAULT now(),
  CONSTRAINT notificaciones_pkey PRIMARY KEY (id_notificacion),
  CONSTRAINT notificaciones_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.perfiles(id)
);
CREATE TABLE public.guias_completadas (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  id_participante uuid,
  id_guia uuid,
  fecha_completada timestamp without time zone DEFAULT now(),
  CONSTRAINT guias_completadas_pkey PRIMARY KEY (id),
  CONSTRAINT guias_completadas_id_participante_fkey FOREIGN KEY (id_participante) REFERENCES public.participantes(id_participante),
  CONSTRAINT guias_completadas_id_guia_fkey FOREIGN KEY (id_guia) REFERENCES public.guias_ciberseguridad(id_guia)
);
CREATE TABLE public.respuestas_encuesta_ciberseguridad (
  id_respuesta uuid NOT NULL DEFAULT gen_random_uuid(),
  id_usuario uuid,
  fecha_respuesta timestamp with time zone DEFAULT now(),
  usa_nube text,
  plataforma_nube text,
  contenido_nube text,
  nivel_conocimiento text,
  manejo_ciberseguridad integer,
  frecuencia_info_seguridad text,
  reconoce_phishing text,
  identifica_herramientas_seguridad text,
  estado_antivirus text,
  tipo_conexion text,
  estabilidad_conexion integer,
  frecuencia_fallas_internet text,
  cambio_contrasenas_anual text,
  reutiliza_contrasenas text,
  importancia_actualizar_contrasenas integer,
  puntaje_riesgo integer,
  clasificacion_riesgo text,
  observacion text,
  CONSTRAINT respuestas_encuesta_ciberseguridad_pkey PRIMARY KEY (id_respuesta),
  CONSTRAINT respuestas_encuesta_ciberseguridad_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.perfiles(id)
);