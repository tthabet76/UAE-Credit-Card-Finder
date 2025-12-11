import os
from supabase import create_client, Client
import toml

try:
    secrets = toml.load("streamlit_app/.streamlit/secrets.toml")
    SUPABASE_URL = secrets["supabase"]["url"]
    SUPABASE_KEY = secrets["supabase"]["key"]
except Exception as e:
    print(f"Error loading secrets: {e}")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

tables = ["card_inventory", "llm_interaction_log", "credit_cards_details", "card_images"]

print("--- Supabase Live Counts ---")
for t in tables:
    try:
        # count='exact', head=True returns count without data
        res = supabase.table(t).select("*", count="exact").execute()
        print(f"{t}: {res.count}")
    except Exception as e:
        print(f"{t}: Error {e}")
