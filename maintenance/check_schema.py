import sqlite3
import pandas as pd
import os

db_path = os.path.join(os.getcwd(), 'credit_card_data.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(credit_cards_details)")
columns = cursor.fetchall()

print("Local Columns:")
for col in columns:
    print(f"- {col[1]} ({col[2]})")

conn.close()
