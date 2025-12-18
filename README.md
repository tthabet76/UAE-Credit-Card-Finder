# 💳 UAE Credit Card Finder (Smart Spending)

**The Future of Smart Spending Using AI.**  
Stop guessing. Compare interest rates, rewards, and fees side-by-side with our interactive tools.

---

## 📖 Project Overview & Story
Finding the right credit card in the UAE is difficult. Banks have complex fee structures, hidden salary requirements, and confusing reward points. 

**This project solves that problem.** 
It is an intelligent ecosystem that:
1.  **Crawls** bank websites to find every card available.
2.  **Reads** the fine print using AI (LLMs) to extract structured data (Fees, Cashback, Miles).
3.  **Visualizes** this data in a beautiful, dark-mode web application for users.

It is split into two distinct parts: a **Local Backend** (for intelligence gathering) and a **Cloud Frontend** (for user interaction).

---

## 🏗️ System Architecture

### 1. The Backend (Local Intelligence)
*   **Location**: Your local machine (`maintenance/` folder).
*   **Role**: The Factory. It does the heavy lifting.
*   **Technology**: Python, Selenium (Web Browser Automation), Google Gemini AI, SQLite.
*   **Why Local?**: Bank scraping requires a full browser engine and heavy processing power that is expensive or blocked in the cloud.

### 2. The Frontend (User Experience)
*   **Location**: Streamlit Cloud (`streamlit_app/` folder).
*   **Role**: The Showroom. It displays the finished product.
*   **Technology**: Streamlit, Pandas, CSS/HTML.
*   **Data Source**: Reads from **Supabase** (a cloud database) which is synced from your local machine.

---

## 🤖 The "Agents" (Backend Workers)
The backend is powered by specialized Python scripts we call "Agents". Each has a specific job:

### 🕵️‍♂️ Agent 1: The Bank Explorer (`update_banks.py`)
*   **Mission**: Find new cards.
*   **Action**: Visits the "All Cards" page of major UAE banks (ADCB, FAB, etc.). It looks for links to specific card pages.
*   **Output**: Populates the `card_inventory` table with URLs.

### 📝 Agent 2: The Card Analyst (`update_cards.py`)
*   **Mission**: Read the fine print.
*   **Action**: Visits every URL found by Agent 1. It takes the text of the page and sends it to an LLM (AI). The AI reads it and extracts: Annual Fees, Minimum Salary, Cashback Rates, and Travel Benefits.
*   **Output**: Populates the `credit_cards_details` table.
*   *Note: Using `update_cards_rest.py` (REST API version) is planned for better SSL handling.*

### 🎨 Agent 3: The Art curator (`update_images.py`)
*   **Mission**: Make it look good.
*   **Action**: Visits the card pages again specifically to find the high-quality card image. It downloads, crops, and optimizes links to these images.
*   **Output**: Populates the `card_images` table.

### 🌉 The Bridge: Sync (`sync_to_supabase.py`)
*   **Mission**: Deploy.
*   **Action**: Takes the data from your local `credit_card_data.db` and pushes it to the generic Cloud Database (Supabase). This makes the data visible to the public Frontend.

---

## 📂 Project File Guide (Root Directory)

| File | Importance | Description |
| :--- | :--- | :--- |
| **`README.md`** | ⭐⭐⭐⭐⭐ | **You are reading it.** The manual for the project. |
| **`CONTINUITY.md`** | ⭐⭐⭐⭐⭐ | **Critical.** Contains the "Brain" of the project—history of prompts, decisions, and logic. Use this to resume work after a break or on a new PC. |
| **`ROADMAP.md`** | ⭐⭐⭐ | The Project Plan. Tracks what is done, what is pending, and future ideas. |
| **`requirements.txt`** | ⭐⭐⭐⭐⭐ | The Recipe. Lists all software libraries (like `selenium`, `streamlit`) needed to make this run. |
| **`credit_card_data.db`** | ⭐⭐⭐⭐⭐ | The Vault. Your local SQLite database containing all the hard-earned data. |
| **`.gitignore`** | ⭐⭐⭐⭐ | The Security Guard. Tells Git which files to **IGNORE** (like passwords or local test pages) so they don't leak to the internet. |

---

## 🚀 How to Run (Quick Start)

### Prerequisites
*   Python 3.10+ installed.
*   Chrome Browser installed.

### 1. Installation
Install the required libraries:
```bash
pip install -r requirements.txt
```

### 2. Running the Frontend (Locally)
To see the website on your computer:
```bash
streamlit run streamlit_app/Home.py
```

### 3. Running an Agent (Backend)
To update bank data (for example):
```bash
python maintenance/update_banks.py
```

---
**Maintained by**: Tarek Thabet
**Last Updated**: Dec 2025
