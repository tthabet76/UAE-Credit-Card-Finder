# Project Migration & Handover Guide

This document is your "Emergency Kit". It details exactly how to move this project—and its "brain" (the AI context)—to another computer, even if you have **no internet connection**.

---

## 🚨 1. The "Grab Bag" (Copy These IMMEDIATELY)

If you are losing access to this PC, copy these **3 Critical Folders** to a USB drive or external hard drive.

### Folder 1: The Project Code
> **Path**: `C:\Users\cdf846\Documents\personal\UAE-Credit-Card-Finder`
>
> **Why**: Contains the application logic, database, and local tools.
>
> **Critical Check**: Ensure you include `secrets.toml` inside `.streamlit/` (it is usually hidden/ignored by git).

### Folder 2: The "Brain" (AI Context)
> **Path**: `C:\Users\cdf846\.gemini`
>
> **Why**: This contains the "Anti Gravity" agent's memory, artifacts (like this guide), and task history. Without this, the AI on the new PC will be "amnesiac" and won't know the project history.

### Folder 3: Offline Dependencies (Optional but Recommended)
If the new PC has **NO Internet**, you must download the libraries now.
1. Open Terminal in the project folder.
2. Run:
   ```powershell
   mkdir offline_packages
   pip download -r requirements.txt -d ./offline_packages
   pip download -r streamlit_app/requirements.txt -d ./offline_packages
   ```
3. Copy the `offline_packages` folder to your USB drive.

---

## 🛠️ 2. Restoration Guide (On the New PC)

Follow these steps to set up the project on a new machine.

### Step A: Install Prerequisites
1. **Python**: Install Python 3.10+ (Installer included on USB if you downloaded it, otherwise get from python.org).
   - **IMPORTANT**: Check "Add Python to PATH" during installation.
2. **VS Code** (Optional): Recommended editor.

### Step B: Restore the "Brain" 🧠
1. Navigate to `C:\Users\<NewUser>\`.
2. Create a folder named `.gemini` if it doesn't exist.
3. Copy the contents of your backed-up `.gemini` folder into this new location.
   - Final path should look like: `C:\Users\<NewUser>\.gemini\antigravity\...`

### Step C: Restore the Project
1. Copy the `UAE-Credit-Card-Finder` folder to your Documents.
2. **Verify Secrets**:
   - Go to `UAE-Credit-Card-Finder\streamlit_app\.streamlit\`
   - Ensure `secrets.toml` exists. If not, create it and paste your API keys:
     ```toml
     [supabase]
     url = "..."
     key = "..."
     
     [openai]
     api_key = "sk-..."
     ```

### Step D: Install Dependencies
Open a terminal in the project folder (`UAE-Credit-Card-Finder`).

**Option 1: With Internet**
```powershell
pip install -r requirements.txt
pip install -r streamlit_app/requirements.txt
```

**Option 2: NO Internet (Offline)**
```powershell
pip install --no-index --find-links=./offline_packages -r requirements.txt
pip install --no-index --find-links=./offline_packages -r streamlit_app/requirements.txt
```

### Step E: Run the App 🚀
```powershell
streamlit run streamlit_app/Home.py
```

---

## 📝 Handover Notes for New Developers

If you are giving this to a new developer:

1. **The Database**: The project uses a local SQLite database (`credit_card_data.db`). It is self-contained.
2. **The "Brain"**: Explain that the `.gemini` folder contains the project's architectural history. If they install the Anti Gravity agent, it will read this folder and "remember" everything.
3. **Key Files**:
   - `streamlit_app/Home.py`: The main entry point.
   - `maintenance/`: Scripts for scraping and updating data.
   - `secrets.toml`: **NEVER share this publicly.** It contains your credit card (API billing) keys.

---

## ❓ Troubleshooting

- **"Module not found"**: You missed a requirement. Run the pip install commands again.
- **"OpenAI API Error"**: Check `secrets.toml`. The key might be missing or expired.
- **"Database locked"**: Ensure no other script (like a maintenance script) is writing to the DB while the app is running.
