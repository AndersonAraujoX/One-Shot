# backend/tests/test_chat.py
import pytest
import json
from unittest.mock import patch, MagicMock
from app.chat import gerar_aventura_batch, COMMAND_PROMPTS

@patch('app.chat.iniciar_chat')
@patch('app.chat.enviar_mensagem')
def test_gerar_aventura_batch_sucesso(mock_enviar, mock_iniciar):
    mock_chat = MagicMock()
    mock_iniciar.return_value = mock_chat

    def mock_enviar_side_effect(chat, prompt):
        if '"contexto":' in prompt:
            return '{"contexto": {"titulo": "Título Teste", "sinopse": "Sinopse Teste"}, "ganchos": ["1", "2"]}'
        if '"personagens": Lista' in prompt:
            return '{"personagens": [{"nome": "Herói 1", "raca": "Elfo"}]}'
        if 'Gere "personagens_chave" e "locais_importantes"' in prompt:
            return '{"personagens_chave": [{"nome": "NPC Teste", "prompt_imagem": "img"}], "locais_importantes": [{"nome": "Local Teste"}]}'
        if "Gere 'cenario' e 'desafios'" in prompt:
            return '{"cenario": [{"nome": "Taverna"}], "desafios": [{"nome": "Luta"}]}'
        if "Gere o 'ato1'" in prompt:
            return '{"ato1": {"titulo": "Ato 1zinho"}}'
        if "Gere o 'ato2'" in prompt:
            return '{"ato2": {"titulo": "Ato 2zinho"}}'
        if "Gere o 'ato3'" in prompt:
            return '{"ato3": {"titulo": "Ato 3zinho"}}'
        if "Gere o 'ato4'" in prompt:
            return '{"ato4": {"titulo": "Ato 4zinho"}}'
        if "Gere o 'ato5'" in prompt:
            return '{"ato5": {"titulo": "Ato 5zinho"}, "resumo": "Fim do jogo"}'
        return "{}"

    mock_enviar.side_effect = mock_enviar_side_effect

    # Chama a função principal de teste
    adventure_data = gerar_aventura_batch(gerar_personagens=True, num_jogadores=4, nivel_tier="1")

    # Verifica chaves básicas retornadas pelo chunk JSON
    assert "titulo" in adventure_data
    assert adventure_data["titulo"] == "Título Teste"
    assert "personagens" in adventure_data
    assert "personagens_chave" in adventure_data
    assert "cenario" in adventure_data
    assert "ato1" in adventure_data
    assert "resumo" in adventure_data

@patch('app.chat.iniciar_chat')
@patch('app.chat.enviar_mensagem')
def test_gerar_aventura_batch_json_invalido_fallback(mock_enviar, mock_iniciar):
    mock_chat = MagicMock()
    mock_iniciar.return_value = mock_chat

    # Simula o modelo retornando puro texto para o mundo (fallback)
    def mock_enviar_side_effect(chat, prompt):
        if 'Gere "personagens_chave"' in prompt:
            return "Aqui está uma lista de NPCs e locais em texto longo sem JSON..."
        
        # Para o resto, retorna JSON vazio apenas para não quebrar iteradores
        return "{}"

    mock_enviar.side_effect = mock_enviar_side_effect

    adventure_data = gerar_aventura_batch()

    # O fallback do Mundo salva tudo em "personagens_chave" (conforme chat.py:374)
    assert "personagens_chave" in adventure_data
    assert "texto longo sem JSON" in adventure_data["personagens_chave"]
