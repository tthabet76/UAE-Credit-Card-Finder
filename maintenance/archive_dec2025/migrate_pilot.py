import sqlite3
import os
import mimetypes
from supabase import create_client, Client
import toml

DB_FILE = 'credit_card_data.db'
IMAGE_DIR = os.path.join('streamlit_app', 'static', 'cards')
BUCKET_NAME = 'card-images'
LIMIT = 10  # Pilot run limit

try:
    secrets = toml.load("streamlit_app/.streamlit/secrets.toml")
    SUPABASE_URL = secrets["supabase"]["url"]
    SUPABASE_KEY = secrets["supabase"]["key"]
except Exception as e:
    print(f"Error loading secrets: {e}")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print(f"Connected to Supabase. Pilot Run Limit: {LIMIT} Records.")

def get_public_url(bucket, path):
    return f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{path}"

def clean_tables():
    print("\n[Cleaning Destination Tables]...")
    # Order matters due to Foreign Keys
    tables = ["card_images", "credit_cards_details", "llm_interaction_log", "card_inventory"]
    for t in tables:
        try:
            # Delete all rows
            supabase.table(t).delete().neq("id", -1).execute() # 'neq id -1' is a hack to delete all if no 'truncate' RPC
            print(f"  [OK] Cleared {t}")
        except Exception as e:
            print(f"  [!] Could not clear {t}: {e}")

def upload_image_file(local_filename):
    file_path = os.path.join(IMAGE_DIR, local_filename)
    if not os.path.exists(file_path): return None
    
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type: mime_type = 'application/octet-stream'

    try:
        with open(file_path, 'rb') as f:
            supabase.storage.from_(BUCKET_NAME).upload(
                file=f, path=local_filename, file_options={"content-type": mime_type, "upsert": "true"}
            )
        return get_public_url(BUCKET_NAME, local_filename)
    except Exception as e:
        # verify if it exists
        return get_public_url(BUCKET_NAME, local_filename)

def sync_batch():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Inventory
    print(f"\n[1] Syncing Inventory (Limit {LIMIT})...")
    cursor.execute(f"SELECT * FROM card_inventory LIMIT {LIMIT}")
    for row in cursor.fetchall():
        try:
            supabase.table("card_inventory").insert(dict(row)).execute()
        except Exception as e: print(f"  Error: {e}")

    # 2. Logs
    print(f"\n[2] Syncing Logs (Limit {LIMIT})...")
    cursor.execute(f"SELECT * FROM llm_interaction_log LIMIT {LIMIT}")
    for row in cursor.fetchall():
        try:
            supabase.table("llm_interaction_log").insert(dict(row)).execute()
        except Exception as e: print(f"  Error: {e}")

    # 3. Details (The Parent)
    print(f"\n[3] Syncing Card Details (Limit {LIMIT})...")
    cursor.execute(f"SELECT * FROM credit_cards_details ORDER BY id ASC LIMIT {LIMIT}")
    details_rows = cursor.fetchall()
    
    synced_ids = []
    for row in details_rows:
        try:
            supabase.table("credit_cards_details").insert(dict(row)).execute()
            print(f"  [OK] Card {row['id']}")
            synced_ids.append(row['id'])
        except Exception as e: print(f"  Error: {e}")

    # 4. Images (The Child)
    print(f"\n[4] Syncing Images (Matching {len(synced_ids)} Parents)...")
    if not synced_ids:
        print("  No parents synced, skipping images.")
        return

    placeholders = ','.join('?' * len(synced_ids))
    cursor.execute(f"SELECT * FROM card_images WHERE card_id IN ({placeholders})", synced_ids)
    image_rows = cursor.fetchall()

    for row in image_rows:
        local_filename = row['local_filename']
        public_url = None
        
        if local_filename:
            public_url = upload_image_file(local_filename)
            print(f"  [Img] Uploaded {local_filename}")
        elif row['scraper_image_url']:
            public_url = row['scraper_image_url']
            
        if public_url:
            payload = dict(row)
            payload['image_url'] = public_url
            try:
                supabase.table("card_images").insert(payload).execute()
            except Exception as e: print(f"  Error linking img: {e}")

    conn.close()
    print("\n--- Pilot Run Complete ---")

if __name__ == "__main__":
    clean_tables()
    sync_batch()
