import sqlite3
import os

# Use absolute path to ROOT DB
db_path = r'c:\Users\cdf846\Documents\personal\UAE-Credit-Card-Finder\credit_card_data.db'

print(f"Connecting to: {db_path}")

try:
    if not os.path.exists(db_path):
        print("DB file not found!")
        exit()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if table exists first
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='card_images'")
    if not cursor.fetchone():
        print("Table 'card_images' does not exist in this DB.")
        conn.close()
        exit()

    print("Checking specific banks (RAKBANK, Emirates Islamic, Mashreq)...")
    banks_to_check = ['RAKBANK', 'Emirates Islamic', 'Mashreq']
    
    for bank in banks_to_check:
        cursor.execute("SELECT COUNT(*) FROM card_images WHERE bank_name = ?", (bank,))
        count = cursor.fetchone()[0]
        print(f"{bank}: {count} images")

    print("-" * 20)
    print("Checking ALL banks count in card_images:")
    cursor.execute("SELECT bank_name, COUNT(*) FROM card_images GROUP BY bank_name")
    rows = cursor.fetchall()
    for row in rows:
        print(f"{row[0]}: {row[1]}")

    conn.close()

except Exception as e:
    print(f"Error: {e}")
