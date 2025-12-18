import sqlite3

conn = sqlite3.connect('credit_card_data.db')
cursor = conn.cursor()
cursor.execute("SELECT card_name, url FROM credit_cards_details WHERE bank_name='SIB' AND card_name LIKE '%Smiles%'")
rows = cursor.fetchall()
for r in rows:
    print(f"Card: {r[0]}")
    print(f"URL: {r[1]}")
conn.close()
