import sqlite3
import os

db_path = 'maintenance/credit_card_data.db'

if not os.path.exists(db_path):
    print(f"❌ Database not found at {db_path}")
    exit()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables found:", [t[0] for t in tables])

# Check llm_interaction_log schema
if ('llm_interaction_log',) in tables:
    print("\n✅ 'llm_interaction_log' table exists.")
    cursor.execute("PRAGMA table_info(llm_interaction_log);")
    columns = cursor.fetchall()
    print("Columns:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
        
    # Check if there is data
    cursor.execute("SELECT COUNT(*) FROM llm_interaction_log WHERE raw_page_text IS NOT NULL AND raw_page_text != '';")
    count = cursor.fetchone()[0]
    print(f"\n📊 Rows with 'raw_page_text': {count}")
    
    # Preview one row
    if count > 0:
        cursor.execute("SELECT url, raw_page_text FROM llm_interaction_log WHERE raw_page_text IS NOT NULL LIMIT 1;")
        row = cursor.fetchone()
        print(f"\nExample URL: {row[0]}")
        print(f"Text Preview: {row[1][:100]}...")
else:
    print("\n❌ 'llm_interaction_log' table does NOT exist.")

conn.close()
