import sqlite3
import pandas as pd
import os

DB_FILE = 'credit_card_data.db'

def check_structure():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("--- Found Tables ---")
    for t in tables:
        print(f"- {t[0]}")
        
        # Get info for each
        print(f"  Schema for {t[0]}:")
        cursor.execute(f"PRAGMA table_info({t[0]})")
        cols = cursor.fetchall()
        for c in cols:
            print(f"    {c[1]} ({c[2]})")
        print("")

    conn.close()

if __name__ == "__main__":
    check_structure()
