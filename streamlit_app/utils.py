import streamlit as st
import os
import base64
import json
import re

def load_css():
    # Initialize theme in session state if not present
    if 'theme' not in st.session_state:
        st.session_state.theme = 'dark'

    theme = st.session_state.theme

    # Define Theme Palettes
    if theme == 'dark':
        css_vars = """
        :root {
            --bg-gradient: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --card-bg: rgba(30, 41, 59, 0.7);
            --card-border: rgba(255, 255, 255, 0.1);
            --shadow-color: rgba(0, 0, 0, 0.3);
            --accent-primary: #06b6d4;
            --accent-secondary: #8b5cf6;
            --button-bg: #0f172a;
            --button-text: #ffffff;
            --button-border: rgba(255, 255, 255, 0.2);
            --sidebar-bg: #0f172a;
            --sidebar-border: rgba(255, 255, 255, 0.1);
            --glass-blur: blur(12px);
            --pill-bg: rgba(30, 41, 59, 0.7);
            --pill-text: #f8fafc;
            --pill-active-bg: #06b6d4;
        }
        """
    else: # Light Theme
        css_vars = """
        :root {
            --bg-gradient: linear-gradient(135deg, #fdfbf7 0%, #f4f7f6 100%);
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --card-bg: #ffffff;
            --card-border: rgba(0, 0, 0, 0.05);
            --shadow-color: rgba(0, 0, 0, 0.05);
            --accent-primary: #06b6d4;
            --accent-secondary: #3b82f6;
            --button-bg: #0f172a;
            --button-text: #ffffff;
            --button-border: transparent;
            --sidebar-bg: #ffffff;
            --sidebar-border: #f1f5f9;
            --glass-blur: none;
            --pill-bg: #ffffff;
            --pill-text: #1e293b;
            --pill-active-bg: #06b6d4;
        }
        """

    st.markdown(f"""
    <style>
        /* Import modern font */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

        /* Inject Theme Variables */
        {css_vars}

        /* Safer Global Selectors */
        html, body {{
            font-family: 'Outfit', sans-serif;
            color: var(--text-primary);
        }}

        /* Global Background */
        .stApp {{
            background: var(--bg-gradient) !important;
            background-attachment: fixed !important;
            color: var(--text-primary) !important;
        }}

        /* Transparent Header */
        header[data-testid="stHeader"] {{
            background: transparent !important;
        }}
        
        /* Force text color for Streamlit elements */
        .stMarkdown, .stText, p, div, label, li, span, h1, h2, h3, h4, h5, h6 {{
            color: var(--text-primary) !important;
        }}
        
        /* Headings specific overrides if needed */
        h1, h2, h3, h4, h5, h6 {{
            font-weight: 700;
            letter-spacing: -0.5px;
        }}

        /* Card Container */
        .card-container {{
            background-color: var(--card-bg) !important;
            border-radius: 16px;
            box-shadow: 0 4px 20px var(--shadow-color);
            padding: 24px;
            margin-bottom: 20px;
            border: 1px solid var(--card-border) !important;
            backdrop-filter: var(--glass-blur);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}

        .card-container:hover {{
            transform: translateY(-4px);
            box-shadow: 0 12px 30px var(--shadow-color);
        }}
        
        /* Graph Container (reusing card styles) */
        .graph-container {{
            background: var(--card-bg);
            backdrop-filter: var(--glass-blur);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px 0 var(--shadow-color);
        }}

        /* Mini Card */
        .mini-card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 15px;
            text-align: center;
            margin-bottom: 15px;
            transition: transform 0.2s ease, background 0.2s ease;
            height: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 10px var(--shadow-color);
        }}
        .mini-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 20px var(--shadow-color);
        }}
        .mini-card-img-container {{
            height: 100px;
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 10px;
        }}

        /* --- INPUT FIELDS FIX --- */
        /* Force inputs to match theme */
        input, .stTextInput input, .stNumberInput input, .stSelectbox input {{
            color: #333333 !important;
            caret-color: #333333 !important;
        }}
        
        /* Fix for Selectbox dropdown text */
        div[data-baseweb="select"] > div {{
            color: #333333 !important;
        }}
        
        /* Fix for Number Input buttons (+/-) */
        button[kind="secondary"] {{
            color: #333333 !important;
            border-color: rgba(0,0,0,0.1) !important;
        }}
        
        /* Force SVG icons (plus/minus) to be dark */
        button[kind="secondary"] svg,
        button[kind="secondary"] svg path {{
            fill: #333333 !important;
            stroke: #333333 !important;
            color: #333333 !important;
        }}
        .mini-card img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));
        }}
        .mini-card h4 {{
            font-size: 0.9rem;
            color: var(--text-primary) !important;
            margin: 0;
            font-weight: 600;
            line-height: 1.3;
        }}
        .mini-card p {{
            font-size: 0.75rem;
            color: var(--text-secondary) !important;
            margin: 5px 0 0 0;
        }}

        /* Typography Helpers */
        .bank-name {{
            font-size: 0.8rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-weight: 600;
            margin-bottom: 6px;
        }}

        .card-title {{
            font-size: 1.4rem;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 15px;
            background: none;
        }}

        /* Stats Grid */
        .stats-grid {{
            display: flex;
            gap: 25px;
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--card-border);
        }}

        .stat-item {{
            display: flex;
            flex-direction: column;
        }}

        .stat-label {{
            font-size: 0.7rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            font-weight: 600;
            margin-bottom: 4px;
        }}

        .stat-value {{
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text-primary);
        }}

        /* Benefits List */
        .benefit-item {{
            font-size: 0.9rem;
            color: var(--text-secondary);
            margin-bottom: 8px;
            display: flex;
            align-items: center;
        }}
        
        .benefit-icon {{
            margin-right: 10px;
            color: var(--accent-primary);
            text-shadow: none;
        }}

        /* Buttons */
        .stButton>button {{
            background: var(--button-bg) !important;
            color: var(--button-text) !important;
            border-radius: 8px;
            border: 1px solid var(--button-border);
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            transition: all 0.3s;
            box-shadow: 0 4px 10px var(--shadow-color);
        }}
        
        .stButton>button p, .stButton>button div, .stButton>button span {{
            color: var(--button-text) !important;
        }}
        
        .stButton>button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 15px var(--shadow-color);
            filter: brightness(1.1);
        }}

        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: var(--sidebar-bg) !important;
            border-right: 1px solid var(--sidebar-border);
        }}
        
        [data-testid="stSidebar"] * {{
            color: var(--text-primary) !important;
        }}
        
        /* Pills (Filter Chips) */
        [data-testid="stPills"] {{
            background: transparent !important;
        }}
        
        /* Target the individual pill options */
        [data-testid="stPills"] [role="option"] {{
            background-color: var(--pill-bg) !important;
            border: 1px solid var(--card-border) !important;
            color: var(--pill-text) !important;
            transition: all 0.2s;
        }}
        
        [data-testid="stPills"] [role="option"]:hover {{
            border-color: var(--accent-primary) !important;
            color: var(--accent-primary) !important;
        }}
        
        /* Active Pill */
        [data-testid="stPills"] [role="option"][aria-selected="true"] {{
            background-color: var(--pill-active-bg) !important;
            color: #ffffff !important;
            border-color: var(--pill-active-bg) !important;
        }}
        
        /* Fallback for button selector if role="option" fails */
        [data-testid="stPills"] button {{
            background-color: var(--pill-bg) !important;
            border: 1px solid var(--card-border) !important;
            color: var(--pill-text) !important;
        }}

        /* Dialog/Modal */
        div[data-testid="stDialog"], div[role="dialog"] {{
            background-color: var(--card-bg) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--card-border);
            backdrop-filter: blur(20px);
        }}
        div[data-testid="stDialog"] > div, div[role="dialog"] > div {{
             background-color: transparent !important;
             color: var(--text-primary) !important;
        }}
        
        /* Glass Card (used in lists) */
        .glass-card {{
            background: var(--card-bg);
            backdrop-filter: var(--glass-blur);
            border-radius: 16px;
            border: 1px solid var(--card-border);
            box-shadow: 0 8px 32px 0 var(--shadow-color);
            margin-bottom: 20px;
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .glass-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 12px 40px 0 var(--shadow-color);
        }}
        
        .card-content {{
            display: flex;
            flex-direction: row;
            padding: 20px;
            gap: 25px;
        }}
        
        .card-image-container {{
            flex: 0 0 180px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 10px;
            height: 120px;
        }}
        
        .card-img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));
        }}
        
        .card-details {{
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        
        .card-header {{
            margin-bottom: 10px;
        }}
        
        .card-bank {{
            font-size: 0.9rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
            margin: 0;
        }}
        
        .card-stats {{
            display: flex;
            gap: 30px;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid var(--card-border);
        }}
        
        /* Mobile Optimization */
        @media (max-width: 768px) {{
            .card-content {{
                flex-direction: row !important;
                padding: 10px !important;
                gap: 10px !important;
            }}
            .card-image-container {{
                flex: 0 0 80px !important;
                height: 50px !important;
            }}
            .card-benefits {{
                display: none !important;
            }}
        }}

        /* --- SIDEBAR TOGGLE CUSTOMIZATION --- */
        /* Target the container */
        [data-testid="stSidebarCollapsedControl"] {{
            color: #38bdf8 !important; /* Light Blue */
            font-weight: 700 !important;
            display: flex !important;
            align-items: center !important;
            border: 1px solid rgba(56, 189, 248, 0.2);
            border-radius: 8px;
            padding: 2px 10px;
            background: rgba(56, 189, 248, 0.1);
            transition: all 0.3s ease;
        }}

        [data-testid="stSidebarCollapsedControl"]:hover {{
            background: rgba(56, 189, 248, 0.2);
            border-color: #38bdf8;
            box-shadow: 0 0 10px rgba(56, 189, 248, 0.3);
        }}
        
        /* Target the SVG icon specifically */
        [data-testid="stSidebarCollapsedControl"] svg,
        [data-testid="stSidebarCollapsedControl"] svg path {{
            fill: #38bdf8 !important;
            color: #38bdf8 !important;
        }}
        
        /* Add "Menu" label */
        [data-testid="stSidebarCollapsedControl"]::after {{
            content: "Menu";
            margin-left: 8px;
            font-size: 1rem;
            color: #38bdf8 !important; /* Light Blue */
            font-weight: 600;
            padding-bottom: 2px; /* Alignment tweak */
        }}

        /* --- HOVER FIXES --- */
        /* Prevent white box/highlight on link hover */
        a.card-link {{
            text-decoration: none !important;
            background: transparent !important;
        }}
        
        a.card-link:hover {{
            background-color: transparent !important;
            background: transparent !important;
            text-decoration: none !important;
            box-shadow: none !important;
        }}

        /* Disable pointer events on image to prevent tooltips */
        .card-img {{
            pointer-events: none !important;
        }}

        /* --- GLASS SHEET MODAL (CSS ONLY) --- */
        .modal-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(4px);
            z-index: 9999;
            opacity: 0;
            display: none; /* Changed from visibility: hidden to display: none */
            transition: opacity 0.3s ease;
            align-items: center;
            justify-content: center;
        }}

        /* Show modal when target is active */
        .modal-overlay:target {{
            opacity: 1;
            display: flex; /* Show when targeted */
        }}

        .modal-content {{
            background: rgba(30, 41, 59, 0.95); /* Dark Slate */
            backdrop-filter: blur(15px);
            border-radius: 20px;
            width: 90%;
            max-width: 600px;
            max-height: 85vh;
            overflow-y: auto;
            position: relative;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.1);
            transform: scale(0.95);
            transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
            display: flex;
            flex-direction: column;
        }}

        .modal-overlay:target .modal-content {{
            transform: scale(1);
        }}

        .modal-close {{
            position: absolute;
            top: 15px;
            right: 15px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 50%;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-decoration: none;
            color: #f8fafc;
            font-weight: bold;
            font-size: 1.2rem;
            z-index: 10;
            transition: background 0.2s;
        }}
        
        .modal-close:hover {{
            background: rgba(0, 0, 0, 0.1);
        }}

        .modal-header {{
            padding: 25px 25px 15px 25px;
            border-bottom: 1px solid rgba(0,0,0,0.05);
            text-align: center;
        }}
        
        .modal-img-container {{
            height: 140px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 15px;
        }}
        
        .modal-img {{
            max-height: 100%;
            max-width: 100%;
            object-fit: contain;
            filter: drop-shadow(0 8px 16px rgba(0,0,0,0.15));
        }}

        .modal-title {{
            font-size: 1.5rem;
            font-weight: 800;
            color: #f8fafc !important;
            margin: 0;
            line-height: 1.2;
        }}
        
        .modal-bank {{
            font-size: 0.9rem;
            color: #cbd5e1 !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 5px;
        }}

        .modal-body {{
            padding: 25px;
            flex: 1;
        }}

        .modal-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 25px;
        }}
        
        .modal-stat-box {{
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 12px;
            text-align: center;
        }}
        
        .modal-stat-label {{
            font-size: 0.7rem;
            color: #94a3b8 !important;
            text-transform: uppercase;
            display: block;
            margin-bottom: 4px;
        }}
        
        .modal-stat-value {{
            font-size: 0.95rem;
            font-weight: 700;
            color: #f8fafc !important;
        }}

        .modal-section-title {{
            font-size: 1rem;
            font-weight: 700;
            margin: 20px 0 10px 0;
            color: #e2e8f0 !important;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .modal-benefits-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        
        .modal-benefit-item {{
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            font-size: 0.95rem;
            color: #cbd5e1 !important;
            display: flex;
            gap: 10px;
        }}
        
        .modal-benefit-item:last-child {{
            border-bottom: none;
        }}

        .modal-footer {{
            padding: 20px;
            background: rgba(30, 41, 59, 0.9);
            border-top: 1px solid rgba(255,255,255,0.1);
            position: sticky;
            bottom: 0;
            backdrop-filter: blur(10px);
        }}

        .modal-text-content {{
            font-size: 0.95rem;
            color: #cbd5e1 !important;
            margin-bottom: 15px;
        }}

        /* Mobile Bottom Sheet Animation */
        @media (max-width: 768px) {{
            .modal-overlay {{
                align-items: flex-end; /* Align to bottom */
            }}
            
            .modal-content {{
                width: 100%;
                max-width: 100%;
                border-radius: 24px 24px 0 0; /* Rounded top only */
                max-height: 85vh;
                transform: translateY(100%); /* Start off-screen */
                transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            }}
            
            .modal-overlay:target .modal-content {{
                transform: translateY(0); /* Slide up */
            }}
        }}

    </style>
    """, unsafe_allow_html=True)

def parse_salary(salary_str):
    """
    Parses a salary string (e.g., 'AED 15,000', '5000', 'Not Mentioned') into a float.
    Returns 0.0 if not found or invalid.
    """
    if not salary_str or salary_str in ["Not Mentioned", "Not Found", "-"]:
        return 0.0
    
    # Remove commas and non-numeric chars (except dot)
    clean_str = re.sub(r'[^\d.]', '', str(salary_str))
    
    try:
        return float(clean_str)
    except ValueError:
        return 0.0

def get_image_base64(file_path):
    """Reads an image file and returns the base64 string."""
    try:
        with open(file_path, "rb") as f:
            data = f.read()
            encoded = base64.b64encode(data).decode()
            return f"data:image/png;base64,{encoded}"
    except Exception as e:
        # print(f"Error loading image {file_path}: {e}")
        return "https://via.placeholder.com/300x180?text=Error+Loading+Image"

import sqlite3

@st.cache_data(ttl=3600)
def get_card_image_from_db(card_id):
    """
    Fetches image source from the database (Cached).
    Prioritizes scraper_image_url, then local_filename.
    Returns None if not found.
    """
    db_path = os.path.join(os.path.dirname(__file__), '..', 'credit_card_data.db')
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Select both columns
        cursor.execute("SELECT scraper_image_url, local_filename FROM card_images WHERE card_id = ?", (card_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            scraper_url, local_filename = result
            # Priority 1: Local Filename (Manual Override)
            if local_filename and local_filename.strip():
                return local_filename
            # Priority 2: Scraper URL
            if scraper_url and scraper_url.strip():
                return scraper_url
                
        return None
    except Exception as e:
        # print(f"DB Error: {e}")
        return None

@st.cache_data(ttl=3600)
def get_image_base64_cached(file_path):
    """Reads an image file and returns the base64 string (Cached)."""
    return get_image_base64(file_path)

def get_card_image_source(row):
    """
    Finds the image and returns a source string (URL or Base64) for HTML.
    """
    card_id = str(row['id'])
    
    # 1. Try Database (returns URL or Filename)
    image_source = get_card_image_from_db(card_id)
        
    # Handle Generic
    if image_source == "Generic Card":
        return "https://via.placeholder.com/300x180?text=Generic+Card"
    
    # 2. If no source, return placeholder
    if not image_source:
        return "https://via.placeholder.com/300x180?text=No+Image"
        
    # 3. If it's a URL (starts with http), return it directly
    if image_source.startswith("http"):
        return image_source
        
    # 4. If it's a filename, construct absolute file path and get Base64
    # utils.py is in streamlit_app/, images are in streamlit_app/static/cards/
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, 'static', 'cards', image_source)
    
    if os.path.exists(file_path):
        return get_image_base64_cached(file_path)
        
    return "https://via.placeholder.com/300x180?text=Image+Not+Found"

def get_card_html(row):
    # Get the image source (Base64 or URL)
    image_src = get_card_image_source(row)
    
    # Helper to format "Not Mentioned" as "---"
    def fmt(val):
        if val is None:
            return "---"
        s = str(val).strip()
        if s in ["Not Mentioned", "None", "nan", "", "N/A"]:
            return "---"
        return s

    # Parse benefits list (assuming stored as JSON string or comma-separated)
    benefits_html = ""
    try:
        # Try parsing as JSON first
        benefits_list = json.loads(row['other_key_benefits']) if row['other_key_benefits'] else []
        if isinstance(benefits_list, list):
            for b in benefits_list:
                benefits_html += f'<li class="modal-benefit-item"><span class="benefit-icon">✨</span>{b}</li>'
        else:
            # Fallback for string
            benefits_html = f'<li class="modal-benefit-item"><span class="benefit-icon">✨</span>{row["other_key_benefits"]}</li>'
    except:
        # Fallback for plain text
        benefits_html = f'<li class="modal-benefit-item"><span class="benefit-icon">✨</span>{row.get("other_key_benefits", "No details available")}</li>'

    html = f"""
    <!-- Card Trigger -->
    <!-- Card Trigger -->
    <a href="#modal-{row['id']}" class="card-link" style="text-decoration: none; color: inherit; display: block;">
        <div class="glass-card">
            <div class="card-content">
                <div class="card-image-container">
                    <img src="{image_src}" class="card-img" alt="{row['card_name']}">
                </div>
                <div class="card-details">
                    <div class="card-header">
                        <p class="card-bank">{row['bank_name']}</p>
                        <h4 class="card-title">{row['card_name']}</h4>
                    </div>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <span class="stat-label">Fee</span>
                            <span class="stat-value">{fmt(row['annual_fee'])}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Min Salary</span>
                            <span class="stat-value">{fmt(row['minimum_salary_requirement'])}</span>
                        </div>
                    </div>
                    <div class="card-benefits">
                        <span class="benefit-tag">✨ {str(row['welcome_bonus'])[:30]}...</span>
                        <span class="benefit-tag">💰 {str(row['cashback_rates'])[:30]}...</span>
                    </div>
                    <!-- Mobile Only Hint -->
                    <div class="mobile-actions" style="display:none; color: #0056b3; font-size: 0.8rem; margin-top: 5px;">
                         Tap for details 👆
                    </div>
                </div>
            </div>
        </div>
    </a>

    <!-- Glass Sheet Modal -->
    <div id="modal-{row['id']}" class="modal-overlay">
        <div class="modal-content">
            <a href="#" class="modal-close">×</a>
            <div class="modal-header">
                <div class="modal-img-container">
                    <img src="{image_src}" class="modal-img" alt="{row['card_name']}">
                </div>
                <h3 class="modal-title">{row['card_name']}</h3>
                <p class="modal-bank">{row['bank_name']}</p>
            </div>
            
            <div class="modal-body">
                <!-- Key Stats Grid -->
                <div class="modal-grid">
                    <div class="modal-stat-box">
                        <span class="modal-stat-label">Annual Fee</span>
                        <span class="modal-stat-value">{fmt(row['annual_fee'])}</span>
                    </div>
                    <div class="modal-stat-box">
                        <span class="modal-stat-label">Min Salary</span>
                        <span class="modal-stat-value">{fmt(row['minimum_salary_requirement'])}</span>
                    </div>
                    <div class="modal-stat-box">
                        <span class="modal-stat-label">Min Spend</span>
                        <span class="modal-stat-value">{fmt(row.get('minimum_spend'))}</span>
                    </div>
                    <div class="modal-stat-box">
                        <span class="modal-stat-label">Foreign Fee</span>
                        <span class="modal-stat-value">{fmt(row.get('foreign_currency_fee'))}</span>
                    </div>
                </div>

                <!-- Text Content -->
                <div class="modal-section-title">
                    <span>🏆</span> Welcome Bonus
                </div>
                <div class="modal-text-content">
                    {fmt(row['welcome_bonus'])}
                </div>

                <div class="modal-section-title">
                    <span>💳</span> Cashback & Rewards
                </div>
                <div class="modal-text-content">
                    {fmt(row.get('cashback_summary'))}
                </div>
                
                <div class="modal-section-title">
                    <span>✈️</span> Travel Benefits
                </div>
                <div class="modal-text-content">
                    {fmt(row.get('travel_points_summary'))}
                </div>

                <!-- Key Benefits List -->
                <div class="modal-section-title">
                    <span>✨</span> Other Perkes (Lounge, Dining, etc.)
                </div>
                <ul class="modal-benefits-list">
                    {benefits_html}
                </ul>
            </div>

            <div class="modal-footer">
                <a href="#" style="
                    display: block; 
                    width: 100%; 
                    padding: 15px; 
                    background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%); 
                    color: white; 
                    text-align: center; 
                    text-decoration: none; 
                    font-weight: 700; 
                    border-radius: 12px;
                    box-shadow: 0 4px 15px rgba(6, 182, 212, 0.4);
                ">Apply Now / View Details</a>
            </div>
        </div>
    </div>
    """
    return html
