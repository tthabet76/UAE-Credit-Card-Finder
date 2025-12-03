"""
Quickly checks how many RAKBANK cards are active and lists them.
"""
import sqlite3
import os

# Connect to DB in parent directory
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'credit_card_data.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Checking RAKBANK Active Cards...")
cursor.execute("SELECT count(*) FROM card_inventory WHERE bank_name = 'RAKBANK' AND is_active = 1")
active_count = cursor.fetchone()[0]
print(f"Active RAKBANK Cards: {active_count}")

cursor.execute("SELECT card_name FROM card_inventory WHERE bank_name = 'RAKBANK' AND is_active = 1")
cards = cursor.fetchall()
for card in cards:
    print(f"- {card[0]}")

conn.close()
