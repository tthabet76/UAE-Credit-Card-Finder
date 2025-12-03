# Maintenance & Utilities

This folder contains scripts for maintaining the data, debugging the application, and managing the database.

## 📂 Core Maintenance Scripts
These are the most important scripts for keeping the app updated.

| File | Description |
| :--- | :--- |
| **`update_banks.py`** | **[CRITICAL]** The main "Spider". It visits bank websites to discover new credit cards and adds them to the database. Uses parallel processing for speed. |
| **`update_cards.py`** | **[CRITICAL]** The main "Scraper". It visits the specific page of each card to extract fees, interest rates, and benefits. |
| **`update_banks_sequential.py`** | A backup version of `update_banks.py` that runs one browser at a time (slower but safer if parallel fails). |
| **`sync_to_supabase.py`** | Syncs the local `credit_card_data.db` to a remote Supabase database (if you are using one for production). |

## 🛠️ Debugging & Testing Tools
Use these to check if things are working correctly.

| File | Description |
| :--- | :--- |
| **`check_card.py`** | Prints all details stored in the database for a specific card (e.g., RAKBANK World). |
| **`check_rakbank_status.py`** | Quickly checks how many RAKBANK cards are active and lists them. |
| **`check_suspicious_cards.py`** | Scans the database for cards with names like "Not Found" or "Not Mentioned" to identify scraping errors. |
| **`test_api_quota.py`** | Sends a simple "Hello" to Google Gemini to check if your API key is valid and working. |
| **`test_rakbank_discovery.py`** | Runs a test of the discovery logic specifically for RAKBANK without updating the real database. |
| **`test_single_card.py`** | Runs the full scraping process on a *single* card to test if the scraper is working, without waiting for all cards. |
| **`list_models.py`** | Lists all available Google Gemini AI models accessible with your API key. |
| **`clear_cache.py`** | Clears the Streamlit cache. Useful if the web app isn't showing the latest data. |

## 🗄️ Database & Migrations
Scripts that modify the database structure or clean up data.

| File | Description |
| :--- | :--- |
| **`credit_card_data.db`** | The SQLite database file where all card information is stored. |
| **`add_cashback_columns.py`** | **[Run Once]** Adds columns for `max_cashback_rate`, `is_uncapped`, etc., to the database. |
| **`add_salary_column.py`** | **[Run Once]** Adds the `salary` column to the database. |
| **`fix_bank_names.py`** | Normalizes bank names (e.g., changing "Rakbank" to "RAKBANK") to ensure consistency. |
| **`run_targeted_update.py`** | Allows you to force an update for a specific list of URLs or banks. |
