-- Limita las nuevas descripciones a 500 caracteres sin invalidar datos históricos.
ALTER TABLE public.encuestas_dinamicas
  ADD CONSTRAINT encuestas_dinamicas_descripcion_500
  CHECK (char_length(descripcion) <= 500) NOT VALID;
