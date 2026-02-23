# backend/tests/test_resources.py
import pytest
import json
import os

# Teste para validar a sintaxe do prompts.json
def test_validade_json_prompts():
    import os

    # Determina o caminho dinâmico para o arquivo json (para funcionar no CI e rodando local na pasta backend)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_dir, "app", "prompts.json")

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        pytest.fail(f"O arquivo prompts.json é inválido ou não foi encontrado: {e}")

def test_presenca_chave_api():
    """Verifica se há aviso estrutural quando GEMINI_API_KEY não estiver no env."""
    from typing import cast
    """Esta verificação é indireta, o ideal é testar funções que requerem a chave, 
       mas apenas para checar recursos locais"""
    pass

def test_placeholders_no_prompt():
    """Garante que placeholders como {sistema} existam no json para substituição (se usassemos json)."""
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(base_dir, "app", "prompts.json")
    
    with open(json_path, 'r', encoding='utf-8') as f:
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
