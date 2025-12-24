
import google.generativeai as genai
import os
import time
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def test_model(model_name):
    print(f"\nTesting model: {model_name}")
    try:
        model = genai.GenerativeModel(model_name)
        start = time.time()
        # Simple prompt
        response = model.generate_content("Hello, reply with 'OK'.")
        duration = time.time() - start
        print(f"Success! Time: {duration:.2f}s")
        print(f"Response: {response.text}")
        return True
    except Exception as e:
        print(f"Failed: {e}")
        return False

if __name__ == "__main__":
    # Test specific requested models
    test_model("gemini-2.5-flash")
    test_model("gemini-2.0-flash")
    test_model("gemini-flash-latest")
    
    # Test generic fallback
    test_model("gemini-1.5-flash-latest")
