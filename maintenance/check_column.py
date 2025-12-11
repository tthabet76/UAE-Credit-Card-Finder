import toml
from supabase import create_client, Client

try:
    secrets = toml.load("streamlit_app/.streamlit/secrets.toml")
    url = secrets["supabase"]["url"]
    key = secrets["supabase"]["key"]
    supabase = create_client(url, key)
    
    # Try to insert a dummy record or select the column
    # easiest is to select and look at keys, or just use table info if possible, 
    # but select limit 1 is easiest test.
    
    print("Checking credit_cards_details schema...")
    res = supabase.table("credit_cards_details").select("ai_summary").limit(1).execute()
    print("✅ Column 'ai_summary' found.")
    
except Exception as e:
    print(f"❌ Error: {e}")
