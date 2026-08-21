-- =========================================================
-- CyberLey
-- Agregar fecha de nacimiento y actualizar edad mínima
-- =========================================================

ALTER TABLE public.participantes
ADD COLUMN IF NOT EXISTS fecha_nacimiento date;


ALTER TABLE public.participantes
DROP CONSTRAINT IF EXISTS participantes_edad_check;


ALTER TABLE public.participantes
ADD CONSTRAINT participantes_edad_check
CHECK (
  edad >= 14
  AND edad <= 100
);