-- Make card_id unique to allow UPSERT operations
ALTER TABLE public.card_images
ADD CONSTRAINT card_images_card_id_key UNIQUE (card_id);
