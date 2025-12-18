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
            print(f"  Attempting to upload {local_filename}...")
            # Upsert=true replaces existing
            response = supabase.storage.from_(BUCKET_NAME).upload(
                file=f,
                path=local_filename,
                file_options={"content-type": mime_type, "upsert": "true"}
            )
        return get_public_url(BUCKET_NAME, local_filename)
    except Exception as e:
        # If error is 409 (duplicate) and upsert is true, it shouldn't happen.
        # But if it does, we can assume it's there.
        print(f"  Error uploading {local_filename}: {e}")
        return None

def test_single_migration():
    print("--- Starting Single Image Test ---")
    
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Select 1 image that definitely has a local file
    cursor.execute("SELECT * FROM card_images WHERE local_filename IS NOT NULL LIMIT 1")
    row = cursor.fetchone()
    
    if not row:
        print("No local images found to test.")
        return

    card_id = row['card_id']
    local_filename = row['local_filename']
    scraper_url = row['scraper_image_url']
    
    print(f"Testing with Card ID: {card_id}, File: {local_filename}")

    # --- STEP 0: Sync Parent Record (Fix FK Error) ---
    print(f"  Syncing parent card details for ID {card_id}...")
    cursor.execute("SELECT * FROM credit_cards_details WHERE id = ?", (card_id,))
    parent_row = cursor.fetchone()
    if parent_row:
        parent_data = dict(parent_row)
        # Assuming ID needs to be explicit or we trust the sequence?
        # Supabase usually respects ID in INSERT if we provide it?
        # Let's try to include it.
        try:
            supabase.table("credit_cards_details").upsert(parent_data).execute()
            print("  [OK] Parent record synced.")
        except Exception as e:
            print(f"  [X] Failed to sync parent: {e}")
    else:
        print("  [e] Local parent record not found!?")

    public_url = upload_image(local_filename)
            
    if public_url:
        print(f"  [OK] Upload Success! URL: {public_url}")
        
        # Test DB Update
        payload = {
            "card_id": card_id,
            "bank_name": row['bank_name'],
            "card_name": row['card_name'],
            "image_url": public_url,
            "local_filename": local_filename,
            "scraper_image_url": scraper_url
        }
        
        try:
            print("  Updating Database Record...")
            # We must enable upsert on_conflict card_id.
            # Make sure card_id has a UNIQUE constraint in Supabase if using on_conflict.
            # Or just rely on ID if we knew it.
            supabase.table("card_images").upsert(payload, on_conflict="card_id").execute()
            print("  [OK] Database Update Success!")
        except Exception as e:
            print(f"  [X] Error updating DB: {e}")
    else:
        print("  [X] Upload Failed.")

    print("\n--- Test Complete ---")
    conn.close()

if __name__ == "__main__":
    test_single_migration()
