import sqlite3
import pandas as pd
import os

# Path to the database file (relative to the streamlit app root)
# Since we run from project root, and db is in project root:
DB_FILE = 'credit_card_data.db'

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row # Access columns by name
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def fetch_all_cards():
    """Fetches all cards from the credit_cards_details table."""
    conn = get_db_connection()
    if conn:
        try:
            query = "SELECT * FROM credit_cards_details"
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Error fetching cards: {e}")
            conn.close()
            return pd.DataFrame()
    return pd.DataFrame()

def fetch_card_by_id(card_id):
    """Fetches a single card by ID."""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM credit_cards_details WHERE id = ?", (card_id,))
            row = cursor.fetchone()
            conn.close()
            return dict(row) if row else None
        except Exception as e:
            print(f"Error fetching card {card_id}: {e}")
            conn.close()
            return None
    return None

def log_interaction(card_url, user_query, ai_response, status="SUCCESS"):
    """Logs the AI interaction (optional, if we want to keep logging locally)."""
    # For now, we can skip logging or implement it if needed.
    pass
