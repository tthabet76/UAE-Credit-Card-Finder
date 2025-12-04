import streamlit as st
from utils import load_css

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="CardCompare - Smart Spending",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS & ANIMATION ---
load_css()

# Hero Typography overrides for this page
st.markdown("""
<style>
    /* --- HOME PAGE SPECIFIC DARK THEME OVERRIDES --- */
    
    /* Global Background - Deep Space Gradient */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%) !important;
        background-attachment: fixed !important;
    }
    
    /* Force text color for Home Page */
    .stApp, .stApp p, .stApp div, .stApp span, .stApp label, .stApp li, .stApp td, .stApp th {
        color: #e2e8f0 !important;
    }
    
    /* Headings */
    h1, h2, h3, h4, h5, h6, .stHeading {
        color: #f8fafc !important;
        text-shadow: 0 0 20px rgba(6, 182, 212, 0.1);
    }

    /* Card Container - Glassmorphism */
    .card-container {
        background: rgba(30, 41, 59, 0.7) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Sidebar - Dark Theme for Home */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }

    /* Hero Typography */
    .hero-title {
        font-family: 'Outfit', sans-serif;
        font-size: 4rem;
        font-weight: 800;
        line-height: 1.1;
        color: #ffffff !important;
        margin-bottom: 1rem;
        text-shadow: 0 0 30px rgba(6, 182, 212, 0.2);
    }
    .hero-subtitle {
        font-size: 1.3rem;
        color: #94a3b8 !important;
        line-height: 1.6;
        margin-bottom: 2rem;
    }
    .highlight {
        color: #06b6d4 !important; /* Neon Cyan */
        text-shadow: 0 0 15px rgba(6, 182, 212, 0.5);
    }

    /* --- FINAL CTA BUTTON (White Cosmic Pulse) --- */
    /* Targeting the actual Streamlit button */
    div.stButton > button {
        position: relative;
        width: 100%;
        padding: 1rem 2rem !important;
        background: #0f172a !important;
        color: #ffffff !important;
        text-decoration: none;
        text-transform: uppercase;
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        font-size: 1.2rem !important;
        letter-spacing: 2px;
        border: 1px solid #ffffff !important;
        border-radius: 8px !important;
        overflow: hidden;
        transition: all 0.5s ease !important;
        box-shadow: 0 0 10px rgba(255, 255, 255, 0.3), 0 0 30px rgba(255, 255, 255, 0.1) !important;
    }

    div.stButton > button:hover {
        background: #ffffff !important;
        color: #00008b !important; /* Dark Blue */
        border-color: #ffffff !important;
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.8), 0 0 60px rgba(255, 255, 255, 0.6) !important;
        transform: scale(1.02);
    }

    /* FORCE child elements (like <p>) to change color too */
    div.stButton > button:hover p,
    div.stButton > button:hover div,
    div.stButton > button:hover span {
        color: #00008b !important;
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

    # Original functional button (hidden/secondary for now)
    # if st.button("Start Comparing Now 🚀", type="primary", use_container_width=False):
    #     st.switch_page("pages/1_Compare_Cards.py")

with col2:
    # Display User's Custom Image Simply
    st.image("streamlit_app/static/cards/CC_Tarek_T_future.png", use_container_width=True)

st.markdown("---")

# --- FEATURES SECTION (Adapted from original Home.py) ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="card-container" style="text-align: center;">
        <div style="font-size: 2.5rem; margin-bottom: 10px; text-shadow: 0 0 15px rgba(6, 182, 212, 0.5);">🔍</div>
        <h3 style="margin: 10px 0; color: #f8fafc;">Smart Comparison</h3>
        <p style="color: #94a3b8;">Filter by minimum salary, annual fees, and specific benefits like lounge access or cashback.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card-container" style="text-align: center;">
        <div style="font-size: 2.5rem; margin-bottom: 10px; text-shadow: 0 0 15px rgba(139, 92, 246, 0.5);">🤖</div>
        <h3 style="margin: 10px 0; color: #f8fafc;">AI Assistant</h3>
        <p style="color: #94a3b8;">Not sure what you need? Tell our AI about your spending habits and get tailored advice.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="card-container" style="text-align: center;">
        <div style="font-size: 2.5rem; margin-bottom: 10px; text-shadow: 0 0 15px rgba(6, 182, 212, 0.5);">📊</div>
        <h3 style="margin: 10px 0; color: #f8fafc;">Real-time Data</h3>
        <p style="color: #94a3b8;">Up-to-date information on interest rates, fees, and limited-time offers from top UAE banks.</p>
    </div>
    """, unsafe_allow_html=True)
