import os
from dotenv import load_dotenv

# Try loading from .env
load_dotenv()

def check_key():
    key = os.getenv("OPENAI_API_KEY")
    if key:
        print("OPENAI_API_KEY found.")
        # Print first few chars to verify (safe)
        print(f"Key starts with: {key[:7]}...")
        return True
    else:
        print("OPENAI_API_KEY NOT found in environment variables.")
        return False

if __name__ == "__main__":
    check_key()
