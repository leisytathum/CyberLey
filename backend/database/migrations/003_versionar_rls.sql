-- Políticas reproducibles para CyberLey. Ejecutar después de 001 y 002.
CREATE OR REPLACE FUNCTION public.es_admin(uid uuid)
RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path = public
AS $$ SELECT EXISTS (SELECT 1 FROM public.perfiles WHERE id = uid AND rol = 'admin') $$;

ALTER TABLE public.perfiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.participantes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.respuestas_encuesta_ciberseguridad ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reportes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.guias_ciberseguridad ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.recomendaciones ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.guias_completadas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notificaciones ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS perfiles_lectura ON public.perfiles;
CREATE POLICY perfiles_lectura ON public.perfiles FOR SELECT TO authenticated USING (id = auth.uid() OR public.es_admin(auth.uid()));
DROP POLICY IF EXISTS perfiles_admin_actualiza ON public.perfiles;
CREATE POLICY perfiles_admin_actualiza ON public.perfiles FOR UPDATE TO authenticated USING (public.es_admin(auth.uid())) WITH CHECK (public.es_admin(auth.uid()));
DROP POLICY IF EXISTS perfiles_admin_inserta ON public.perfiles;
CREATE POLICY perfiles_admin_inserta ON public.perfiles FOR INSERT TO authenticated WITH CHECK (public.es_admin(auth.uid()));

DROP POLICY IF EXISTS participantes_lectura ON public.participantes;
CREATE POLICY participantes_lectura ON public.participantes FOR SELECT TO authenticated USING (id_usuario = auth.uid() OR public.es_admin(auth.uid()));
DROP POLICY IF EXISTS participantes_admin_actualiza ON public.participantes;
CREATE POLICY participantes_admin_actualiza ON public.participantes FOR UPDATE TO authenticated USING (public.es_admin(auth.uid())) WITH CHECK (public.es_admin(auth.uid()));
DROP POLICY IF EXISTS participantes_admin_inserta ON public.participantes;
CREATE POLICY participantes_admin_inserta ON public.participantes FOR INSERT TO authenticated WITH CHECK (public.es_admin(auth.uid()));

DROP POLICY IF EXISTS respuestas_lectura ON public.respuestas_encuesta_ciberseguridad;
CREATE POLICY respuestas_lectura ON public.respuestas_encuesta_ciberseguridad FOR SELECT TO authenticated USING (id_usuario = auth.uid() OR public.es_admin(auth.uid()));
DROP POLICY IF EXISTS respuestas_insertar_propias ON public.respuestas_encuesta_ciberseguridad;
CREATE POLICY respuestas_insertar_propias ON public.respuestas_encuesta_ciberseguridad FOR INSERT TO authenticated WITH CHECK (id_usuario = auth.uid());
DROP POLICY IF EXISTS respuestas_admin_actualiza ON public.respuestas_encuesta_ciberseguridad;
CREATE POLICY respuestas_admin_actualiza ON public.respuestas_encuesta_ciberseguridad FOR UPDATE TO authenticated USING (public.es_admin(auth.uid())) WITH CHECK (public.es_admin(auth.uid()));
DROP POLICY IF EXISTS respuestas_admin_inserta ON public.respuestas_encuesta_ciberseguridad;
CREATE POLICY respuestas_admin_inserta ON public.respuestas_encuesta_ciberseguridad FOR INSERT TO authenticated WITH CHECK (public.es_admin(auth.uid()));

DROP POLICY IF EXISTS guias_lectura ON public.guias_ciberseguridad;
CREATE POLICY guias_lectura ON public.guias_ciberseguridad FOR SELECT TO authenticated USING (true);

DROP POLICY IF EXISTS guias_completadas_lectura ON public.guias_completadas;
CREATE POLICY guias_completadas_lectura ON public.guias_completadas FOR SELECT TO authenticated USING (public.es_admin(auth.uid()) OR EXISTS (SELECT 1 FROM public.participantes p WHERE p.id_participante = guias_completadas.id_participante AND p.id_usuario = auth.uid()));
DROP POLICY IF EXISTS guias_completadas_insertar ON public.guias_completadas;
CREATE POLICY guias_completadas_insertar ON public.guias_completadas FOR INSERT TO authenticated WITH CHECK (EXISTS (SELECT 1 FROM public.participantes p WHERE p.id_participante = guias_completadas.id_participante AND p.id_usuario = auth.uid()));

DROP POLICY IF EXISTS reportes_admin ON public.reportes;
CREATE POLICY reportes_admin ON public.reportes FOR ALL TO authenticated USING (public.es_admin(auth.uid())) WITH CHECK (public.es_admin(auth.uid()));
DROP POLICY IF EXISTS recomendaciones_lectura ON public.recomendaciones;
CREATE POLICY recomendaciones_lectura ON public.recomendaciones FOR SELECT TO authenticated USING (public.es_admin(auth.uid()) OR EXISTS (SELECT 1 FROM public.participantes p WHERE p.id_participante = recomendaciones.id_participante AND p.id_usuario = auth.uid()));
DROP POLICY IF EXISTS notificaciones_lectura ON public.notificaciones;
CREATE POLICY notificaciones_lectura ON public.notificaciones FOR SELECT TO authenticated USING (id_usuario = auth.uid() OR public.es_admin(auth.uid()));
