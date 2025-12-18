-- Add verified flag
ALTER TABLE public.credit_cards_details ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE;
