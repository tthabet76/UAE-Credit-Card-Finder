import sqlite3
import os

db_path = 'credit_card_data.db'

def inspect_db():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables found: {[t[0] for t in tables]}")
    
    for table_name in tables:
        t = table_name[0]
        print(f"\n--- Schema for {t} ---")
        cursor.execute(f"PRAGMA table_info({t})")
        columns = cursor.fetchall()
        for col in columns:
            print(col) # (cid, name, type, notnull, dflt_value, pk)

    conn.close()

if __name__ == "__main__":
    inspect_db()
