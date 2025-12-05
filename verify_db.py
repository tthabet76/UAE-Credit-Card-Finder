import sqlite3
import os

DB_FILE = 'credit_card_data.db'

def verify():
    if not os.path.exists(DB_FILE):
        print("❌ DB file not found!")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM card_images")
        count = cursor.fetchone()[0]
        print(f"✅ 'card_images' table has {count} rows.")
        
        cursor.execute("SELECT * FROM card_images LIMIT 1")
        row = cursor.fetchone()
        print(f"🔍 Sample row: {row}")
        
    except Exception as e:
        print(f"❌ Error querying DB: {e}")
        
    conn.close()

if __name__ == "__main__":
    verify()
