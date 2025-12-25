
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Erro: GEMINI_API_KEY não encontrada.")
    exit(1)

genai.configure(api_key=api_key)

print("--- Start Model List ---")
for m in genai.list_models():
    print(f"Model: {m.name}")
    print(f"  Display Name: {m.display_name}")
    print(f"  Methods: {m.supported_generation_methods}")
print("--- End Model List ---")
