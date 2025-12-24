import google.generativeai as genai
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env no diretório atual
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("A variável de ambiente GEMINI_API_KEY não foi encontrada no arquivo .env")
else:
    try:
        genai.configure(api_key=api_key)
        print("Modelos disponíveis para sua chave de API que suportam 'generateContent':")
        # Itera sobre os modelos e verifica se 'generateContent' está nos métodos suportados
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f'- {m.name}')
    except Exception as e:
        print(f"Ocorreu um erro ao listar os modelos: {e}")
