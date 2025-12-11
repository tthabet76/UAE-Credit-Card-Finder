import sqlite3
import pandas as pd

conn = sqlite3.connect('credit_card_data.db')
cards = pd.read_sql_query("SELECT id FROM credit_cards_details LIMIT 5", conn)
images = pd.read_sql_query("SELECT card_id FROM card_images LIMIT 5", conn)

print("--- Cards IDs ---")
print(cards)
print(cards.dtypes)

print("\n--- Images Card IDs ---")
print(images)
print(images.dtypes)
conn.close()
