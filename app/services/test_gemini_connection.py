import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

def test_gemini_connection():
    if not GEMINI_API_KEY:
        print("❌ Error: GEMINI_API_KEY is not set in the environment.")
        return

    headers = {
        "Content-Type": "application/json"
    }

    prompt = "Say hello from Gemini!"
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers=headers,
            json=data,
            timeout=10
        )

        if response.status_code == 200:
            reply = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            print("✅ Gemini API is connected successfully!")
            print("Response:", reply)
        else:
            print(f"❌ Gemini API Error: {response.status_code}")
            print("Details:", response.text)

    except requests.exceptions.RequestException as e:
        print("❌ Request failed:", e)

if __name__ == "__main__":
    test_gemini_connection()
