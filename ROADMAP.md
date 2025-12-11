# Project Roadmap & Status

## ✅ What We Have Done (The "Wins")
1.  **Core Application**:
    *   **Card Comparison**: Robust side-by-side comparison with "No cards selected" bug fixed.
    *   **Real-Time Data Dashboard**: Interactive charts for Salary, Cashback, and Bank distribution (`pages/3_Real_Time_Data.py`).
    *   **Search & Filter**: Effective filtering by bank, salary, and benefits.

2.  **UI/UX Enhancements**:
    *   **"Glassmorphism" Theme**: Modern, futuristic dark mode design.
    *   **Modal Revamp**: Detailed card popup with AI summary, top features, and "Apply Now" button.
    *   **Mobile Optimization**: Improved card display for smaller screens.

3.  **Infrastructure**:
    *   **GitHub Deployment**: Codebase is clean and synced with GitHub.
    *   **Streamlit Cloud**: App is deployed and secrets are configured.
    *   **Health Checks**: Local DB, Git, and Project structure are verified healthy.

---

## 🚀 Roadmap: Upcoming Priorities

### 1. Supabase & Vector Database Integration ☁️
*   **Goal**: Migrate the backend from SQLite to **Supabase** and enable **Vector Search**.
*   **Why**:
    *   **Vector Database**: Allows for "semantic search" (e.g., searching for "travel" finds cards with "miles").
    *   **Scalability**: A proper cloud database is needed for user logins and analytics.
    *   **Live Data**: Removes the need to redeploy the app just to update card details.
*   **Action Items**:
    *   Update `maintenance/sync_to_supabase.py` to fully sync all card data.
    *   Enable `pgvector` extension on Supabase.
    *   Switch the Streamlit app to read primarily from Supabase.

### 2. User Login & Authentication 🔐
*   **Goal**: Allow users to sign up and log in.
*   **Why**:
    *   **Personalization**: Users can save their favorite cards.
    *   **Security**: Essential for any future features involving sensitive user data.
*   **Implementation**: Use Supabase Auth (built-in, secure, and integrates easily with Streamlit).

### 3. User Analytics & Statistics 📈
*   **Goal**: Track visitor numbers and user retention (repeat visits).
*   **Why**: To understand how the app is growing and whether users are coming back.
*   **Features**:
    *   **Visitor Counter**: Total distinct visitors.
    *   **Retention Metric**: How many users return after their first visit.
*   **Technical Approach**: Store visit logs in a new Supabase table (or use a lightweight analytics tool, but Supabase is preferred for keeping everything in one place).

---

## 👂 Customer Feedack / To Be Validated
*The following items are potential features based on user feedback, pending validation and design.*

1.  **Card Comparison Improvements**:
    *   Fix results not showing for some cards.
    *   Visualize comparison in a **Table View** for easier scanning.
    *   Add **"Period"** (e.g., Annual/Monthly) context to fees/benefits where applicable.
    *   Add **Grace Period** to comparison points.
    *   Allow comparison by specific criteria (not just salary), e.g., "Compare by Annual Fee".
2.  **Corporate vs. Individual Cards**:
    *   Add a high-level filter for **Individual** vs. **Corporate/SME** cards.
    *   Differentiate data points for corporate cards (Expense Tracking, Liability Waiver, etc.).
3.  **Application Links**:
    *   Add direct "Apply Now" links to the bank's mobile app or website for every card.
4.  **Search & Filtering**:
    *   Improve the "Search Cards" filter to be more intuitive (users might not know specific names like "Signature").
    *   Add "Recommended for You" or AI-driven suggestions based on user profile/needs.
5.  **Grace Period**: Ensure grace period information is displayed and comparable.

---

### ⏳ Future Considerations (The Backlog)
*   **"Smart" Card Matcher**: Wizard-style spending calculator.
*   **Admin Portal**: Web interface for editing card data.
*   **Automated Weekly Scraper**: GitHub Action for auto-updates.
