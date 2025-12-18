import sqlite3
import pandas as pd
import os

DB_FILE = os.path.join(os.getcwd(), 'credit_card_data.db')

def check_counts():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    tables = ["card_inventory", "credit_cards_details", "card_images", "llm_interaction_log"]
    
    print("--- Local Record Counts ---")
    for t in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {t}")
            count = cursor.fetchone()[0]
            print(f"{t}: {count}")
        except Exception as e:
            print(f"{t}: Error ({e})")
            
    conn.close()

if __name__ == "__main__":
    check_counts()
