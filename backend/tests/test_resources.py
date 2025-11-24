# backend/tests/test_resources.py
import pytest
import json
import os

# Teste para validar a sintaxe do prompts.json
def test_validade_json_prompts():
    try:
        with open("backend/app/prompts.json", 'r', encoding='utf-8') as f:
            json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        pytest.fail(f"O arquivo prompts.json é inválido ou não foi encontrado: {e}")

# Teste para verificar a presença da chave de API
def test_presenca_chave_api():
    # Este teste assume que as variáveis de ambiente são carregadas antes da execução
    # Em um cenário de CI/CD, esta variável seria configurada no ambiente de teste
    api_key = os.getenv("GEMINI_API_KEY")
    assert api_key is not None, "A variável de ambiente GEMINI_API_KEY não está configurada."
    assert len(api_key.strip()) > 0, "A variável de ambiente GEMINI_API_KEY está vazia."

# Teste para garantir que o template de prompt contém os placeholders esperados
def test_placeholders_no_prompt():
    with open("backend/app/prompts.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    template = data.get("PROMPT_TEMPLATE")
    assert template is not None, "A chave 'PROMPT_TEMPLATE' não foi encontrada no prompts.json."
    
    placeholders_esperados = [
        "{sistema}",
        "{genero_estilo}",
        "{num_jogadores}",
        "{nivel_tier}",
        "{tempo_estimado}",
        "{tom_adicional}"
    ]
    
    for placeholder in placeholders_esperados:
        assert placeholder in template, f"O placeholder '{placeholder}' está faltando no template do prompt."
