"""
Clears the Streamlit cache. Useful if the web app isn"t showing the latest data.
"""
import streamlit as st

if __name__ == "__main__":
    try:
        st.cache_data.clear()
        st.cache_resource.clear()
        print("Cache cleared successfully.")
    except Exception as e:
        print(f"Error clearing cache: {e}")
