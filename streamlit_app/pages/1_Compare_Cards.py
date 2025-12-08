import streamlit as st
import pandas as pd
from utils import load_css, get_card_html
from db_utils import fetch_all_cards

# 1. Setup
load_css()
st.title("Compare Credit Cards 🚀")

# 1.1 Query Parameter Logic (Triggered by Floating Bar)
if "action" in st.query_params:
    action = st.query_params["action"]
    if action == "compare":
        st.query_params.clear()
        # We need to defer the dialog show until after the app runs, 
        # but since st.dialog is a decorator, we just set a flag or call it if possible.
        # However, calling it directly here might be too early if data isn't loaded.
        # Better approach: Set a session state flag.
        st.session_state.show_comparison = True
    elif action == "clear":
        st.query_params.clear()
        st.session_state.selected_cards = []
        st.session_state.show_comparison = False
        st.rerun()

if st.session_state.get("show_comparison", False):
    # We need to define the dialog function first, but it's defined later.
    # So we will handle the actual showing AFTER the function definition.
    pass

# 2. Data Fetching
@st.cache_data(ttl=60)
def get_cards():
    return fetch_all_cards()

with st.spinner("Loading cards..."):
    try:
        df = get_cards()
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        st.stop()

# Clean bank names to ensure consistent filtering
if not df.empty and 'bank_name' in df.columns:
    df['bank_name'] = df['bank_name'].astype(str).str.strip()

if df.empty:
    st.warning("No cards found.")
    st.stop()

# 3. Filters
st.sidebar.header("Filters")

# Keyword Search
search_term = st.sidebar.text_input("🔍 Search Cards", placeholder="e.g. Platinum, Cashback...").strip().lower()
st.sidebar.markdown("---")

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

# Callback to sync sidebar checkbox with session state list
def toggle_sidebar_bank(bank_name):
    key = f"chk_{bank_name}"
    is_checked = st.session_state.get(key, False)
    if is_checked:
        if bank_name not in st.session_state.selected_banks:
            st.session_state.selected_banks.append(bank_name)
    else:
        if bank_name in st.session_state.selected_banks:
            st.session_state.selected_banks.remove(bank_name)

# 1. Render Top 5 Checkboxes
for bank in top_banks:
    is_checked = bank in st.session_state.selected_banks
    st.sidebar.checkbox(
        bank, 
        value=is_checked, 
        key=f"chk_{bank}", 
        on_change=toggle_sidebar_bank, 
        args=(bank,)
    )

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

if st.sidebar.button("Clear Filters 🧹"):
    st.session_state.selected_banks = []
    st.rerun()

# Use the session state for filtering
selected_banks = st.session_state.selected_banks

st.sidebar.markdown("---")
st.sidebar.subheader("💰 Salary Requirement")

# Salary Filter
if 'salary_input' not in st.session_state:
    st.session_state.salary_input = 0

def decrease_salary():
    st.session_state.salary_input = max(0, st.session_state.salary_input - 1000)

def increase_salary():
    st.session_state.salary_input += 1000

col_minus, col_input, col_plus = st.sidebar.columns([1, 2, 1])

with col_minus:
    st.button("➖", key="btn_minus", on_click=decrease_salary, use_container_width=True)

with col_input:
    # Use the same key 'salary_input' so changes to state reflect in widget and vice versa
    st.number_input("Monthly Salary (AED)", min_value=0, step=1000, key="salary_input", label_visibility="collapsed")

with col_plus:
    st.button("➕", key="btn_plus", on_click=increase_salary, use_container_width=True)

# Use the session state value for filtering
user_salary = st.session_state.salary_input
show_higher_salary = st.sidebar.checkbox("Show cards requiring HIGHER salary", value=False)

# Sort Option
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Sorting")
sort_option = st.sidebar.radio(
    "Sort Cards By:",
    ["Default", "Highest Cashback", "Best Travel Points", "Lowest Salary"],
    index=0
)

# 4. Filter Logic
try:
    filtered_df = df.copy()

    # Filter State Tracking to Reset Pagination
    current_filter_state = f"{selected_banks}_{user_salary}_{show_higher_salary}_{sort_option}"
    
    if 'last_filter_state' not in st.session_state:
        st.session_state.last_filter_state = current_filter_state
        
    if st.session_state.last_filter_state != current_filter_state:
        st.session_state.page_number = 0
        st.session_state.last_filter_state = current_filter_state

    if selected_banks:
        filtered_df = filtered_df[filtered_df['bank_name'].isin(selected_banks)]

    if search_term:
        filtered_df = filtered_df[filtered_df['card_name'].str.lower().str.contains(search_term, na=False)]

    if user_salary > 0:
        if show_higher_salary:
            # Show cards where requirement > user_salary
            filtered_df = filtered_df[filtered_df['min_salary_numeric'] > user_salary]
        else:
            # Default: Show cards where requirement <= user_salary OR requirement is 0 (Not Mentioned)
            filtered_df = filtered_df[(filtered_df['min_salary_numeric'] <= user_salary) | (filtered_df['min_salary_numeric'] == 0)]

    # Sorting Logic
    if sort_option == "Highest Cashback":
        if 'max_cashback_rate' in filtered_df.columns:
            filtered_df = filtered_df.sort_values(by='max_cashback_rate', ascending=False)
        else:
            st.warning("Cashback data not available for sorting.")
            
    elif sort_option == "Lowest Salary":
        # Sort by salary ascending (0/Not Mentioned at bottom ideally, but 0 is usually lowest)
        # To put 0 at bottom, we can replace 0 with infinity for sorting
        filtered_df['sort_salary'] = filtered_df['min_salary_numeric'].replace(0, 999999)
        filtered_df = filtered_df.sort_values(by='sort_salary', ascending=True)
        
    elif sort_option == "Best Travel Points":
        # Sort by presence of travel points data
        # Create a flag: 1 if has data, 0 if None/"Not Mentioned"
        def has_travel_data(val):
            if not val: return 0
            s = str(val).strip().lower()
            if s in ["not mentioned", "none", "nan", "", "n/a"]: return 0
            return 1
            
        filtered_df['has_travel'] = filtered_df['travel_points_summary'].apply(has_travel_data)
        # Sort by flag descending (has data first)
        filtered_df = filtered_df.sort_values(by='has_travel', ascending=False)

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
        # Helper to format "Not Mentioned" as "---"
        def fmt(val):
            if val is None:
                return "---"
            s = str(val).strip()
            if s in ["Not Mentioned", "None", "nan", "", "N/A"]:
                return "---"
            return s

        for i, (idx, row) in enumerate(comparison_df.iterrows()):
            with cols[i]:
                st.markdown(get_card_html(row), unsafe_allow_html=True)
                st.markdown("---")
                st.markdown(f"**Fee:** {fmt(row['annual_fee'])}")
                st.markdown(f"**Salary:** {fmt(row['minimum_salary_requirement'])}")
                st.markdown(f"**Spend:** {fmt(row.get('minimum_spend'))}")
                st.markdown(f"**Cashback:** {fmt(row.get('cashback_summary'))}")
                st.markdown(f"**Points:** {fmt(row.get('travel_points_summary'))}")
                st.markdown(f"**Dining:** {fmt(row.get('hotel_dining_offers'))}")
                st.markdown(f"**Lounge:** {fmt(row.get('airport_lounge_access'))}")
                st.markdown(f"**Foreign Fee:** {fmt(row.get('foreign_currency_fee'))}")
                st.markdown(f"**Bonus:** {fmt(row['welcome_bonus'])}")

    st.markdown("---")
    if st.button("Close & Clear Selection", type="primary", use_container_width=True):
        clear_all_selections()
        st.rerun()

# Trigger Dialog if flag is set
if st.session_state.get("show_comparison", False):
    show_comparison_dialog()
    # Reset flag after showing? No, the dialog handles its own state usually.
    # But for st.dialog, it's a modal.
    st.session_state.show_comparison = False

# --- FLOATING ACTION BAR ---
if st.session_state.selected_cards:
    count = len(st.session_state.selected_cards)
    
    # CSS for Floating Bar
    st.markdown("""
    <style>
        .floating-bar {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(15, 23, 42, 0.95); /* Dark Slate */
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            padding: 12px 24px;
            border-radius: 50px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.4);
            display: flex;
            align-items: center;
            gap: 20px;
            z-index: 999999;
            min-width: 320px;
            justify-content: space-between;
            animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }
        
        @keyframes slideUp {
            from { transform: translate(-50%, 100%); opacity: 0; }
            to { transform: translate(-50%, 0); opacity: 1; }
        }

        .floating-text {
            color: #f8fafc;
            font-weight: 600;
            font-size: 1rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .floating-badge {
            background: rgba(255,255,255,0.1);
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.85rem;
            color: #94a3b8;
        }

        .floating-btn-primary {
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            color: white !important;
            padding: 10px 24px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 700;
            font-size: 0.95rem;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
            transition: all 0.2s ease;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .floating-btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(59, 130, 246, 0.5);
            color: white !important;
        }
        
        .floating-btn-secondary {
            color: #94a3b8 !important;
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 500;
            padding: 8px 12px;
            border-radius: 8px;
            transition: all 0.2s;
        }
        
        .floating-btn-secondary:hover {
            color: #f1f5f9 !important;
            background: rgba(255,255,255,0.05);
        }
    </style>
    
    <div class="floating-bar">
        <div class="floating-text">
            <span>Selected</span>
            <span class="floating-badge">{count}</span>
        </div>
        <div style="display: flex; align-items: center; gap: 10px;">
            <a href="?action=clear" target="_self" class="floating-btn-secondary">Clear</a>
            <a href="?action=compare" target="_self" class="floating-btn-primary">Compare Now 🚀</a>
        </div>
    </div>
    """.replace("{count}", str(count)), unsafe_allow_html=True)

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
