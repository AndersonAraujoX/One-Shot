
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Erro: GEMINI_API_KEY não encontrada.")
    exit(1)

genai.configure(api_key=api_key)

def test_model(model_name, label):
    print(f"\n--- Testando {label}: {model_name} ---")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Olá, isso é um teste.")
        print(f"Sucesso! Resposta: {response.text}")
        return True
    except Exception as e:
        print(f"Falha ao usar {model_name}: {e}")
        return False

# Teste 1: Texto com gemini-2.5-flash
test_model("gemini-2.5-flash", "Texto (Gemini 2.5 Flash)")

# Teste 2: Imagem com gemini-2.5-flash (se suportar image generation via generate_content?)
# Imagem geralmente é via imagen-3.0-generate-001, mas vamos testar se o user ta certo.
# Nao existe 'gemini-2.5-flash-image' listado normalmente, mas vamos tentar.
test_model("gemini-2.5-flash-image", "Modelo Imagem Sugerido")

# Listar modelos parecidos
print("\n--- Modelos Disponíveis (Filtro '2.5' ou 'flash') ---")
for m in genai.list_models():
    if 'flash' in m.name or '2.5' in m.name:
        print(f"- {m.name}: {m.supported_generation_methods}")
