-- Add the missing column to credit_cards_details
ALTER TABLE public.credit_cards_details 
ADD COLUMN IF NOT EXISTS ai_summary TEXT;
