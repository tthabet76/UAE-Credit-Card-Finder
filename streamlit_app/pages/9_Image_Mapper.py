import streamlit as st
import json
import os
import sqlite3
import pandas as pd

st.set_page_config(layout="wide", page_title="Image Mapper Tool")

# Paths
DB_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'credit_card_data.db')
MAPPING_FILE = os.path.join(os.path.dirname(__file__), '..', 'card_image_mapping.json')
IMAGE_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'cards')

st.title("🛠️ Image Mapping Tool")
st.info("Use this tool to manually fix image assignments. Changes are saved to `card_image_mapping.json`.")

import requests
from io import BytesIO
from PIL import Image

# ... (Previous imports)

# 1. Load Data
@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT id, bank_name, card_name, url FROM credit_cards_details", conn)
    conn.close()
    return df

# ... (Previous code)

# Helper to download image
def download_image(url, bank_name, card_name):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Open image to verify and convert
        img = Image.open(BytesIO(response.content))
        
        # Create clean filename
        # e.g. "ADCB-Lulu_Platinum.png"
        def clean(text): return text.replace(" ", "_").replace("/", "-").replace(":", "")
        filename = f"{clean(bank_name)}-{clean(card_name)}.png"
        file_path = os.path.join(IMAGE_DIR, filename)
        
        # Save
        img.save(file_path, "PNG")
        return filename
    except Exception as e:
        return None, str(e)

# ... (UI Code)

# List Cards


try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load database: {e}")
    st.stop()

# 2. Load Existing Mapping
if 'mapping' not in st.session_state:
    if os.path.exists(MAPPING_FILE):
        with open(MAPPING_FILE, 'r') as f:
            st.session_state.mapping = json.load(f)
    else:
        st.session_state.mapping = {}

# 3. Load Available Images
try:
    # List files and sort them alphabetically (case-insensitive)
    all_images = sorted(os.listdir(IMAGE_DIR), key=lambda x: x.lower())
    # Add a "None" option
    image_options = ["None"] + all_images
except Exception as e:
    st.error(f"Could not list images: {e}")
    st.stop()

# --- UI ---

# Filter
c_filter1, c_filter2 = st.columns([1, 1])
with c_filter1:
    search = st.text_input("Search Card or Bank", "")
with c_filter2:
    show_unmapped_only = st.checkbox("Show only unmapped cards", value=True)

# Filter Logic
if show_unmapped_only:
    # Get list of IDs that have a valid mapping (not None and not empty)
    mapped_ids = [k for k, v in st.session_state.mapping.items() if v]
    # Exclude these from df
    # Ensure ID is string for comparison
    df = df[~df['id'].astype(str).isin(mapped_ids)]

if search:
    df = df[df['card_name'].str.contains(search, case=False) | df['bank_name'].str.contains(search, case=False)]

# Add Generic Option
if "Generic Card" not in image_options:
    image_options.insert(1, "Generic Card")

# Save Button
st.markdown(f"### Showing {len(df)} cards to map")
if st.button("💾 Save Changes to JSON", type="primary"):
    with open(MAPPING_FILE, 'w') as f:
        json.dump(st.session_state.mapping, f, indent=2)
    st.success("Mapping saved successfully!")
    st.rerun() # Rerun to refresh the list if unmapped filter is on

# List Cards
for index, row in df.iterrows():
    card_id = str(row['id'])
    current_file = st.session_state.mapping.get(card_id)
    
    with st.container():
        c1, c2, c3 = st.columns([2, 2, 1])
        
        with c1:
            st.subheader(f"{row['bank_name']}")
            st.write(f"**{row['card_name']}**")
            st.caption(f"ID: {card_id}")
            if row['url']:
                st.markdown(f"[🔗 Official Page]({row['url']})")
            
        with c2:
            # Dropdown to select image
            # Find index of current selection
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
            
            # URL Fetcher
            with st.expander("🌐 Fetch from URL"):
                img_url = st.text_input("Paste Image Link", key=f"url_{card_id}")
                if st.button("Fetch & Save", key=f"btn_{card_id}"):
                    if img_url:
                        saved_filename = download_image(img_url, row['bank_name'], row['card_name'])
                        if isinstance(saved_filename, tuple): # Error
                            st.error(f"Failed: {saved_filename[1]}")
                        elif saved_filename:
                            # Update mapping and session state
                            st.session_state.mapping[card_id] = saved_filename
                            
                            # Auto-save to JSON
                            with open(MAPPING_FILE, 'w') as f:
                                json.dump(st.session_state.mapping, f, indent=2)
                                
                            st.success(f"Saved as {saved_filename}")
                            st.rerun()
            
            # Update session state if changed
            if new_file != "None":
                st.session_state.mapping[card_id] = new_file
            elif card_id in st.session_state.mapping:
                # If None selected, remove from mapping or set to None
                st.session_state.mapping[card_id] = None

        with c3:
            # Preview
            if new_file == "Generic Card":
                st.image("https://via.placeholder.com/300x180?text=Generic+Card", width=150)
            elif new_file and new_file != "None":
                img_path = os.path.join(IMAGE_DIR, new_file)
                st.image(img_path, width=150)
            else:
                st.warning("No Image")
        
        st.divider()
