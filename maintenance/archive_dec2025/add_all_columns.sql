-- Add all potential missing columns
ALTER TABLE public.credit_cards_details ADD COLUMN IF NOT EXISTS cashback_summary TEXT;
ALTER TABLE public.credit_cards_details ADD COLUMN IF NOT EXISTS travel_points_summary TEXT;
ALTER TABLE public.credit_cards_details ADD COLUMN IF NOT EXISTS special_discount_summary TEXT;
ALTER TABLE public.credit_cards_details ADD COLUMN IF NOT EXISTS hotel_dining_offers TEXT;
ALTER TABLE public.credit_cards_details ADD COLUMN IF NOT EXISTS golf_wellness TEXT;
ALTER TABLE public.credit_cards_details ADD COLUMN IF NOT EXISTS ai_summary TEXT;
