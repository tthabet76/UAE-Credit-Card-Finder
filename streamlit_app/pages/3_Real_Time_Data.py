import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_css
from db_utils import get_db_connection

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Real-time Data - CardCompare",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS ---
load_css()

# Additional CSS for this page to match Home
st.markdown("""
<style>
    /* Page Background */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%) !important;
        background-attachment: fixed !important;
    }
    
    /* Text Colors */
    h1, h2, h3, h4, .stMarkdown, p, span, div {
        color: #e2e8f0 !important;
    }
    
    /* Plotly Chart Backgrounds */
    .js-plotly-plot .plotly .main-svg {
        background: rgba(0,0,0,0) !important;
    }
    
    /* Card Containers for Graphs */
    .graph-container {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# --- DATA LOADING ---
@st.cache_data
def load_data():
    try:
        conn = get_db_connection()
        if not conn:
            return pd.DataFrame()
            
        query = """
        SELECT 
            bank_name, 
            min_salary_numeric, 
            max_cashback_rate 
        FROM credit_cards_details
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df = load_data()

# --- HEADER ---
st.markdown('<h1 style="text-align: center; margin-bottom: 2rem; text-shadow: 0 0 20px rgba(6, 182, 212, 0.5);">Real-time Market Insights 📊</h1>', unsafe_allow_html=True)

if df.empty:
    st.warning("No data available to display.")
    st.stop()

# --- METRICS ROW ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Cards Tracked", len(df))
with col2:
    st.metric("Banks Monitored", df['bank_name'].nunique())
with col3:
    st.metric("Avg Max Cashback", f"{df['max_cashback_rate'].mean():.1f}%")

st.markdown("---")

# --- GRAPHS ROW 1 ---
c1, c2 = st.columns(2)

with c1:
    # 1. Salary Requirement Distribution
    st.markdown("### 💰 Salary Requirements")
    st.markdown("Count of cards available for different salary brackets.")

    # Binning logic
    bins = [0, 5000, 10000, 20000, float('inf')]
    labels = ['< 5k', '5k - 10k', '10k - 20k', '> 20k']
    df['Salary_Bracket'] = pd.cut(df['min_salary_numeric'], bins=bins, labels=labels, right=False)

    salary_counts = df['Salary_Bracket'].value_counts().reindex(labels).reset_index()
    salary_counts.columns = ['Salary Bracket', 'Count']

    fig_salary = px.bar(
        salary_counts, 
        x='Salary Bracket', 
        y='Count',
        text='Count',
        color='Count',
        color_continuous_scale='Blues',
        template='plotly_dark'
    )
    fig_salary.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_family="Outfit",
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    fig_salary.update_traces(textposition='outside')

    with st.container():
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        st.plotly_chart(fig_salary, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

with c2:
    # 2. Cashback Comparison
    st.markdown("### 💸 Cashback Analysis")
    st.markdown("Distribution of maximum cashback rates across all cards.")

    fig_cashback = px.histogram(
        df, 
        x='max_cashback_rate', 
        nbins=20,
        labels={'max_cashback_rate': 'Max Cashback Rate (%)'},
        color_discrete_sequence=['#8b5cf6'], # Violet
        template='plotly_dark'
    )
    fig_cashback.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_family="Outfit",
        bargap=0.1,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    with st.container():
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        st.plotly_chart(fig_cashback, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# 3. Cards per Bank
st.markdown("### 🏦 Cards per Bank")
st.markdown("Number of credit cards offered by each bank in our database.")

bank_counts = df['bank_name'].value_counts().reset_index()
bank_counts.columns = ['Bank', 'Count']

fig_bank = px.bar(
    bank_counts, 
    x='Count', 
    y='Bank', 
    orientation='h',
    text='Count',
    color='Count',
    color_continuous_scale='Tealgrn',
    template='plotly_dark'
)
fig_bank.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font_family="Outfit",
    yaxis={'categoryorder':'total ascending'},
    height=600
)
fig_bank.update_traces(textposition='outside')

with st.container():
    st.markdown('<div class="graph-container">', unsafe_allow_html=True)
    st.plotly_chart(fig_bank, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

