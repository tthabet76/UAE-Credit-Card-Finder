"""
Prints all details stored in the database for a specific card (e.g., RAKBANK World).
"""
import sqlite3
import os

# Connect to DB in parent directory
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'credit_card_data.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Checking RAKBANK World Credit Card...")
cursor.execute("SELECT * FROM card_inventory WHERE bank_name = 'RAKBANK' AND card_name LIKE '%World%'")
rows = cursor.fetchall()

if not rows:
    print("No matching card found.")
else:
    for row in rows:
        print(f"ID: {row[0]}")
        print(f"Bank: {row[1]}")
        print(f"Name: {row[2]}")
        print(f"URL: {row[3]}")
        print(f"Active: {row[4]}")
        print(f"First Discovered: {row[5]}")
        print("-" * 20)

conn.close()
