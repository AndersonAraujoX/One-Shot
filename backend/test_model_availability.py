
import google.generativeai as genai
import os
import time
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def run_model_test(model_name):
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
    run_model_test("gemini-2.5-flash")
    run_model_test("gemini-2.0-flash")
    run_model_test("gemini-flash-latest")
    
    # Test generic fallback
    run_model_test("gemini-1.5-flash-latest")
