import streamlit as st
from utils import load_css

# --- PAGE CONFIGURATION ---
# Updated title as per user request
st.set_page_config(
    page_title="Smart Spending UAE",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- THEME TOGGLE (SIDEBAR TOP) ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

with st.sidebar:
    def update_theme():
        st.session_state.theme = 'dark' if st.session_state.theme_toggle else 'light'
    
    is_dark = st.session_state.theme == 'dark'
    st.toggle("Dark Mode", value=is_dark, key="theme_toggle", on_change=update_theme)
    st.markdown("---")
    
    # --- CSS HACK TO MOVE TOGGLE ABOVE NAV ---
    st.markdown("""
        <style>
            /* Force the sidebar content to be a flex column */
            [data-testid="stSidebar"] > div > div {
                display: flex;
                flex-direction: column;
            }
            /* Move the Navigation (Page List) to the bottom (order 2) */
            [data-testid="stSidebarNav"] {
                order: 2;
            }
            /* Move the User Content (Toggle) to the top (order 1) */
            [data-testid="stSidebarUserContent"] {
                order: 1;
            }
        </style>
    """, unsafe_allow_html=True)

# ==============================================
# START OF NEWS TICKER CODE
# ==============================================

# --- 1. DAILY NEWS HEADLINES (LOADED FROM FILE) ---
try:
    with open('streamlit_app/news.txt', 'r') as f:
        news_items = [line.strip() for line in f.readlines() if line.strip()]
except FileNotFoundError:
    news_items = [
        "Welcome to Smart Spending UAE",
        "Compare the best credit cards in the UAE",
        "Update news.txt to change these headlines"
    ]

# Combine the items with a separator for display
news_string = "  +++  ".join(news_items)

# --- 2. NEWS TICKER COMPONENT (CSS & HTML INJECTION) ---
st.markdown(
    f"""
    <style>
    /* --- CSS STYLES START --- */
    /* The Container: Defines the background area */
    .ticker-wrap {{
        width: 100%;
        overflow: hidden; /* Hides text when it moves off-screen */
        background-color: var(--card-bg); /* Dynamic Theme Background */
        padding: 10px 0;
        margin-bottom: 20px; /* Space before main title */
        border-top: 1px solid var(--card-border);
        border-bottom: 1px solid var(--card-border);
        white-space: nowrap;
        box-shadow: 0 4px 6px var(--shadow-color);
    }}

    /* The Moving Element: The block that scrolls */
    .ticker {{
        display: inline-block;
        /* The animation: name, duration, curve, loop */
        animation: ticker-scroll 70s linear infinite;
        padding-left: 100%; /* Start off-screen right */
    }}

    /* The Text Styling */
    .ticker-item {{
        display: inline-block;
        font-size: 1rem;
        color: var(--text-primary); /* Dynamic Theme Text */
        font-family: 'Outfit', sans-serif;
        font-weight: 500;
    }}

    /* The Animation Keyframes: Defines movement from right to left */
    @keyframes ticker-scroll {{
        0% {{ transform: translate3d(0, 0, 0); visibility: visible; }}
        100% {{ transform: translate3d(-100%, 0, 0); }}
    }}
    /* --- CSS STYLES END --- */
    </style>

    <div class="ticker-wrap">
        <div class="ticker">
            <div class="ticker-item">Latest Financial News: &nbsp;&nbsp; {news_string}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
# ==============================================
# END OF NEWS TICKER CODE
# ==============================================



# --- CUSTOM CSS & ANIMATION ---
load_css()

# Hero Typography overrides for this page
st.markdown("""
<style>
    /* Hero Typography - Default (Desktop) */
    .hero-title {
        font-family: 'Outfit', sans-serif;
        font-size: 4rem; /* Big size for desktop */
        font-weight: 800;
        line-height: 1.1;
        color: var(--text-primary) !important;
        margin-bottom: 1rem;
        text-shadow: 0 0 30px rgba(6, 182, 212, 0.2);
    }
    .hero-subtitle {
        font-size: 1.3rem;
        color: var(--text-secondary) !important;
        line-height: 1.6;
        margin-bottom: 2rem;
    }
    .highlight {
        color: var(--accent-primary) !important; /* Neon Cyan */
        text-shadow: 0 0 15px rgba(6, 182, 212, 0.5);
    }

    /* --- MOBILE ADJUSTMENTS --- */
    /* Increased breakpoint to 768px to catch more devices */
    @media only screen and (max-width: 768px) {
        .hero-title {
            font-size: 1.4rem !important; /* Increased by ~15% from 1.2rem */
        }
        .hero-subtitle {
            font-size: 0.8rem !important;
            margin-bottom: 1rem;
        }
    }

    /* --- FINAL CTA BUTTON (Cosmic Pulse) --- */
    /* Targeting the actual Streamlit button */
    div.stButton > button {
        position: relative;
        width: 100%;
        padding: 1rem 2rem !important;
        background: var(--button-bg) !important;
        color: var(--button-text) !important;
        text-decoration: none;
        text-transform: uppercase;
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        font-size: 1.2rem !important;
        letter-spacing: 2px;
        border: 1px solid var(--button-border) !important;
        border-radius: 8px !important;
        overflow: hidden;
        transition: all 0.5s ease !important;
        box-shadow: 0 0 10px var(--shadow-color) !important;
    }

    div.stButton > button:hover {
        background: var(--accent-primary) !important;
        color: #ffffff !important;
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 20px var(--accent-primary), 0 0 60px var(--accent-primary) !important;
        transform: scale(1.02);
    }

    /* FORCE child elements (like <p>) to change color too */
    div.stButton > button:hover p,
    div.stButton > button:hover div,
    div.stButton > button:hover span {
        color: #ffffff !important;
    }

    div.stButton > button:active {
        transform: scale(0.98);
    }
</style>
""", unsafe_allow_html=True)

# --- HERO SECTION ---
# Using columns to create the layout from the HTML design
col1, col2 = st.columns([1.5, 1])

with col1:
    st.markdown("""
        <div class="hero-container">
            <h1 class="hero-title"><span class="highlight">The Future of Smart Spending Using AI</span></h1>
            <p class="hero-subtitle">Stop guessing. Compare interest rates, rewards, and fees side-by-side with our interactive tools built on Streamlit.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Call to Action
    if st.button("Start Comparing Now", type="primary", use_container_width=True):
        st.switch_page("pages/1_Compare_Cards.py")

with col2:
    # Display User's Custom Image Simply
    st.image("streamlit_app/static/cards/CC_Tarek_T_future.png", use_container_width=True)

st.markdown("---")

# --- FEATURES SECTION (Adapted from original Home.py) ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <a href="Compare_Cards" target="_self" style="text-decoration: none;">
        <div class="card-container" style="text-align: center;">
            <div style="font-size: 2.5rem; margin-bottom: 10px; text-shadow: 0 0 15px rgba(6, 182, 212, 0.5);">🔍</div>
            <h3 style="margin: 10px 0; color: #f8fafc;">Smart Comparison</h3>
            <p style="color: #94a3b8;">Filter by minimum salary, annual fees, and specific benefits like lounge access or cashback.</p>
        </div>
    </a>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <a href="AI_Assistant" target="_self" style="text-decoration: none;">
        <div class="card-container" style="text-align: center;">
            <div style="font-size: 2.5rem; margin-bottom: 10px; text-shadow: 0 0 15px rgba(139, 92, 246, 0.5);">🤖</div>
            <h3 style="margin: 10px 0; color: #f8fafc;">AI Assistant</h3>
            <p style="color: #94a3b8;">Not sure what you need? Tell our AI about your spending habits and get tailored advice.</p>
        </div>
    </a>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <a href="Real_Time_Data" target="_self" style="text-decoration: none;">
        <div class="card-container" style="text-align: center;">
            <div style="font-size: 2.5rem; margin-bottom: 10px; text-shadow: 0 0 15px rgba(6, 182, 212, 0.5);">📊</div>
            <h3 style="margin: 10px 0; color: #f8fafc;">Real-time Data</h3>
            <p style="color: #94a3b8;">Up-to-date information on interest rates, fees, and limited-time offers from top UAE banks.</p>
        </div>
    </a>
    """, unsafe_allow_html=True)
