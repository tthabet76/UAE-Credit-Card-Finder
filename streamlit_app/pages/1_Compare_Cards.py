import streamlit as st
import pandas as pd
from utils import load_css, get_card_html
from db_utils import fetch_all_cards

# 1. Setup
load_css()
st.title("Compare Credit Cards")

# 2. Data Fetching
@st.cache_data(ttl=3600)
def get_cards():
    return fetch_all_cards()

with st.spinner("Loading cards..."):
    try:
        df = get_cards()
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        st.stop()

if df.empty:
    st.warning("No cards found.")
    st.stop()

# 3. Filters
st.sidebar.header("Filters")

# Bank Filter
# Bank Filter
banks = sorted(df['bank_name'].unique().tolist())

# Initialize selection state if not exists
if 'selected_banks' not in st.session_state:
    st.session_state.selected_banks = []

# Top 5 Popular Banks (Adjust based on your data or preference)
top_banks = ["ADCB", "ADIB", "Emirates NBD", "FAB", "Mashreq"]
# Ensure top banks actually exist in the data
top_banks = [b for b in top_banks if b in banks]

st.sidebar.subheader("Select Bank")

# 1. Render Top 5 Checkboxes
for bank in top_banks:
    is_checked = bank in st.session_state.selected_banks
    if st.sidebar.checkbox(bank, value=is_checked, key=f"chk_{bank}"):
        if bank not in st.session_state.selected_banks:
            st.session_state.selected_banks.append(bank)
    else:
        if bank in st.session_state.selected_banks:
            st.session_state.selected_banks.remove(bank)

# 2. "See All" Modal Logic
@st.dialog("Select Banks", width="large")
def show_bank_selector():
    st.write("Search and select multiple banks.")
    
    # Search Bar
    search_query = st.text_input("Search Bank", placeholder="Type to search...", key="bank_search").lower()
    
    # Filter banks based on search
    filtered_banks = [b for b in banks if search_query in b.lower()]
    
    # "Select All" / "Deselect All" for filtered results
    col_tools = st.columns([0.3, 0.3, 0.4])
    with col_tools[0]:
        if st.button("Select All Visible", key="btn_select_all"):
            for b in filtered_banks:
                if b not in st.session_state.selected_banks:
                    st.session_state.selected_banks.append(b)
            st.rerun()
            
    with col_tools[1]:
        if st.button("Clear Selection", key="btn_clear_all_banks"):
            st.session_state.selected_banks = []
            st.rerun()

    st.markdown("---")

    # Render Checkboxes in Grid
    cols = st.columns(3)
    for i, bank in enumerate(filtered_banks):
        col = cols[i % 3]
        with col:
            is_selected = bank in st.session_state.selected_banks
            if st.checkbox(bank, value=is_selected, key=f"modal_chk_{bank}"):
                if bank not in st.session_state.selected_banks:
                    st.session_state.selected_banks.append(bank)
            else:
                if bank in st.session_state.selected_banks:
                    st.session_state.selected_banks.remove(bank)
    
    st.markdown("---")
    if st.button("Apply Filters", type="primary", use_container_width=True):
        st.rerun()

if st.sidebar.button("See All Banks 🏦"):
    show_bank_selector()

# Use the session state for filtering
selected_banks = st.session_state.selected_banks

st.sidebar.markdown("---")
st.sidebar.subheader("💰 Salary Requirement")

# Salary Filter
user_salary = st.sidebar.number_input("Enter your Monthly Salary (AED)", min_value=0, step=1000, value=0)
show_higher_salary = st.sidebar.checkbox("Show cards requiring HIGHER salary", value=False)

# Sort Option
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Sorting")
sort_by_cashback = st.sidebar.toggle("Sort by Highest Cashback Rate")

# 4. Filter Logic
try:
    filtered_df = df.copy()

    # Filter State Tracking to Reset Pagination
    current_filter_state = f"{selected_banks}_{user_salary}_{show_higher_salary}_{sort_by_cashback}"
    
    if 'last_filter_state' not in st.session_state:
        st.session_state.last_filter_state = current_filter_state
        
    if st.session_state.last_filter_state != current_filter_state:
        st.session_state.page_number = 0
        st.session_state.last_filter_state = current_filter_state

    if selected_banks:
        filtered_df = filtered_df[filtered_df['bank_name'].isin(selected_banks)]

    if user_salary > 0:
        if show_higher_salary:
            # Show cards where requirement > user_salary
            filtered_df = filtered_df[filtered_df['min_salary_numeric'] > user_salary]
        else:
            # Default: Show cards where requirement <= user_salary OR requirement is 0 (Not Mentioned)
            filtered_df = filtered_df[(filtered_df['min_salary_numeric'] <= user_salary) | (filtered_df['min_salary_numeric'] == 0)]

    if sort_by_cashback:
        if 'max_cashback_rate' in filtered_df.columns:
            filtered_df = filtered_df.sort_values(by='max_cashback_rate', ascending=False)
        else:
            st.warning("Cashback data not available for sorting.")

except Exception as e:
    st.error(f"Error filtering data: {e}")
    filtered_df = df.copy()

# 5. Rendering
# Initialize Session State for Selection
if 'selected_cards' not in st.session_state:
    st.session_state.selected_cards = []

def toggle_selection(card_id):
    """Callback to handle selection logic and sync checkbox state"""
    key = f"select_{card_id}"
    is_checked = st.session_state.get(key, False)
    
    if is_checked:
        if len(st.session_state.selected_cards) >= 3:
            # FIFO: Remove the first selected card
            removed_id = st.session_state.selected_cards.pop(0)
            # Uncheck the removed card's widget
            st.session_state[f"select_{removed_id}"] = False
            
        if card_id not in st.session_state.selected_cards:
            st.session_state.selected_cards.append(card_id)
    else:
        if card_id in st.session_state.selected_cards:
            st.session_state.selected_cards.remove(card_id)

def clear_all_selections():
    """Clears the list and unchecks all boxes"""
    st.session_state.selected_cards = []
    # Reset all checkbox widget states
    for key in list(st.session_state.keys()):
        if key.startswith("select_"):
            st.session_state[key] = False

# Comparison Dialog
@st.dialog("Compare Cards", width="large")
def show_comparison_dialog():
    # Inject specific CSS for this dialog's button
    # Dialog CSS handled by utils.load_css

    if not st.session_state.selected_cards:
        st.warning("No cards selected.")
        return

    selected_ids = st.session_state.selected_cards
    comparison_df = df[df['id'].isin(selected_ids)]
    
    if comparison_df.empty:
        st.error("Error loading selected cards.")
    else:
        # Render Comparison Table
        cols = st.columns(len(comparison_df))
        for i, (idx, row) in enumerate(comparison_df.iterrows()):
            with cols[i]:
                st.markdown(get_card_html(row), unsafe_allow_html=True)
                st.markdown("---")
                st.markdown(f"**Fee:** {row['annual_fee']}")
                st.markdown(f"**Salary:** {row['minimum_salary_requirement']}")
                st.markdown(f"**Spend:** {row['minimum_spend_requirement']}")
                st.markdown(f"**Bonus:** {row['welcome_bonus']}")

    st.markdown("---")
    if st.button("Close & Clear Selection", type="primary", use_container_width=True):
        clear_all_selections()
        st.rerun()

col_actions = st.columns([0.6, 0.2, 0.2])
with col_actions[1]:
    if st.session_state.selected_cards:
        if st.button("Clear", type="secondary", use_container_width=True):
            clear_all_selections()
            st.rerun()
with col_actions[2]:
    if st.session_state.selected_cards:
        if st.button(f"Compare ({len(st.session_state.selected_cards)})", type="primary", use_container_width=True):
            show_comparison_dialog()

# Pagination Logic
if 'page_number' not in st.session_state:
    st.session_state.page_number = 0
    
cards_per_page = 20
total_cards = len(filtered_df)
total_pages = max(1, (total_cards + cards_per_page - 1) // cards_per_page)

# Ensure page number is valid
if st.session_state.page_number >= total_pages:
    st.session_state.page_number = total_pages - 1
if st.session_state.page_number < 0:
    st.session_state.page_number = 0
    
start_idx = st.session_state.page_number * cards_per_page
end_idx = start_idx + cards_per_page

# Slice the dataframe
paginated_df = filtered_df.iloc[start_idx:end_idx]

st.subheader(f"Showing {len(filtered_df)} cards (Page {st.session_state.page_number + 1} of {total_pages})")

# Loop with Checkboxes
for idx, row in paginated_df.iterrows():
    try:
        c1, c2 = st.columns([0.85, 0.15])
        
        with c1:
            card_html = get_card_html(row)
            st.markdown(card_html, unsafe_allow_html=True)
            
        with c2:
            st.write("") 
            st.write("")
            
            is_selected = row['id'] in st.session_state.selected_cards
            st.checkbox(
                "Compare", 
                key=f"select_{row['id']}", 
                value=is_selected,
                on_change=toggle_selection,
                args=(row['id'],)
            )
            
    except Exception as e:
        st.error(f"Error rendering card {row.get('card_name', 'Unknown')}: {e}")

# Pagination Controls
if total_pages > 1:
    st.markdown("---")
    c_prev, c_info, c_next = st.columns([0.2, 0.6, 0.2])
    
    with c_prev:
        if st.session_state.page_number > 0:
            if st.button("Previous Page", use_container_width=True):
                st.session_state.page_number -= 1
                st.rerun()
                
    with c_next:
        if st.session_state.page_number < total_pages - 1:
            if st.button("Next Page", use_container_width=True):
                st.session_state.page_number += 1
                st.rerun()
