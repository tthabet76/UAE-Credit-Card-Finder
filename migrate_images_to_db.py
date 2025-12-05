import sqlite3
import json
import os

# Paths
DB_FILE = 'credit_card_data.db'
MAPPING_FILE = os.path.join('streamlit_app', 'card_image_mapping.json')

def migrate():
    print("🚀 Starting migration...")
    
    # 1. Connect to DB
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 2. Create Table
    print("📦 Creating 'card_images' table...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS card_images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_id TEXT UNIQUE NOT NULL,
        bank_name TEXT,
        card_name TEXT,
        image_url TEXT,
        local_filename TEXT,
        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 3. Load JSON Data
    if not os.path.exists(MAPPING_FILE):
        print(f"❌ Mapping file not found: {MAPPING_FILE}")
        return

    with open(MAPPING_FILE, 'r') as f:
        mapping_data = json.load(f)
        
    print(f"📂 Found {len(mapping_data)} entries in JSON.")
    
    # 4. Migrate Data
    migrated_count = 0
    skipped_count = 0
    
    # Get existing card details to populate bank/card names
    cursor.execute("SELECT id, bank_name, card_name FROM credit_cards_details")
    card_details = {str(row[0]): {'bank': row[1], 'name': row[2]} for row in cursor.fetchall()}
    
    for card_id, value in mapping_data.items():
        # Handle both string (old format) and dict (future format)
        if isinstance(value, dict):
            filename = value.get('filename')
            url = value.get('url')
        else:
            filename = value
            url = None
            
        if not filename:
            continue
            
        # Get extra details if available
        details = card_details.get(card_id, {})
        bank_name = details.get('bank')
        card_name = details.get('name')
        
        try:
            cursor.execute("""
            INSERT OR REPLACE INTO card_images (card_id, bank_name, card_name, image_url, local_filename)
            VALUES (?, ?, ?, ?, ?)
            """, (card_id, bank_name, card_name, url, filename))
            migrated_count += 1
        except Exception as e:
            print(f"⚠️ Error migrating card {card_id}: {e}")
            skipped_count += 1
            
    conn.commit()
    conn.close()
    
    print(f"✅ Migration Complete!")
    print(f"   - Migrated: {migrated_count}")
    print(f"   - Skipped: {skipped_count}")

if __name__ == "__main__":
    migrate()
