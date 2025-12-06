import sqlite3
import os

db_path = r'C:\Users\cdf846\Documents\personal\UAE-Credit-Card-Finder\credit_card_data.db'

if not os.path.exists(db_path):
    print(f"❌ Database not found at {db_path}")
    exit()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print(f"Checking schema for 'credit_cards_details' in {db_path}...")

try:
    cursor.execute("PRAGMA table_info(credit_cards_details);")
    columns = cursor.fetchall()
    print(f"Found {len(columns)} columns:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
except Exception as e:
    print(f"Error: {e}")

conn.close()
