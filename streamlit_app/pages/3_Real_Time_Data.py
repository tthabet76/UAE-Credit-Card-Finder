import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_css, get_card_html
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
# CSS handled by utils.load_css

# --- HELPER FUNCTIONS ---
def get_mini_card_html(row):
    """Returns a simplified HTML card for the Real-time Data page."""
    from utils import get_card_image_source
    image_src = get_card_image_source(row)
    
    return f"""
    <div class="mini-card">
        <div class="mini-card-img-container">
            <img src="{image_src}" alt="{row['card_name']}">
        </div>
        <h4>{row['card_name']}</h4>
        <p>{row['bank_name']}</p>
    </div>
    """

# --- DATA LOADING ---
@st.cache_data
def load_data():
    try:
        conn = get_db_connection()
        if not conn:
            return pd.DataFrame()
            
        query = "SELECT * FROM credit_cards_details"
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
    avg_cards = len(df) / df['bank_name'].nunique() if df['bank_name'].nunique() > 0 else 0
    st.metric("Avg Cards per Bank", f"{avg_cards:.1f}")

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
        margin=dict(l=20, r=20, t=40, b=20),
        clickmode='event+select'
    )
    fig_salary.update_traces(textposition='outside')

    with st.container():
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        # Enable selection events
        event_salary = st.plotly_chart(fig_salary, use_container_width=True, on_select="rerun", selection_mode="points", key="salary_chart")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- INTERACTION LOGIC (SALARY) ---
    if event_salary and len(event_salary.selection["points"]) > 0:
        selected_point = event_salary.selection["points"][0]
        selected_bracket = selected_point["x"]
        
        st.markdown(f"**Featured Cards ({selected_bracket})**")
        
        filtered_cards = pd.DataFrame()
        if selected_bracket == '< 5k':
            filtered_cards = df[df['min_salary_numeric'] < 5000]
        elif selected_bracket == '5k - 10k':
            filtered_cards = df[(df['min_salary_numeric'] >= 5000) & (df['min_salary_numeric'] < 10000)]
        elif selected_bracket == '10k - 20k':
            filtered_cards = df[(df['min_salary_numeric'] >= 10000) & (df['min_salary_numeric'] < 20000)]
        elif selected_bracket == '> 20k':
            filtered_cards = df[df['min_salary_numeric'] >= 20000]
            
        if not filtered_cards.empty:
            cols = st.columns(3) # Show in a grid of 3
            for idx, (i, row) in enumerate(filtered_cards.head(6).iterrows()):
                with cols[idx % 3]:
                    st.markdown(get_mini_card_html(row), unsafe_allow_html=True)
        else:
            st.info("No cards found.")

with c2:
    # 2. Cashback Comparison
    st.markdown("### 💸 Cashback Analysis")
    st.markdown("Distribution of maximum cashback rates.")

    # Manual Binning for Cashback to enable Click Interaction
    # Bins: 0-1%, 1-3%, 3-5%, 5%+
    cb_bins = [0, 1, 3, 5, float('inf')]
    cb_labels = ['0-1%', '1-3%', '3-5%', '5%+']
    df['Cashback_Bracket'] = pd.cut(df['max_cashback_rate'], bins=cb_bins, labels=cb_labels, right=False)
    
    cashback_counts = df['Cashback_Bracket'].value_counts().reindex(cb_labels).reset_index()
    cashback_counts.columns = ['Cashback Bracket', 'Count']

    fig_cashback = px.bar(
        cashback_counts, 
        x='Cashback Bracket', 
        y='Count',
        text='Count',
        color='Count',
        color_continuous_scale='Purples', # Changed to Purples for variety
        template='plotly_dark'
    )
    fig_cashback.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_family="Outfit",
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20),
        clickmode='event+select'
    )
    fig_cashback.update_traces(textposition='outside')

    with st.container():
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        event_cashback = st.plotly_chart(fig_cashback, use_container_width=True, on_select="rerun", selection_mode="points", key="cashback_chart")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- INTERACTION LOGIC (CASHBACK) ---
    if event_cashback and len(event_cashback.selection["points"]) > 0:
        selected_point = event_cashback.selection["points"][0]
        selected_cb_bracket = selected_point["x"]
        
        st.markdown(f"**Featured Cards ({selected_cb_bracket})**")
        
        filtered_cb_cards = pd.DataFrame()
        if selected_cb_bracket == '0-1%':
            filtered_cb_cards = df[df['max_cashback_rate'] < 1]
        elif selected_cb_bracket == '1-3%':
            filtered_cb_cards = df[(df['max_cashback_rate'] >= 1) & (df['max_cashback_rate'] < 3)]
        elif selected_cb_bracket == '3-5%':
            filtered_cb_cards = df[(df['max_cashback_rate'] >= 3) & (df['max_cashback_rate'] < 5)]
        elif selected_cb_bracket == '5%+':
            filtered_cb_cards = df[df['max_cashback_rate'] >= 5]
            
        if not filtered_cb_cards.empty:
            cols = st.columns(3)
            for idx, (i, row) in enumerate(filtered_cb_cards.head(6).iterrows()):
                with cols[idx % 3]:
                    st.markdown(get_mini_card_html(row), unsafe_allow_html=True)
        else:
            st.info("No cards found.")


# 3. Cards per Bank
st.markdown("### 🏦 Cards per Bank")
st.markdown("Number of credit cards offered by each bank.")

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
    height=600,
    margin=dict(l=20, r=20, t=40, b=20),
    clickmode='event+select'
)
fig_bank.update_traces(textposition='outside')

with st.container():
    st.markdown('<div class="graph-container">', unsafe_allow_html=True)
    event_bank = st.plotly_chart(fig_bank, use_container_width=True, on_select="rerun", selection_mode="points", key="bank_chart")
    st.markdown('</div>', unsafe_allow_html=True)

# --- INTERACTION LOGIC (BANK) ---
if event_bank and len(event_bank.selection["points"]) > 0:
    selected_point = event_bank.selection["points"][0]
    selected_bank = selected_point["y"] # Note: y-axis has the labels for horizontal bar
    
    st.markdown(f"### 🏦 Featured Cards from {selected_bank}")
    
    filtered_bank_cards = df[df['bank_name'] == selected_bank]
        
    if not filtered_bank_cards.empty:
        cols = st.columns(6) # Show up to 6 in a single row if possible, or grid
        # Adjust grid based on count
        num_cards = min(len(filtered_bank_cards), 6)
        cols = st.columns(num_cards)
        
        for idx, (i, row) in enumerate(filtered_bank_cards.head(num_cards).iterrows()):
            with cols[idx]:
                st.markdown(get_mini_card_html(row), unsafe_allow_html=True)
    else:
        st.info("No cards found.")

