import sqlite3
import os

db_path = 'credit_card_data.db'

def add_column():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(credit_cards_details)")
        cols = [c[1] for c in cursor.fetchall()]
        
        if 'ai_summary' not in cols:
            print("Adding 'ai_summary' column...")
            cursor.execute("ALTER TABLE credit_cards_details ADD COLUMN ai_summary TEXT")
            conn.commit()
            print("Column added successfully.")
        else:
            print("'ai_summary' column already exists.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_column()
