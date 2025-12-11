import sqlite3
import os
import mimetypes
from supabase import create_client, Client
import toml

# --- Configuration ---
DB_FILE = 'credit_card_data.db'
IMAGE_DIR = os.path.join('streamlit_app', 'static', 'cards')
BUCKET_NAME = 'card-images'

try:
    secrets = toml.load("streamlit_app/.streamlit/secrets.toml")
    SUPABASE_URL = secrets["supabase"]["url"]
    SUPABASE_KEY = secrets["supabase"]["key"]
except Exception as e:
    print(f"Error loading secrets: {e}")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print(f"Connected to Supabase: {SUPABASE_URL}")

def get_public_url(bucket, path):
    return f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{path}"

def upload_image(local_filename):
    """Uploads a local file to Supabase Storage and returns the public URL."""
    file_path = os.path.join(IMAGE_DIR, local_filename)
    if not os.path.exists(file_path):
        print(f"  Warning: Local file not found: {file_path}")
        return None

    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type: mime_type = 'application/octet-stream'

    try:
        with open(file_path, 'rb') as f:
            # Upsert=true replaces existing
            supabase.storage.from_(BUCKET_NAME).upload(
                file=f,
                path=local_filename,
                file_options={"content-type": mime_type, "upsert": "true"}
            )
        return get_public_url(BUCKET_NAME, local_filename)
    except Exception as e:
        print(f"  Error uploading {local_filename}: {e}")
        return None

def sync_table(table_name, unique_col="id"):
    """Generic function to sync a table from SQLite to Supabase."""
    print(f"\n[Syncing Table] {table_name}...")
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        print(f"  Found {len(rows)} records locally.")
        
        synced_count = 0
        for row in rows:
            data = dict(row)
            try:
                # Use upsert. 
                # Note: For some tables like Logs, we might just want to insert? 
                # But to avoid dupes on re-run, upsert on ID is safer if IDs match.
                # Assuming local DB IDs match Supabase IDs (or we force them).
                supabase.table(table_name).upsert(data).execute()
                synced_count += 1
            except Exception as e:
                print(f"  [X] Failed to record {data.get(unique_col, '?')}: {e}")
                
        print(f"  ✅ Synced {synced_count}/{len(rows)} records.")
    except Exception as e:
        print(f"  Error reading local table {table_name}: {e}")
    finally:
        conn.close()

def migrate():
    print("--- Starting Full Migration (4 Tables + Images) ---")
    
    # 1. Sync Inventory (Independent)
    sync_table("card_inventory", unique_col="url")
    
    # 2. Sync Logs (Independent)
    sync_table("llm_interaction_log", unique_col="id")
    
    # 3. Sync Details (Main)
    sync_table("credit_cards_details", unique_col="id")

    # 4. Sync Images (Dependent on Details)
    print("\n[Syncing Table] card_images + Uploading Files...")
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM card_images")
    image_rows = cursor.fetchall()
    print(f"  Found {len(image_rows)} local image records.")
    
    synced_images = 0
    for row in image_rows:
        card_id = row['card_id']
        local_filename = row['local_filename']
        scraper_url = row['scraper_image_url']
        
        public_url = None
        
        if local_filename:
            print(f"  Uploading {local_filename}...")
            public_url = upload_image(local_filename)
        elif scraper_url:
            print(f"  Using Scraper URL for {card_id}...")
            public_url = scraper_url
            
        if public_url:
            payload = {
                "card_id": card_id,
                "bank_name": row['bank_name'],
                "card_name": row['card_name'],
                "image_url": public_url,
                "local_filename": local_filename,
                "scraper_image_url": scraper_url
            }
            try:
                supabase.table("card_images").upsert(payload, on_conflict="card_id").execute()
                synced_images += 1
            except Exception as e:
                print(f"  [X] Error db-sync card {card_id}: {e}")
        else:
            print(f"  Skipping {card_id} (No source).")

    print(f"  ✅ Synced {synced_images} image records.")
    print("\n--- Migration Complete ---")
    conn.close()

if __name__ == "__main__":
    migrate()
