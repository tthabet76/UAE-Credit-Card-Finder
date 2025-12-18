import requests
import os
import toml
# Disable warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load Key
secrets_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'streamlit_app', '.streamlit', 'secrets.toml'))
LLM_API_KEY = None
if os.path.exists(secrets_path):
    data = toml.load(secrets_path)
    if "gemini" in data:
        LLM_API_KEY = data["gemini"]["api_key"]

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={LLM_API_KEY}"
response = requests.get(url, verify=False)

if response.status_code == 200:
    print("--- AVAILABLE MODELS ---")
    data = response.json()
    for model in data.get('models', []):
        if 'generateContent' in model.get('supportedGenerationMethods', []):
            print(f"Name: {model['name']}")
else:
    print(f"Error: {response.text}")
