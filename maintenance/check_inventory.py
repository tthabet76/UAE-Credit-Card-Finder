import sqlite3
conn = sqlite3.connect('credit_card_data.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE name='card_inventory'")
res = cursor.fetchone()
print(f"Result: {res}")
if res:
    cursor.execute("PRAGMA table_info(card_inventory)")
    print(cursor.fetchall())
conn.close()
