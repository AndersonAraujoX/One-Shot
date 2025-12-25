
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found.")
    exit(1)

genai.configure(api_key=api_key)

def test_text():
    print("--- Testing gemini-2.5-flash (Text) ---")
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content("Hello! Are you functional? Reply with a short 'Yes'.")
        print(f"Success! Response: {response.text}")
    except Exception as e:
        print(f"Failed: {e}")

def test_image_model():
    print("\n--- Testing gemini-2.5-flash-image ---")
    try:
        # User believes this model exists. Let's see if we can instantiate it.
        # If it's an image GENERATION model, generate_content might behave differently or fail if it expects properties.
        # But regular Gemini models use generate_content.
        model = genai.GenerativeModel("gemini-2.5-flash-image")
        
        # Attempt 1: Simple text prompt to see if it responds (maybe it's multimodal)
        response = model.generate_content("Describe a cat.")
        print(f"Success (Text Prompt): {response.text}")
        
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test_text()
    test_image_model()
