import sqlite3

conn = sqlite3.connect('credit_card_data.db')
cursor = conn.cursor()
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='credit_cards_details';")
print(cursor.fetchone()[0])
conn.close()
