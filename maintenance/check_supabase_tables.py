import toml
from supabase import create_client, Client
import os

try:
    secrets = toml.load("streamlit_app/.streamlit/secrets.toml")
    SUPABASE_URL = secrets["supabase"]["url"]
    SUPABASE_KEY = secrets["supabase"]["key"]
except Exception as e:
    print(f"Error loading secrets: {e}")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print(f"Connected to Supabase: {SUPABASE_URL}")

def check_table(table_name):
    print(f"Checking table '{table_name}'...")
    try:
        # Try to select 1 row
        response = supabase.table(table_name).select("*").limit(1).execute()
        print(f"  [OK] Table '{table_name}' exists.")
        return True
    except Exception as e:
        print(f"  [X] Table '{table_name}' seemingly missing or inaccessible. Error: {str(e)[:100]}")
        return False

tables_to_check = ["credit_cards_details", "card_images", "card_inventory", "llm_interaction_log"]
results = {}

for t in tables_to_check:
    results[t] = check_table(t)

print("\n--- Summary ---")
if not results["card_images"]:
    print("ALERT: 'card_images' table is MISSING. You need to create it.")
else:
    print("Ready to migrate.")
