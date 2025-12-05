import sqlite3

def inspect_schema():
    conn = sqlite3.connect('credit_card_data.db')
    cursor = conn.cursor()
    
    print("--- Table: card_images ---")
    cursor.execute("PRAGMA table_info(card_images)")
    columns = cursor.fetchall()
    for col in columns:
        print(col)
        
    conn.close()

if __name__ == "__main__":
    inspect_schema()
