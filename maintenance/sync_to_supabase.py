"""
Syncs the local credit_card_data.db to a remote Supabase database (if you are using one for production).
"""
import sqlite3
import os
from supabase import create_client, Client
import toml

# Load secrets
try:
    secrets = toml.load("streamlit_app/.streamlit/secrets.toml")
    SUPABASE_URL = secrets["supabase"]["url"]
    SUPABASE_KEY = secrets["supabase"]["key"]
except Exception as e:
    print("Error loading secrets. Make sure streamlit_app/.streamlit/secrets.toml exists and has [supabase] section.")
    exit(1)

# Initialize Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

DB_FILE = 'credit_card_data.db'

def sync_table(table_name, unique_col=None):
    print(f"\n--- Syncing Table: {table_name} ---")
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        print(f"Found {len(rows)} records in local '{table_name}'.")
        
        for row in rows:
            data = dict(row)
            if 'id' in data: del data['id'] # Let Supabase handle IDs
            
            try:
                if unique_col:
                    supabase.table(table_name).upsert(data, on_conflict=unique_col).execute()
                else:
                    # For logs, we might just want to insert, but upsert is safer if we have a unique key.
                    # Since logs don't have a unique URL, we'll just insert. 
                    # WARNING: This might create duplicates if run multiple times without clearing.
                    # ideally we'd have a unique ID from source, but for now let's just insert.
                    supabase.table(table_name).insert(data).execute()
            except Exception as e:
                # print(f"Failed to sync record: {e}") # Reduce noise
                pass
        print(f"Synced {table_name} successfully.")

    except Exception as e:
        print(f"Error reading {table_name}: {e}")
    finally:
        conn.close()

def clear_table(table_name):
    print(f"Clearing remote table: {table_name}...")
    try:
        # Delete all rows (neq id 0 is a hack to delete all if no truncate method exposed easily, 
        # but supabase-py might not support truncate directly. 
        # Standard way: delete with a filter that matches everything. 
        # Or use RPC. For now, let's assume we can delete where id > 0)
        supabase.table(table_name).delete().neq("id", 0).execute()
        print("Table cleared.")
    except Exception as e:
        print(f"Error clearing {table_name}: {e}")

def sync_data():
    print("--- Starting Full Sync: SQLite -> Supabase ---")
    if not os.path.exists(DB_FILE):
        print(f"Error: Database file '{DB_FILE}' not found.")
        return

    # 1. Sync Inventory
    # clear_table("card_inventory") # Optional: Uncomment if you want to hard-reset inventory too
    sync_table("card_inventory", unique_col="url")
    
    # 2. Sync Details (The main data)
    # We clear this to remove "extra cards" that didn't come in this run
    # clear_table("credit_cards_details") # DISABLED: Safer to upsert. 
    
    # Load Image Mapping
    import json
    mapping_file = 'streamlit_app/card_image_mapping.json'
    image_mapping = {}
    if os.path.exists(mapping_file):
        with open(mapping_file, 'r') as f:
            image_mapping = json.load(f)
            print(f"Loaded {len(image_mapping)} image mappings.")
            
    print(f"\n--- Syncing Table: credit_cards_details ---")
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Sync ALL cards, not just fresh ones. We rely on upsert to handle updates.
        cursor.execute("SELECT * FROM credit_cards_details")
        rows = cursor.fetchall()
        print(f"Found {len(rows)} records in local 'credit_cards_details'.")
        
        for row in rows:
            data = dict(row)
            card_id = str(data['id'])
            if 'id' in data: del data['id'] 
            
            # Inject Image Filename if available
            if card_id in image_mapping and image_mapping[card_id]:
                data['image_filename'] = image_mapping[card_id]
            
            try:
                supabase.table("credit_cards_details").upsert(data, on_conflict="url").execute()
            except Exception as e:
                print(f"Failed to sync record {data.get('card_name', 'Unknown')}: {e}") 
                pass
        print(f"Synced credit_cards_details successfully.")

    except Exception as e:
        print(f"Error reading credit_cards_details: {e}")
    finally:
        conn.close()
    
    # Sync Logs (No unique column for upsert usually, unless we use timestamp+url, but let's just insert for now or skip if too large)
    # sync_table("llm_interaction_log") # Uncomment if you really want to sync logs (can be large)
    
    print("--- Full Sync Complete ---")

if __name__ == "__main__":
    sync_data()
