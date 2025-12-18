import sqlite3
import os

DB_FILE = 'credit_card_data.db'

def add_column():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE credit_cards_details ADD COLUMN is_verified BOOLEAN DEFAULT 0")
        print("✅ Added 'is_verified' column to Local SQLite.")
    except Exception as e:
        if "duplicate column" in str(e).lower():
            print("ℹ️ Column 'is_verified' already exists locally.")
        else:
            print(f"❌ Error: {e}")
            
    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_column()
