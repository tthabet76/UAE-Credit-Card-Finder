import streamlit as st
import os

def load_css():
    st.markdown("""
    <style>
        /* Import modern font */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

        /* Safer Global Selectors */
        html, body {
            font-family: 'Outfit', sans-serif;
            color: #333;
        }

        /* Global Background - Warm Neutral Light Theme */
        .stApp {
            background: linear-gradient(135deg, #fdfbf7 0%, #f4f7f6 100%);
            background-attachment: fixed;
            color: #333;
        }
        
        /* Force text color for Streamlit elements */
        .stMarkdown, .stText, p, div, label, li, span {
            color: #333 !important;
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: #1a1a1a !important;
            font-weight: 700;
            letter-spacing: -0.5px;
            text-shadow: none;
        }

        /* Card Container - Clean White */
        .card-container {
            background-color: #ffffff;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            padding: 24px;
            margin-bottom: 20px;
            border: 1px solid rgba(0,0,0,0.05);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .card-container:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 30px rgba(0,0,0,0.1);
        }

        /* Typography */
        .bank-name {
            font-size: 0.8rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-weight: 600;
            margin-bottom: 6px;
        }

        .card-title {
            font-size: 1.4rem;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 15px;
            background: none;
            -webkit-text-fill-color: initial;
        }

        /* Stats Grid */
        .stats-grid {
            display: flex;
            gap: 25px;
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid #f1f5f9;
        }

        .stat-item {
            display: flex;
            flex-direction: column;
        }

        .stat-label {
            font-size: 0.7rem;
            color: #94a3b8;
            text-transform: uppercase;
            font-weight: 600;
            margin-bottom: 4px;
        }

        .stat-value {
            font-size: 1.1rem;
            font-weight: 600;
            color: #333;
            text-shadow: none;
        }

        /* Benefits List */
        .benefit-item {
            font-size: 0.9rem;
            color: #475569;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
        }
        
        .benefit-icon {
            margin-right: 10px;
            color: #06b6d4; /* Keep Cyan Accent */
            text-shadow: none;
        }

        /* Buttons */
        /* Buttons */
        .stButton>button {
            background: #0f172a; /* Dark Button for Contrast */
            color: white !important;
            border-radius: 8px;
            border: none;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            transition: all 0.3s;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        
        /* Force child elements in buttons to be white */
        .stButton>button p, .stButton>button div, .stButton>button span {
            color: white !important;
        }

        /* Specific fix for Buttons inside Dialogs/Modals */
        div[data-testid="stDialog"] .stButton > button,
        div[role="dialog"] .stButton > button {
            background: #0f172a !important;
            color: white !important;
            border: 1px solid rgba(255,255,255,0.1);
        }

        /* FORCE Primary Buttons to have white text everywhere */
        button[kind="primary"], 
        button[kind="primary"] p, 
        button[kind="primary"] div, 
        button[kind="primary"] span {
            color: #ffffff !important;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(0,0,0,0.15);
            background: #1e293b;
        }
        
        /* Sidebar - Light Theme */
        [data-testid="stSidebar"] {
            background-color: #ffffff !important;
            border-right: 1px solid #f1f5f9;
        }
        
        [data-testid="stSidebar"] * {
            color: #333 !important;
        }
        
        /* Reset Pills to Default (Streamlit handles light mode well) */
        div[data-testid="stPills"] span {
            color: inherit !important;
            font-weight: normal;
        }

        /* Force Dialog/Modal background to be Dark (User Preference) */
        div[data-testid="stDialog"], div[role="dialog"] {
            background-color: #1e293b !important;
            color: #f8fafc !important;
            border: 1px solid rgba(255,255,255,0.1);
        }
        div[data-testid="stDialog"] > div, div[role="dialog"] > div {
             background-color: #1e293b !important;
             color: #f8fafc !important;
        }
        div[data-testid="stDialog"] p, div[role="dialog"] p,
        div[data-testid="stDialog"] div, div[role="dialog"] div,
        div[data-testid="stDialog"] span, div[role="dialog"] span,
        div[data-testid="stDialog"] h1, div[data-testid="stDialog"] h2, 
        div[data-testid="stDialog"] h3, div[data-testid="stDialog"] h4 {
            color: #f8fafc !important;
            background-color: transparent !important;
        }

        /* Secondary Button Style */
        .btn-secondary {
            background: rgba(255, 255, 255, 0.05);
            color: #e2e8f0;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        /* Custom Links as Buttons */
        .apply-btn {
            display: inline-block;
            background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
            color: white !important;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            text-align: center;
            width: 100%;
            margin-bottom: 10px;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(6, 182, 212, 0.3);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .apply-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(6, 182, 212, 0.5);
            filter: brightness(1.1);
        }

        .details-btn {
            display: inline-block;
            background: rgba(255, 255, 255, 0.03);
            color: #06b6d4 !important;
            padding: 10px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            text-align: center;
            width: 100%;
            border: 1px solid rgba(6, 182, 212, 0.3);
            transition: all 0.3s;
        }

        .details-btn:hover {
            background: rgba(6, 182, 212, 0.1);
            color: #22d3ee !important;
            border-color: #22d3ee;
            box-shadow: 0 0 15px rgba(6, 182, 212, 0.2);
        }

        /* Chat Bubbles */
        .user-bubble {
            background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
            color: white;
            border-radius: 18px 18px 0 18px;
            padding: 14px 20px;
            margin: 10px 0;
            text-align: right;
            display: inline-block;
            float: right;
            clear: both;
            box-shadow: 0 4px 15px rgba(6, 182, 212, 0.2);
        }
        
        .ai-bubble {
            background: #f1f5f9; /* Light Grey */
            color: #333333; /* Dark Text */
            border: 1px solid #e2e8f0;
            border-radius: 18px 18px 18px 0;
            padding: 14px 20px;
            margin: 10px 0;
            display: inline-block;
            float: left;
            clear: both;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        
        /* Glass Card */
        .glass-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
            margin-bottom: 20px;
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .glass-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.15);
        }
        
        .card-content {
            display: flex;
            flex-direction: row;
            padding: 20px;
            gap: 25px;
        }
        
        .card-image-container {
            flex: 0 0 180px; /* Wider for landscape */
            display: flex;
            align-items: center;
            justify-content: center;
            background: #f8f9fa;
            border-radius: 12px;
            padding: 10px;
            height: 120px; /* Fixed height to force landscape box */
        }
        
        .card-img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));
        }
        
        .card-details {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        
        .card-header {
            margin-bottom: 10px;
        }
        
        .card-title {
            font-size: 1.4rem;
            font-weight: 700;
            color: #1a1a1a;
            margin: 0 0 5px 0;
        }
        
        .card-bank {
            font-size: 0.9rem;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
            margin: 0;
        }
        
        .card-stats {
            display: flex;
            gap: 30px;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid #eee;
        }
        
        .stat-item {
            display: flex;
            flex-direction: column;
        }
        
        .stat-label {
            font-size: 0.75rem;
            color: #adb5bd;
            text-transform: uppercase;
            font-weight: 600;
            margin-bottom: 4px;
        }
        
        .stat-value {
            font-size: 1rem;
            font-weight: 600;
            color: #212529;
        }
        
        .card-benefits {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .benefit-tag {
            background: #e7f5ff;
            color: #0056b3;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        /* Mobile Optimization - Compact View */
        @media (max-width: 768px) {
            .card-container {
                padding: 10px !important;
                margin-bottom: 10px !important;
            }
            
            .card-content {
                flex-direction: row !important; /* Keep horizontal */
                padding: 0 !important;
                gap: 10px !important;
                align-items: center !important;
            }
            
            .card-image-container {
                flex: 0 0 80px !important; /* Fixed small width */
                height: 50px !important;
                min-height: 0 !important;
                padding: 2px !important;
                margin: 0 !important;
            }
            
            .card-img {
                max-height: 100% !important;
            }
            
            .card-details {
                text-align: left !important;
                align-items: flex-start !important;
                gap: 2px !important;
            }
            
            .card-header {
                margin-bottom: 2px !important;
            }
            
            .card-title {
                font-size: 0.95rem !important;
                margin-bottom: 0 !important;
                line-height: 1.2 !important;
            }
            
            .card-bank {
                font-size: 0.7rem !important;
                display: none; /* Hide bank name to save space if title has it */
            }
            
            .card-stats {
                border: none !important;
                margin: 0 !important;
                padding: 0 !important;
                gap: 10px !important;
                justify-content: flex-start !important;
            }
            
            .stat-item {
                flex-direction: column !important;
                gap: 0px !important;
                align-items: flex-start !important;
                margin-right: 0px !important;
                flex: 1 1 0px !important; /* Equal width columns */
                min-width: 0 !important; /* Allow text wrap */
                word-wrap: break-word !important;
            }
            
            .stat-label {
                font-size: 0.6rem !important;
                display: block !important; /* Show labels */
                line-height: 1 !important;
                margin-bottom: 2px !important;
            }
            
            .stat-value {
                font-size: 0.75rem !important;
                font-weight: 600 !important;
                line-height: 1.1 !important;
            }
            
            /* Remove icons */
            .stat-value::before {
                content: none !important; 
            }
            
            /* Hide benefits on mobile list view */
            .card-benefits {
                display: none !important;
            }
            
            /* Show mobile actions */
            .mobile-actions {
                display: block !important;
                margin-top: 5px;
            }
        }

        /* --- GLASS SHEET MODAL (CSS ONLY) --- */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(4px);
            z-index: 9999;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s ease, visibility 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        /* Show modal when target is active */
        .modal-overlay:target {
            opacity: 1;
            visibility: visible;
        }

        .modal-content {
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
        }

        .modal-overlay:target .modal-content {
            transform: scale(1);
        }

        .modal-close {
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
        }
        
        .modal-close:hover {
            background: rgba(0, 0, 0, 0.1);
        }

        .modal-header {
            padding: 25px 25px 15px 25px;
            border-bottom: 1px solid rgba(0,0,0,0.05);
            text-align: center;
        }
        
        .modal-img-container {
            height: 140px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 15px;
        }
        
        .modal-img {
            max-height: 100%;
            max-width: 100%;
            object-fit: contain;
            filter: drop-shadow(0 8px 16px rgba(0,0,0,0.15));
        }

        .modal-title {
            font-size: 1.5rem;
            font-weight: 800;
            color: #f8fafc !important;
            margin: 0;
            line-height: 1.2;
        }
        
        .modal-bank {
            font-size: 0.9rem;
            color: #cbd5e1 !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 5px;
        }

        .modal-body {
            padding: 25px;
            flex: 1;
        }

        .modal-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 25px;
        }
        
        .modal-stat-box {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 12px;
            text-align: center;
        }
        
        .modal-stat-label {
            font-size: 0.7rem;
            color: #94a3b8 !important;
            text-transform: uppercase;
            display: block;
            margin-bottom: 4px;
        }
        
        .modal-stat-value {
            font-size: 0.95rem;
            font-weight: 700;
            color: #f8fafc !important;
        }

        .modal-section-title {
            font-size: 1rem;
            font-weight: 700;
            margin: 20px 0 10px 0;
            color: #e2e8f0 !important;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .modal-benefits-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        
        .modal-benefit-item {
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            font-size: 0.95rem;
            color: #cbd5e1 !important;
            display: flex;
            gap: 10px;
        }
        
        .modal-benefit-item:last-child {
            border-bottom: none;
        }

        .modal-footer {
            padding: 20px;
            background: rgba(30, 41, 59, 0.9);
            border-top: 1px solid rgba(255,255,255,0.1);
            position: sticky;
            bottom: 0;
            backdrop-filter: blur(10px);
        }

        .modal-text-content {
            font-size: 0.95rem;
            color: #cbd5e1 !important;
            margin-bottom: 15px;
        }

        /* Mobile Bottom Sheet Animation */
        @media (max-width: 768px) {
            .modal-overlay {
                align-items: flex-end; /* Align to bottom */
            }
            
            .modal-content {
                width: 100%;
                max-width: 100%;
                border-radius: 24px 24px 0 0; /* Rounded top only */
                max-height: 85vh;
                transform: translateY(100%); /* Start off-screen */
                transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            }
            
            .modal-overlay:target .modal-content {
                transform: translateY(0); /* Slide up */
            }
        }

    </style>
    """, unsafe_allow_html=True)

import base64
import json
import re

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

@st.cache_data(ttl=3600)
def load_card_mapping():
    """Loads the card image mapping from JSON."""
    mapping_file = os.path.join(os.path.dirname(__file__), 'card_image_mapping.json')
    if os.path.exists(mapping_file):
        try:
            with open(mapping_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

@st.cache_data(ttl=3600)
def get_image_base64_cached(file_path):
    """Reads an image file and returns the base64 string (Cached)."""
    return get_image_base64(file_path)

def get_card_image_source(row):
    """
    Finds the image and returns a Base64 string source for HTML.
    """
    # Load mapping (Cached)
    card_mapping = load_card_mapping()

    card_id = str(row['id'])
    filename = None
    
    # 1. Try Mapping
    if card_id in card_mapping and card_mapping[card_id]:
        filename = card_mapping[card_id]
        
    # Handle Generic
    if filename == "Generic Card":
        return "https://via.placeholder.com/300x180?text=Generic+Card"
    
    # 2. If no filename, return placeholder
    if not filename:
        return "https://via.placeholder.com/300x180?text=No+Image"
        
    # 3. Construct absolute file path
    # utils.py is in streamlit_app/, images are in streamlit_app/static/cards/
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, 'static', 'cards', filename)
    
    if os.path.exists(file_path):
        return get_image_base64_cached(file_path)
        
    return "https://via.placeholder.com/300x180?text=Image+Not+Found"

def get_card_html(row):
    # Get the image source (Base64 or URL)
    image_src = get_card_image_source(row)
    
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
    <a href="#modal-{row['id']}" style="text-decoration: none; color: inherit; display: block;">
        <div class="glass-card">
            <div class="card-content">
                <div class="card-image-container">
                    <img src="{image_src}" class="card-img" alt="{row['card_name']}">
                </div>
                <div class="card-details">
                    <div class="card-header">
                        <h3 class="card-title">{row['card_name']}</h3>
                        <p class="card-bank">{row['bank_name']}</p>
                    </div>
                    <div class="card-stats">
                        <div class="stat-item">
                            <span class="stat-label">Annual Fee</span>
                            <span class="stat-value">{row['annual_fee']}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Min Salary</span>
                            <span class="stat-value">{row['minimum_salary_requirement']}</span>
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
        <a href="#" class="modal-close-area" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; cursor: default;"></a>
        <div class="modal-content">
            <a href="#" class="modal-close">&times;</a>
            <div class="modal-header">
                <div class="modal-img-container">
                    <img src="{image_src}" class="modal-img" alt="{row['card_name']}">
                </div>
                <h2 class="modal-title">{row['card_name']}</h2>
                <p class="modal-bank">{row['bank_name']}</p>
            </div>
            
            <div class="modal-body">
                <div class="modal-grid">
                    <div class="modal-stat-box">
                        <span class="modal-stat-label">Annual Fee</span>
                        <span class="modal-stat-value">{row['annual_fee']}</span>
                    </div>
                    <div class="modal-stat-box">
                        <span class="modal-stat-label">Min Salary</span>
                        <span class="modal-stat-value">{row['minimum_salary_requirement']}</span>
                    </div>
                    <div class="modal-stat-box">
                        <span class="modal-stat-label">Min Spend</span>
                        <span class="modal-stat-value">{row['minimum_spend_requirement']}</span>
                    </div>
                    <div class="modal-stat-box">
                        <span class="modal-stat-label">Balance Transfer</span>
                        <span class="modal-stat-value">{row['balance_transfer_eligibility']}</span>
                    </div>
                </div>

                <div class="modal-section-title">🎁 Welcome Bonus</div>
                <p class="modal-text-content">{row['welcome_bonus']}</p>

                <div class="modal-section-title">💰 Cashback & Rewards</div>
                <p class="modal-text-content">{row['cashback_rates']}</p>
                
                <div class="modal-section-title">✨ Key Benefits</div>
                <ul class="modal-benefits-list">
                    {benefits_html}
                </ul>
            </div>

            <div class="modal-footer">
                <a href="{row['url']}" target="_blank" class="apply-btn">Apply Now 🔗</a>
            </div>
        </div>
    </div>
    """
    return html.replace('\n', ' ')
