import sqlite3
import datetime

DB_FILE = 'credit_card_data.db'

def upgrade_schema():
    print("🚀 Starting Schema Upgrade...")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # 1. Check if columns already exist to avoid errors
        cursor.execute("PRAGMA table_info(card_images)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'scraper_image_url' in columns:
            print("⚠️ Schema already upgraded. Skipping.")
            return

        print("📦 Altering 'card_images' table...")
        
        # SQLite doesn't support RENAME COLUMN in older versions easily, 
        # but let's try the standard way first. If it fails, we do the table copy method.
        # Actually, simpler to just ADD the new columns and migrate data if needed.
        # Current columns: id, card_id, bank_name, card_name, image_url, local_filename, last_updated
        
        # Step 1: Rename image_url -> manual_image_url
        # Note: If image_url was populated by the migration script (which came from JSON), 
        # it was likely "manual" data (or at least approved data).
        try:
            cursor.execute("ALTER TABLE card_images RENAME COLUMN image_url TO manual_image_url")
            print("  - Renamed 'image_url' to 'manual_image_url'")
        except Exception as e:
            print(f"  - Rename failed (might not exist or old SQLite): {e}")
            # Fallback: Add manual_image_url and copy data? 
            # If rename failed, maybe column doesn't exist?
            pass

        # Step 2: Add new columns
        new_cols = {
            'scraper_image_url': 'TEXT',
            'manual_date': 'DATETIME',
            'scraper_date': 'DATETIME'
        }
        
        for col, dtype in new_cols.items():
            if col not in columns:
                cursor.execute(f"ALTER TABLE card_images ADD COLUMN {col} {dtype}")
                print(f"  - Added column '{col}'")
        
        # Step 3: Backfill manual_date for existing entries
        cursor.execute("UPDATE card_images SET manual_date = last_updated WHERE manual_image_url IS NOT NULL")
        print("  - Backfilled 'manual_date'")

        conn.commit()
        print("✅ Schema Upgrade Complete!")
        
    except Exception as e:
        print(f"❌ Error during upgrade: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    upgrade_schema()
