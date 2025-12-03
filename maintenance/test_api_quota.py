"""
Sends a simple "Hello" to Google Gemini to check if your API key is valid and working.
"""
import google.generativeai as genai
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv(override=True)
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY not found in .env")
    exit(1)

genai.configure(api_key=api_key)

# Use the standard flash model
model = genai.GenerativeModel('models/gemini-flash-latest')

print(f"Testing API Key: {api_key[:10]}...")
print("Sending 1 simple request...")

try:
    start_time = time.time()
    response = model.generate_content("Hello, are you working?")
    end_time = time.time()
    
    print("\n--- SUCCESS ---")
    print(f"Response: {response.text}")
    print(f"Time taken: {end_time - start_time:.2f}s")
    
except Exception as e:
    print("\n--- FAILURE ---")
    print(f"Error: {e}")
