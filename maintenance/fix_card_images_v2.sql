-- Add last_updated column
ALTER TABLE public.card_images ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP WITH TIME ZONE;
