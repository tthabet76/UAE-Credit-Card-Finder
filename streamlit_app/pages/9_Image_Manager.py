import streamlit as st
import pandas as pd
import sqlite3
import os
from PIL import Image
from utils import load_css
from db_utils import get_db_connection

st.set_page_config(page_title="Image Manager", page_icon="🖼️", layout="wide")

# --- ENVIRONMENT CHECK REMOVED ---
# if not st.secrets.get("is_local", False): ...

load_css()

st.title("🖼️ Image Manager")
st.markdown("Compare local (manual) images with scraped images and update the database.")
st.markdown("💡 **Tip:** You can drag and drop images directly onto the 'Upload' area.")

IMAGE_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'cards')

# --- DATA LOADING ---
def load_image_data():
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
    
    # LEFT JOIN to get ALL cards, not just ones with images
    query = """
    SELECT 
        d.id as card_id, 
        d.bank_name, 
        d.card_name, 
        d.url as card_url,
        ci.local_filename, 
        ci.scraper_image_url
    FROM credit_cards_details d
    LEFT JOIN card_images ci ON d.id = ci.card_id
    ORDER BY d.bank_name, d.card_name
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def update_local_filename(card_id, new_filename, bank_name, card_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # UPSERT: Insert if not exists, otherwise update
    # We need bank_name and card_name to fill the row if it's new
    sql = """
    INSERT INTO card_images (card_id, bank_name, card_name, local_filename, scraper_date)
    VALUES (?, ?, ?, ?, datetime('now'))
    ON CONFLICT(card_id) DO UPDATE SET
        local_filename = excluded.local_filename;
    """
    cursor.execute(sql, (card_id, bank_name, card_name, new_filename))
    conn.commit()
    conn.close()
    st.cache_data.clear()

def save_uploaded_file(uploaded_file, bank_name, card_name):
    try:
        if not os.path.exists(IMAGE_DIR):
            os.makedirs(IMAGE_DIR)
            
        # Create a clean filename
        sanitized_bank = "".join(x for x in bank_name if x.isalnum())
        sanitized_card = "".join(x for x in card_name if x.isalnum())
        # Add timestamp or random to avoid cache? No, keep it deterministic for now or simple
        filename = f"{sanitized_bank}_{sanitized_card}.png"
        
        file_path = os.path.join(IMAGE_DIR, filename)
        
        image = Image.open(uploaded_file)
        image.save(file_path, "PNG")
        return filename
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None

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
        
        c1, c2, c3 = st.columns([2, 2, 2])
        
        # Local Image
        with c1:
            st.markdown("**Current (Local)**")
            local_src = row['local_filename']
            if local_src:
                if local_src.startswith("http"):
                    st.image(local_src, width=300)
                else:
                    # Try to find it in static/cards
                    local_path = os.path.join(IMAGE_DIR, local_src)
                    if os.path.exists(local_path):
                        st.image(local_path, width=300)
                    else:
                        st.error(f"File not found: {local_src}")
            else:
                st.info("No local image set.")
            st.caption(local_src if local_src else "None")

        # Scraped Image
        with c2:
            st.markdown("**Scraped (New)**")
            scraped_src = row['scraper_image_url']
            if scraped_src:
                st.image(scraped_src, width=300)
            else:
                st.info("No scraped image.")
            st.caption(scraped_src if scraped_src else "None")
            
        # Actions
        with c3:
            st.markdown("**Settings**")
            
            # 1. Source Selection
            # Determine current state
            current_mode_index = 0 if local_src else 1 # 0=Local, 1=Scraped
            
            # If no scraper image, force Local? Or just show options.
            opts = ["Local (Manual)", "Scraped"]
            mode = st.radio("Active Image Source", opts, index=current_mode_index, key=f"mode_{row['card_id']}", horizontal=True)
            
            # 2. File Uploader (Always show to allow updating local)
            st.caption("Update Local Image:")
            uploaded_file = st.file_uploader("Upload", type=['png', 'jpg', 'jpeg', 'webp'], key=f"up_{row['card_id']}", label_visibility="collapsed")
            
            # 3. Save Button
            if st.button("💾 Save Changes", key=f"save_{row['card_id']}"):
                # Logic
                final_filename = local_src # Default to keeping current
                
                # Handle Upload first
                if uploaded_file:
                    saved_name = save_uploaded_file(uploaded_file, row['bank_name'], row['card_name'])
                    if saved_name:
                        final_filename = saved_name
                        # If they uploaded, they probably want to use it
                        # But we respect the Radio button? 
                        # If they upload but select "Scraped", that's weird. 
                        # Let's assume if they upload, they want Local, unless they explicitly kept Scraped?
                        # No, simpler: Just use the Radio button to decide what goes into DB.
                
                if mode == "Scraped":
                    # User wants scraper -> Clear local
                    update_local_filename(row['card_id'], None, row['bank_name'], row['card_name'])
                    st.success("Updated to use Scraped Image.")
                    st.rerun()
                else:
                    # User wants Local
                    if final_filename:
                        update_local_filename(row['card_id'], final_filename, row['bank_name'], row['card_name'])
                        st.success("Updated to use Local Image.")
                        st.rerun()
                    else:
                        st.error("No local image exists. Please upload one first.")
        
        st.divider()
