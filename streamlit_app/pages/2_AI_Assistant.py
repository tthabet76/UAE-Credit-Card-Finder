import streamlit as st
import openai
import httpx
from utils import load_css
from db_utils import fetch_all_cards

load_css()

st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")

st.title("🤖 AI Credit Card Expert")
st.markdown("Ask me anything about UAE credit cards! I can help you find the best card for your lifestyle.")

# Initialize OpenAI
try:
    openai_api_key = st.secrets["openai"]["api_key"]
    openai.api_key = openai_api_key
except Exception:
    st.error("⚠️ API Keys missing! Please add them to `.streamlit/secrets.toml`.")
    st.stop()

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm your personal credit card expert. Are you looking for cashback, travel rewards, or something else?"}
    ]

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        bubble_class = "user-bubble" if message["role"] == "user" else "ai-bubble"
        st.markdown(f'<div class="{bubble_class}">{message["content"]}</div>', unsafe_allow_html=True)

# Chat Logic
# Check if we have a pre-filled query from another page
if "ai_query" in st.session_state and st.session_state.ai_query:
    initial_prompt = st.session_state.ai_query
    # Clear it so it doesn't persist on refresh
    del st.session_state.ai_query
else:
    initial_prompt = None

if prompt := st.chat_input("What kind of card are you looking for?") or initial_prompt:
    
    # Use the available input
    user_input = prompt if prompt else initial_prompt

    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(f'<div class="user-bubble">{user_input}</div>', unsafe_allow_html=True)

    # RAG Logic
    with st.spinner("Thinking..."):
        try:
            # 1. Fetch relevant cards (Local SQLite)
            df = fetch_all_cards()
            
            # Optimization: Pass ALL cards to the LLM (Context Window is large enough for ~200 cards)
            # This allows the AI to perform semantic filtering instead of our brittle keyword match.
            cards_to_context = df
            
            # Prepare context
            card_context = ""
            for index, row in cards_to_context.iterrows():
                card_context += f"""
                - {row['bank_name']} {row['card_name']} | Fee: {row['annual_fee']} | Salary: {row['minimum_salary_requirement']} | Cashback: {row['cashback_rates']} | Benefits: {row['other_key_benefits']}
                """

            # 2. Call OpenAI
            client = openai.OpenAI(
                api_key=openai_api_key,
                http_client=httpx.Client(verify=False)
            )
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"""You are a helpful UAE credit card expert. 
                    Use the following card data to answer the user's question. 
                    If the answer isn't in the data, say so. 
                    Be concise and format your answer nicely with markdown.
                    
                    Data:
                    {card_context}"""},
                    {"role": "user", "content": user_input}
                ]
            )
            
            reply = completion.choices[0].message.content
            
            # Add assistant response to history
            st.session_state.messages.append({"role": "assistant", "content": reply})
            with st.chat_message("assistant"):
                st.markdown(f'<div class="ai-bubble">{reply}</div>', unsafe_allow_html=True)
                
        except Exception as e:
            import traceback
            st.error(f"An error occurred: {e}")
            st.code(traceback.format_exc())
