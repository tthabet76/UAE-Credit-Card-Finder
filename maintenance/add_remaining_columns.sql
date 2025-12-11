-- Add ALL remaining columns to match local schema
ALTER TABLE public.credit_cards_details ADD COLUMN IF NOT EXISTS min_salary_numeric FLOAT;
ALTER TABLE public.credit_cards_details ADD COLUMN IF NOT EXISTS max_cashback_rate FLOAT;
ALTER TABLE public.credit_cards_details ADD COLUMN IF NOT EXISTS is_uncapped BOOLEAN;
ALTER TABLE public.credit_cards_details ADD COLUMN IF NOT EXISTS cashback_type TEXT;
ALTER TABLE public.credit_cards_details ADD COLUMN IF NOT EXISTS foreign_currency_fee TEXT;
