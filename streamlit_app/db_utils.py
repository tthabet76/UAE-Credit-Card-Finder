import sqlite3
import pandas as pd
import os
import streamlit as st
from supabase import create_client, Client

# --- FEATURE FLAGS ---
# Set to FALSE to revert to Local SQLite (The "Safety Net")
SUPABASE_ENABLED = True 

# --- CONFIGURATION ---
DB_FILE = 'credit_card_data.db'

# Optimization: Singleton Supabase Client
@st.cache_resource
def get_supabase_client():
    if not SUPABASE_ENABLED: return None
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        print(f"Supabase Init Error: {e}")
        return None

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row 
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def fetch_all_cards():
    """Fetches all cards. Switches between Local and Cloud."""
    if SUPABASE_ENABLED:
        try:
            client = get_supabase_client()
            if client:
                response = client.table("credit_cards_details").select("*").execute()
                df = pd.DataFrame(response.data)
                # Ensure types match (sqlite might return ints, supabase ints)
                return df
        except Exception as e:
            print(f"Supabase Fetch Error: {e}. Falling back to Local?")
            # Optional: Fallback logic or just fail
            pass
    
    # Fallback / Local Mode
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
    if SUPABASE_ENABLED:
        try:
            client = get_supabase_client()
            if client:
                response = client.table("credit_cards_details").select("*").eq("id", card_id).execute()
                if response.data:
                    return response.data[0]
        except Exception as e:
            print(f"Supabase Fetch ID Error: {e}")

    # Local Mode
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
    """Logs the AI interaction."""
    pass
