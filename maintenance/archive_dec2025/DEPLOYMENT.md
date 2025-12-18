# Deployment Guide

## 1. Prerequisites
- A GitHub account.
- A Streamlit Cloud account (share.streamlit.io).
- Your OpenAI API Key.

## 2. Prepare Repository
1. Ensure all your code is committed and pushed to GitHub.
2. Verify `requirements.txt` contains:
   ```
   streamlit
   pandas
   openai
   httpx
   python-dotenv
   ```

## 3. Deploy to Streamlit Cloud
1. Log in to [Streamlit Cloud](https://share.streamlit.io/).
2. Click **"New app"**.
3. Select your GitHub repository, branch (e.g., `main`), and the main file path: `streamlit_app/Home.py`.
4. Click **"Deploy!"**.

## 4. Configure Secrets (Environment Variables)
The app requires an OpenAI API key to function.
1. In your deployed app's dashboard, go to **Settings** > **Secrets**.
2. Add your secrets in the TOML format:
   ```toml
   OPENAI_API_KEY = "sk-..."
   ```
3. Save the secrets. The app should automatically restart.

## 5. Verify Deployment
- Check the **Home** page to ensure the futuristic theme loads correctly.
- Check **Compare Cards** to ensure the light theme is applied and filters work.
- Check **AI Assistant** to ensure the chat works (requires the API key).

## Troubleshooting
- **Theme Issues**: If the theme looks wrong, ensure `streamlit_app/utils.py` and `streamlit_app/Home.py` are up to date.
- **Missing Dependencies**: Check the logs in Streamlit Cloud for `ModuleNotFoundError`. Add any missing packages to `requirements.txt`.
