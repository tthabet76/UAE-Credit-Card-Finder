import streamlit as st
import os
import base64
import json
import re
from db_utils import get_supabase_client, SUPABASE_ENABLED

def load_css():
    # Initialize theme in session state if not present
    if 'theme' not in st.session_state:
        st.session_state.theme = 'dark'

    theme = st.session_state.theme

    # Define Theme Palettes (Standard CSS strings, no doubling needed here as they are vars)
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
            --input-bg: #0f172a;
            --input-text: #ffffff;
            --input-border: rgba(255, 255, 255, 0.2);
            --dropdown-bg: #1e1b4b;
            --dropdown-border: rgba(255, 255, 255, 0.1);
            --option-text: #e2e8f0;
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
            --input-bg: #ffffff;
            --input-text: #1e293b;
            --input-border: #cbd5e1;
            --dropdown-bg: #ffffff;
            --dropdown-border: #e2e8f0;
            --option-text: #1e293b;
        }
        """

    # Injecting CSS: NOTE ALL BRACES MUST BE DOUBLED {{ }} EXCEPT F-STRING VARS {var}
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

        /* --- UNIVERSAL INPUT FIX (Dynamic Theme) --- */
        
        /* 1. Target the Input Wrapper (The Box Itself) */
        div[data-baseweb="base-input"], .stTextInput div[data-baseweb="base-input"], .stTextArea div[data-baseweb="base-input"] {{
            background-color: var(--input-bg) !important;
            border: 1px solid var(--input-border) !important;
            border-radius: 8px !important;
        }}
        
        /* 2. Target the actual input text element */
        input, textarea, select, .stTextInput input, .stTextArea textarea {{
            color: var(--input-text) !important;
            background-color: transparent !important; 
            caret-color: var(--accent-primary) !important;
        }}
        
        /* 3. Dropdowns (Selectbox) */
        div[data-baseweb="select"] > div {{
            background-color: var(--input-bg) !important;
            color: var(--input-text) !important;
            border: 1px solid var(--input-border) !important;
        }}
        
        /* 4. Dropdown Options Menu */
        ul[data-baseweb="menu"], [role="listbox"] {{
            background-color: var(--dropdown-bg) !important;
            border: 1px solid var(--dropdown-border) !important;
        }}
        
        li[role="option"] {{
            color: var(--option-text) !important;
        }}
        
        /* 5. Number Input Buttons */
        button[kind="secondary"] {{
            background-color: transparent !important;
            color: var(--input-text) !important;
            border: none !important;
        }}
        button[kind="secondary"]:hover {{
            background-color: rgba(125,125,125,0.1) !important;
        }}
        
        /* Fix SVG Icons */
        button[kind="secondary"] svg, button[kind="secondary"] svg path {{
            fill: var(--input-text) !important;
        }}
        
        /* 6. Fix "Not Mentioned" or Disabled inputs */
        input:disabled, textarea:disabled, div[data-baseweb="base-input"][disabled] {{
            background-color: transparent !important; /* Inherit */
            opacity: 0.6;
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
            font-size: 1.1rem; 
            color: var(--text-secondary);
            text-transform: uppercase;
            font-weight: 700;
            margin-bottom: 4px;
        }}

        .stat-value {{
            font-size: 1.1rem; /* Equal size */
            font-weight: 700;
            color: var(--text-primary);
            line-height: 1.2;
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
            padding: 12px; /* Reduced from 20px */
            gap: 20px; /* Reduced from 25px */
            align-items: center; /* Vertically Center Image */
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
            margin-bottom: 3px; /* Reduced from 5px */
        }}
        
        .card-bank {{
            font-size: 0.9rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
            margin: 0;
        }}
        
        .card-title {{
            font-size: 1.4rem;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 4px; /* Reduced from 8px */
            background: none;
            line-height: 1.2;
        }}
        
        .card-grid-2x2 {{
            display: grid;
            grid-template-columns: 1fr 1fr; /* Strict 50% split */
            gap: 15px 25px; /* Row Gap 15px, Col Gap 25px */
            margin-bottom: 5px;
            padding-bottom: 5px;
        }}
        
        .grid-item {{
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            text-overflow: ellipsis;
            line-height: 1.3;
            /* Reset Flex */
            min-width: 0;
            width: 100%;
        }}

        .grid-label {{
            font-size: 0.75rem;
            color: var(--text-secondary);
            font-weight: 700;
            text-transform: uppercase;
            display: inline; /* Force Inline */
            margin-right: 6px; /* Spacing via margin */
            white-space: nowrap;
        }}

        .grid-value {{
            font-size: 0.95rem;
            font-weight: 700;
            color: var(--text-primary);
            display: inline; /* Force Inline */
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

        /* --- GLASS SHEET MODAL (PREMIUM) --- */
        .modal-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(8px);
            z-index: 9999;
            opacity: 0;
            display: none;
            transition: opacity 0.3s ease;
            align-items: center;
            justify-content: center;
        }}

        .modal-overlay:target {{
            opacity: 1;
            display: flex;
        }}

        .modal-content {{
            background: rgba(15, 23, 42, 0.8);
            backdrop-filter: blur(24px) saturate(180%);
            -webkit-backdrop-filter: blur(24px) saturate(180%);
            border-radius: 24px;
            width: 95%;
            max-width: 800px;
            max-height: 90vh;
            overflow-y: auto;
            position: relative;
            box-shadow: 0 50px 100px -20px rgba(0, 0, 0, 0.7), inset 0 0 0 1px rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.08);
            transform: scale(0.96);
            transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            display: flex;
            flex-direction: column;
        }}

        .modal-overlay:target .modal-content {{
            transform: scale(1);
        }}

        .modal-close {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 50%;
            width: 36px;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-decoration: none;
            color: #cbd5e1;
            font-size: 1.5rem;
            z-index: 20;
            transition: all 0.2s;
            border: 1px solid rgba(255,255,255,0.05);
        }}
        
        .modal-close:hover {{
            background: rgba(255, 255, 255, 0.15);
            color: white;
            transform: rotate(90deg);
        }}

        /* Modal Header */
        .modal-header {{
            padding: 40px 40px 20px 40px;
            text-align: center;
            background: linear-gradient(to bottom, rgba(255,255,255,0.02), transparent);
        }}
        
        .modal-img-container {{
            height: 160px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 20px;
            filter: drop-shadow(0 20px 40px rgba(0,0,0,0.3));
            transition: transform 0.3s;
        }}
        
        .modal-img-container:hover {{
            transform: scale(1.05);
        }}
        
        .modal-img {{
            max-height: 100%;
            max-width: 100%;
            object-fit: contain;
        }}

        .modal-title {{
            font-size: 2rem;
            font-weight: 800;
            color: #f8fafc !important;
            margin: 0;
            line-height: 1.1;
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, #fff 0%, #cbd5e1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .modal-bank {{
            font-size: 0.9rem;
            color: #94a3b8 !important;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-top: 8px;
            font-weight: 600;
        }}

        /* Modal Body */
        .modal-body {{
            padding: 30px 40px;
            flex: 1;
        }}

        /* Key Stats Grid - Sleek Cards */
        .modal-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
            gap: 15px;
            margin-bottom: 40px;
        }}
        
        .modal-stat-box {{
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 16px;
            text-align: center;
            transition: background 0.2s, transform 0.2s;
        }}
        
        .modal-stat-box:hover {{
            background: rgba(255,255,255,0.06);
            transform: translateY(-2px);
            border-color: rgba(255,255,255,0.15);
        }}
        
        .modal-stat-label {{
            font-size: 0.75rem;
            color: #94a3b8 !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: block;
            margin-bottom: 6px;
            font-weight: 600;
        }}
        
        .modal-stat-value {{
            font-size: 1rem;
            font-weight: 700;
            color: #f1f5f9 !important;
        }}

        /* Sections */
        .modal-section-title {{
            font-size: 0.85rem;
            font-weight: 700;
            margin: 8px 0 2px 0;
            color: #94a3b8 !important; /* Muted color for label */
            display: flex;
            align-items: center;
            gap: 6px;
            padding-bottom: 0px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border: none;
        }}
        
        .modal-text-content {{
            font-size: 0.95rem;
            color: #f1f5f9 !important;
            line-height: 1.4;
            background: rgba(255,255,255,0.03);
            padding: 8px 12px;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.05);
            margin-bottom: 4px;
        }}

        /* Two Column Layout for Details */
        .modal-details-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }}
        
        .modal-benefit-item {{
            padding: 8px 0;
            font-size: 0.95rem;
            color: #cbd5e1 !important;
            display: flex;
            align-items: flex-start;
            gap: 12px;
        }}
        
        .benefit-icon {{
            color: #38bdf8; /* Sky Blue */
            font-size: 1.1rem;
            margin-top: -2px;
        }}

        /* Footer */
        .modal-footer {{
            padding: 25px 40px;
            background: rgba(15, 23, 42, 0.8);
            border-top: 1px solid rgba(255,255,255,0.08);
            position: sticky;
            bottom: 0;
            backdrop-filter: blur(20px);
            z-index: 10;
        }}
        
        .apply-btn {{
            display: block; 
            width: 100%; 
            padding: 16px; 
            background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%); 
            color: white !important; 
            text-align: center; 
            text-decoration: none; 
            font-weight: 700; 
            font-size: 1.1rem;
            border-radius: 16px;
            box-shadow: 0 10px 30px -10px rgba(14, 165, 233, 0.6);
            transition: all 0.3s;
            border: 1px solid rgba(255,255,255,0.2);
            letter-spacing: 0.5px;
        }}
        
        .apply-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 15px 35px -10px rgba(14, 165, 233, 0.7);
            filter: brightness(1.1);
        }}

        /* Mobile Adjustments */
        @media (max-width: 768px) {{
            .modal-overlay {{
                align-items: flex-end;
            }}
            .modal-content {{
                width: 100%;
                max-width: 100%;
                border-radius: 30px 30px 0 0;
                max-height: 85vh;
                transform: translateY(100%);
            }}
            .modal-overlay:target .modal-content {{
                transform: translateY(0);
            }}
            .modal-details-grid {{
                grid-template-columns: 1fr;
                gap: 0;
            }}
            .modal-header, .modal-body, .modal-footer {{
                padding: 25px;
            }}
            .modal-title {{
                font-size: 1.5rem;
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
    Fetches image source.
    If SUPABASE_ENABLED: Returns the public 'image_url' from Cloud.
    If LOCAL: Returns local_filename or scraper_url from SQLite.
    """
    if SUPABASE_ENABLED:
        try:
            client = get_supabase_client()
            if client:
                # Optimized: Select 'image_url'
                resp = client.table("card_images").select("image_url").eq("card_id", card_id).execute()
                if resp.data and resp.data[0].get('image_url'):
                    return resp.data[0]['image_url']
        except Exception as e:
            # print(f"Supabase Img Error: {e}")
            pass
            
    # Fallback / Local Mode
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

def get_card_html(row, layout="horizontal"):
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

    # --- HELPER: Safe Field Formatter ---
    def safe_fmt(label, val, icon="🔹"):
        if not val: return ""
        s = str(val).strip()
        if s.lower() in ["not mentioned", "none", "nan", "n/a", "", "0", "-"]: return ""
        return f"""<div class="modal-section-title"><span>{icon}</span> {label}</div><div class="modal-text-content">{s}</div>"""

    # --- HELPER: Dynamic Grid Creator ---
    def create_dynamic_grid(items):
        # items = [(label, val, icon), ...]
        valid_htmls = []
        for label, val, icon in items:
            html = safe_fmt(label, val, icon)
            if html.strip():
                valid_htmls.append(html)
        
        if not valid_htmls: return ""
        
        left_col = []
        right_col = []
        for i, h in enumerate(valid_htmls):
            if i % 2 == 0: left_col.append(h)
            else: right_col.append(h)
            
        return f"""<div class="modal-details-grid"><div class="modal-col">{''.join(left_col)}</div><div class="modal-col">{''.join(right_col)}</div></div>"""

    # Helper for benefits (allow longer text, let CSS truncate)
    def fmt_benefit(val):
        if not val: return "---"
        s = str(val).strip()
        if s.lower() in ["not mentioned", "none", "nan", "", "n/a", "no", "0"]: return "---"
        return s

    if layout == "vertical":
        # Vertical Trigger (Mini Card Style)
        trigger_html = f"""<a href="#modal-{row['id']}" class="card-link" style="text-decoration: none; color: inherit; display: block; height: 100%;"><div class="mini-card"><div class="mini-card-img-container"><img src="{image_src}" alt="{row['card_name']}"></div><h4>{row['card_name']}</h4><p style="margin-top: 5px; color: #94a3b8; font-size: 0.8rem;">{row['bank_name']}</p></div></a>"""
    else:
        # Horizontal Trigger (Glass Card Style - Default)
        trigger_html = f"""<a href="#modal-{row['id']}" class="card-link" style="text-decoration: none; color: inherit; display: block;"><div class="glass-card"><div class="card-content"><div class="card-image-container"><img src="{image_src}" class="card-img" alt="{row['card_name']}"></div><div class="card-details"><div class="card-header"><p class="card-bank">{row['bank_name']}</p><h4 class="card-title">{row['card_name']}</h4></div><div class="card-grid-2x2"><div class="grid-item"><span class="grid-label">Fee :</span><span class="grid-value">{fmt(row['annual_fee'])}</span></div><div class="grid-item"><span class="grid-label">Min Salary :</span><span class="grid-value">{fmt(row['minimum_salary_requirement'])}</span></div><div class="grid-item"><span class="grid-label">Welcome Bonus :</span><span class="grid-value" title="{str(row['welcome_bonus'])}">{fmt_benefit(row['welcome_bonus'])}</span></div><div class="grid-item"><span class="grid-label">Cashback :</span><span class="grid-value" title="{str(row['cashback_rates'])}">{fmt_benefit(row['cashback_rates'])}</span></div></div></div></div></div></a>"""

    html = f"""
{trigger_html}

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
<div class="modal-body">
<!-- 1. Key Stats Grid -->
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
<span class="modal-stat-label">Travel Miles</span>
<span class="modal-stat-value">{'Yes' if row.get('travel_points_summary') and str(row.get('travel_points_summary')).lower() not in ['none', 'nan', '', 'not mentioned', '---'] else 'No'}</span>
</div>
<div class="modal-stat-box">
<span class="modal-stat-label">Cashback</span>
<span class="modal-stat-value">{'Yes' if (row.get('cashback_summary') and str(row.get('cashback_summary')).lower() not in ['none', 'nan', '', 'not mentioned', '---']) or (row.get('cashback_rates') and str(row.get('cashback_rates')).lower() not in ['none', 'nan', '', 'not mentioned', '---']) else 'No'}</span>
</div>
</div>

<!-- 2. AI Powerful Shoutout -->
<div class="modal-section-title" style="margin-top: 5px;">
<span>🚀</span> Why this card is special?
</div>
<div class="modal-text-content" style="border-left: 3px solid #06b6d4; background: rgba(6, 182, 212, 0.1);">
{row.get('ai_summary', 'Generating summary... (Please refresh in a moment)')}
</div>

<!-- 3. More Details (Buckets) -->
<details style="margin-top: 20px; border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; overflow: hidden;">
<summary style="padding: 15px; background: rgba(255,255,255,0.05); cursor: pointer; font-weight: 700; color: #fff; list-style: none; display: flex; align-items: center; justify-content: center;">
Tap for All Details / Benefits ⬇️
</summary>
<div style="padding: 20px;">

<!-- Bucket 1: Financial & Eligibility -->
<h5 style="color: #38bdf8; margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 5px;">1. Financial & Eligibility</h5>
{create_dynamic_grid([
    ("Min Salary", row['minimum_salary_requirement'], "💰"),
    ("Annual Fee", row['annual_fee'], "💳"),
    ("FX Fee", row.get('foreign_currency_fee'), "💱"),
    ("Balance Transfer", row.get('balance_transfer_eligibility'), "🔄")
])}

<!-- Bucket 2: Rewards & Earnings -->
<h5 style="color: #38bdf8; margin: 25px 0 15px 0; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 5px;">2. Rewards & Earnings</h5>
{create_dynamic_grid([
    ("Points Earning", row.get('points_earning_rates'), "⭐"),
    ("Cashback Rates", row.get('cashback_rates'), "💵"),
    ("Welcome Bonus", row['welcome_bonus'], "🎁"),
    ("Cashback Summary", row.get('cashback_summary'), "📝")
])}

<!-- Bucket 3: Travel & Mobility -->
<h5 style="color: #38bdf8; margin: 25px 0 15px 0; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 5px;">3. Travel & Mobility</h5>
{create_dynamic_grid([
    ("Lounge Access", row.get('airport_lounge_access'), "🛋️"),
    ("Travel Insurance", row.get('travel_insurance'), "🛡️"),
    ("Airport Transfers", row.get('airport_transfers'), "🚕"),
    ("Hotel Discounts", row.get('hotel_discounts'), "🏨")
])}

<!-- Bucket 4: Lifestyle & Discounts -->
<h5 style="color: #38bdf8; margin: 25px 0 15px 0; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 5px;">4. Lifestyle & Discounts</h5>
{create_dynamic_grid([
    ("Dining Offers", row.get('dining_discounts'), "🍽️"),
    ("Cinema Offers", row.get('cinema_offers'), "🎬"),
    ("Golf Privileges", row.get('golf_privileges'), "⛳"),
    ("Valet Parking", row.get('valet_parking'), "🚗")
])}

<!-- Bucket 5: Security & Protection -->
<h5 style="color: #38bdf8; margin: 25px 0 15px 0; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 5px;">5. Security & Protection</h5>
{safe_fmt("Purchase Protection", row.get('purchase_protection'), "🛍️")}
{safe_fmt("Extended Warranty", row.get('extended_warranty'), "🔧")}

<!-- Bucket 6: Other Benefits -->
<h5 style="color: #38bdf8; margin: 25px 0 15px 0; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 5px;">6. Other Benefits</h5>
<ul class="modal-benefits-list">
{benefits_html}
</ul>

</div>
</details>

</div>

<div class="modal-footer" style="display: flex; gap: 15px;">
<a href="{row['url']}" target="_blank" class="apply-btn" style="flex: 1; background: linear-gradient(135deg, #059669 0%, #10b981 100%); box-shadow: 0 10px 30px -10px rgba(16, 185, 129, 0.6);">
Apply Now 🚀
</a>
</div>
</div>
</div>
"""
    return html
