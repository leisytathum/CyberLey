DROP POLICY IF EXISTS guias_completadas_admin_gestion ON public.guias_completadas;
CREATE POLICY guias_completadas_admin_gestion ON public.guias_completadas
  FOR ALL TO authenticated
  USING (public.es_admin(auth.uid()))
  WITH CHECK (public.es_admin(auth.uid()));
