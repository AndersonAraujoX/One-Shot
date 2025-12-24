
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def test_imagen_rest():
    print("\n--- Testing Imagen 3 via REST API ---")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not set.")
        return

    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:predict?key={api_key}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "instances": [
            {
                "prompt": "A cute robot cat holding a sword"
            }
        ],
        "parameters": {
            "sampleCount": 1
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(response.text)
        
        if response.status_code == 200:
             # Process response if successful
             pass

    except Exception as e:
        print(f"REST Call Failed: {e}")

if __name__ == "__main__":
    test_imagen_rest()
