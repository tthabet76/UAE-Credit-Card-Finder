import streamlit as st
import os
import sqlite3
import pandas as pd
import requests
from io import BytesIO
from PIL import Image
import datetime

st.set_page_config(layout="wide", page_title="Image Mapper Tool")

# --- ENVIRONMENT CHECK ---
# Environment check removed for user access
# if not st.secrets.get("is_local", False):
#     st.warning("⚠️ This tool is only available in the local environment.")
#     st.stop()

# Paths
DB_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'credit_card_data.db')
IMAGE_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'cards')

st.title("🛠️ Image Mapping Tool (Database Edition)")
st.info("Use this tool to fix image assignments. Changes are saved directly to the **Database**.")

# 1. Load Data
def load_data():
    conn = sqlite3.connect(DB_FILE)
    # Join with card_images to get current mapping
    query = """
    SELECT 
        d.id, 
        d.bank_name, 
        d.card_name, 
        d.url as page_url,
        i.local_filename,
        i.manual_image_url,
        i.scraper_image_url,
        i.scraper_date
    FROM credit_cards_details d
    LEFT JOIN card_images i ON d.id = i.card_id
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def save_mapping(card_id, bank_name, card_name, filename, manual_url):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Upsert preserving scraper data
        cursor.execute("""
        INSERT INTO card_images (card_id, bank_name, card_name, local_filename, manual_image_url, manual_date)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(card_id) DO UPDATE SET
            local_filename = excluded.local_filename,
            manual_image_url = excluded.manual_image_url,
            manual_date = excluded.manual_date;
        """, (card_id, bank_name, card_name, filename, manual_url, current_time))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"DB Error: {e}")
        return False
    finally:
        conn.close()

# Helper to download image
def download_image(url, bank_name, card_name):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        img = Image.open(BytesIO(response.content))
        
        # Convert CMYK to RGB to allow saving as PNG
        if img.mode == 'CMYK':
            img = img.convert('RGB')
        
        def clean(text): return text.replace(" ", "_").replace("/", "-").replace(":", "")
        filename = f"{clean(bank_name)}-{clean(card_name)}.png"
        file_path = os.path.join(IMAGE_DIR, filename)
        
        img.save(file_path, "PNG")
        return filename, None
    except Exception as e:
        return None, str(e)

# --- UI ---

try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load database: {e}")
    st.stop()

# Load Available Images
try:
    all_images = sorted(os.listdir(IMAGE_DIR), key=lambda x: x.lower())
    image_options = ["None", "Generic Card"] + all_images
except Exception as e:
    st.error(f"Could not list images: {e}")
    st.stop()

# Filter
c_filter1, c_filter2 = st.columns([1, 1])
with c_filter1:
    search = st.text_input("Search Card or Bank", "")
with c_filter2:
    show_unmapped_only = st.checkbox("Show only unmapped cards", value=False)

# Filter Logic
if show_unmapped_only:
    df = df[df['local_filename'].isna()]

if search:
    df = df[df['card_name'].str.contains(search, case=False) | df['bank_name'].str.contains(search, case=False)]

st.markdown(f"### Showing {len(df)} cards")

# List Cards
for index, row in df.iterrows():
    card_id = str(row['id'])
    current_file = row['local_filename'] if row['local_filename'] else "None"
    manual_url = row['manual_image_url'] if row['manual_image_url'] else ""
    scraper_url = row['scraper_image_url']
    
    with st.container():
        c1, c2, c3 = st.columns([2, 2, 1])
        
        with c1:
            st.subheader(f"{row['bank_name']}")
            st.write(f"**{row['card_name']}**")
            st.caption(f"ID: {card_id}")
            if row['page_url']:
                st.markdown(f"[🔗 Official Page]({row['page_url']})")
            
            # Scraper Suggestion
            if scraper_url:
                st.info(f"🤖 **Scraper Found:**\n{scraper_url}")
                if st.button("✅ Use Scraper Image", key=f"promo_{card_id}"):
                    # Download and save as manual
                    saved_filename, error = download_image(scraper_url, row['bank_name'], row['card_name'])
                    if saved_filename:
                        save_mapping(card_id, row['bank_name'], row['card_name'], saved_filename, scraper_url)
                        st.success("Updated!")
                        st.rerun()
                    else:
                        st.error(f"Failed to download: {error}")
            
        with c2:
            # Image Selection
            try:
                idx = image_options.index(current_file) if current_file in image_options else 0
            except:
                idx = 0
                
            new_file = st.selectbox(
                "Select Image", 
                options=image_options, 
                index=idx, 
                key=f"sel_{card_id}",
                label_visibility="collapsed"
            )
            
            # URL Input
            new_url = st.text_input("Manual Image URL", value=manual_url, key=f"url_in_{card_id}", placeholder="https://...")
            
            # Save Button (Individual)
            if st.button("💾 Save", key=f"save_{card_id}"):
                if new_file == "None":
                    new_file = None
                
                if save_mapping(card_id, row['bank_name'], row['card_name'], new_file, new_url):
                    st.success("Saved!")
                    st.rerun()

            # Fetcher
            with st.expander("🌐 Fetch from URL"):
                fetch_url = st.text_input("Paste Link to Download", key=f"fetch_{card_id}")
                if st.button("Fetch & Save", key=f"btn_fetch_{card_id}"):
                    if fetch_url:
                        saved_filename, error = download_image(fetch_url, row['bank_name'], row['card_name'])
                        if saved_filename:
                            # Save to DB
                            save_mapping(card_id, row['bank_name'], row['card_name'], saved_filename, fetch_url)
                            st.success(f"Downloaded & Saved!")
                            st.rerun()
                        else:
                             st.error(f"Failed: {error}")

        with c3:
            # Preview
            if new_file == "Generic Card":
                st.image("https://via.placeholder.com/300x180?text=Generic+Card", width=150)
            elif new_file and new_file != "None":
                img_path = os.path.join(IMAGE_DIR, new_file)
                if os.path.exists(img_path):
                    st.image(img_path, width=150)
                else:
                    st.warning("File not found")
            else:
                st.warning("No Image")
        
        st.divider()
