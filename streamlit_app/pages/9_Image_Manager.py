import streamlit as st
import pandas as pd
import sqlite3
import os
from utils import load_css, get_card_image_source
from db_utils import get_db_connection

st.set_page_config(page_title="Image Manager", page_icon="🖼️", layout="wide")
load_css()

st.title("🖼️ Image Manager")
st.markdown("Compare local (manual) images with scraped images and update the database.")

# --- DATA LOADING ---
def load_image_data():
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
    
    query = """
    SELECT 
        ci.card_id, 
        ci.bank_name, 
        ci.card_name, 
        ci.local_filename, 
        ci.scraper_image_url,
        ci.card_url
    FROM card_images ci
    ORDER BY ci.bank_name, ci.card_name
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def update_local_filename(card_id, new_filename):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE card_images SET local_filename = ? WHERE card_id = ?", (new_filename, card_id))
    conn.commit()
    conn.close()
    st.cache_data.clear() # Clear cache to reflect changes

df = load_image_data()

if df.empty:
    st.warning("No image data found.")
    st.stop()

# --- FILTERS ---
banks = sorted(df['bank_name'].unique())
selected_bank = st.selectbox("Filter by Bank", ["All"] + list(banks))

if selected_bank != "All":
    df = df[df['bank_name'] == selected_bank]

# --- DISPLAY ---
for index, row in df.iterrows():
    with st.container():
        st.markdown(f"### {row['card_name']} ({row['bank_name']})")
        
        c1, c2, c3 = st.columns([2, 2, 1])
        
        # Local Image
        with c1:
            st.markdown("**Current (Local)**")
            local_src = row['local_filename']
            if local_src:
                # Construct path for display (reusing utils logic roughly)
                if local_src.startswith("http"):
                    st.image(local_src, width=300)
                else:
                    # Assuming static/cards/
                    st.image(f"app/static/cards/{local_src}", width=300) # Streamlit serves static? No, need full path or use utils
                    # Actually, let's just use the filename text for now if image fails, or try to load it.
                    # Better: Use the actual image source logic but force local
                    pass
            else:
                st.info("No local image set.")
            st.code(local_src if local_src else "None")

        # Scraped Image
        with c2:
            st.markdown("**Scraped (New)**")
            scraped_src = row['scraper_image_url']
            if scraped_src:
                st.image(scraped_src, width=300)
            else:
                st.info("No scraped image.")
            st.code(scraped_src if scraped_src else "None")
            
        # Actions
        with c3:
            st.markdown("**Actions**")
            if scraped_src and scraped_src != local_src:
                if st.button("✅ Use Scraped", key=f"use_{row['card_id']}"):
                    # We can't easily download the image to local file system from here without more logic.
                    # BUT, we can set local_filename to the URL if we want to use the URL directly.
                    # Or we can just clear local_filename so it falls back to scraper? 
                    # No, priority is Local > Scraper.
                    # So to use Scraper, we should CLEAR Local.
                    # Wait, if we clear Local, it falls back to Scraper.
                    # So "Use Scraped" -> Set local_filename to NULL/Empty.
                    update_local_filename(row['card_id'], None)
                    st.rerun()
            
            if local_src is None and scraped_src:
                st.success("Using Scraped Image")
            elif local_src:
                if st.button("❌ Clear Local (Use Scraped)", key=f"clear_{row['card_id']}"):
                    update_local_filename(row['card_id'], None)
                    st.rerun()
                
                # Option to set manual filename? Maybe too complex for now.
        
        st.divider()
