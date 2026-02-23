
import os
import google.generativeai as genai
import pytest

from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Pula todos os testes neste arquivo se a chave não estiver configurada no ambiente
pytestmark = pytest.mark.skipif(
    not api_key or len(api_key.strip()) == 0,
    reason="GEMINI_API_KEY não configurada no ambiente (ex: CI pipeline)."
)

if api_key:
    genai.configure(api_key=api_key)

def run_model_test(model_name, label):
    print(f"\n--- Testando {label}: {model_name} ---")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Olá, isso é um teste.")
        print(f"Sucesso! Resposta: {response.text}")
        return True
    except Exception as e:
        print(f"Falha ao usar {model_name}: {e}")
        return False

def test_run_models():
    # Teste 1: Texto com gemini-2.5-flash
    run_model_test("gemini-2.5-flash", "Texto (Gemini 2.5 Flash)")

    # Teste 2: Imagem com gemini-2.5-flash
    run_model_test("gemini-2.5-flash-image", "Modelo Imagem Sugerido")

    # Listar modelos parecidos
    print("\n--- Modelos Disponíveis (Filtro '2.5' ou 'flash') ---")
    for m in genai.list_models():
        if 'flash' in m.name or '2.5' in m.name:
            print(f"- {m.name}: {m.supported_generation_methods}")
