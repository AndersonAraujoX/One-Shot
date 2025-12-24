# backend/tests/test_chat.py
import pytest
from unittest.mock import patch, MagicMock
from app.chat import gerar_aventura_batch, COMMAND_PROMPTS

@patch('app.chat.iniciar_chat')
@patch('app.chat.enviar_mensagem')
def test_gerar_aventura_batch_executa_comandos_ordenados(mock_enviar, mock_iniciar):
    # Configura o mock para o chat
    mock_chat = MagicMock()
    mock_iniciar.return_value = mock_chat

    # Define um side_effect para o mock de enviar_mensagem
    def mock_enviar_side_effect(chat, prompt):
        if COMMAND_PROMPTS["contexto"]["prompt"] in prompt:
            return '{"titulo": "Título Teste", "sinopse": "Sinopse Teste"}'
        if COMMAND_PROMPTS["personagens_chave"]["prompt"] in prompt:
            return '[{"nome": "NPC Teste", "aparencia": "Aparência Teste", "url_imagem": ""}]'
        if COMMAND_PROMPTS["locais_importantes"]["prompt"] in prompt:
            return '[{"nome": "Local Teste", "atmosfera": "Atmosfera Teste", "url_imagem": ""}]'
        return "Conteúdo gerado"

    mock_enviar.side_effect = mock_enviar_side_effect

    # Chama a função
    adventure_data = gerar_aventura_batch(gerar_personagens=True, sistema="D&D 5e", num_jogadores=4, nivel_tier="1")

    # Verifica se os comandos foram chamados na ordem correta
    comandos_esperados = sorted(
        [cmd for cmd, meta in COMMAND_PROMPTS.items() if meta.get("batch_order")],
        key=lambda cmd: COMMAND_PROMPTS[cmd]["batch_order"]
    )
    
    assert mock_enviar.call_count == len(comandos_esperados)
    
    # Verifica as chaves no dicionário retornado
    assert "titulo" in adventure_data
    assert "sinopse" in adventure_data
    assert "personagens_chave" in adventure_data
    assert "locais_importantes" in adventure_data
    assert adventure_data["titulo"] == "Título Teste"
    assert len(adventure_data["personagens_chave"]) == 1
    assert len(adventure_data["locais_importantes"]) == 1

@patch('app.chat.iniciar_chat')
@patch('app.chat.enviar_mensagem')
def test_gerar_aventura_batch_pula_personagens(mock_enviar, mock_iniciar):
    mock_iniciar.return_value = MagicMock()
    mock_enviar.return_value = "Conteúdo"

    # Chama a função sem a flag gerar_personagens
    adventure_data = gerar_aventura_batch(gerar_personagens=False)

    # Verifica que 'personagens' não está nos dados retornados
    assert "personagens" not in adventure_data
    
    # Verifica que o número de chamadas é um a menos que o total de batch commands
    total_batch_commands = sum(1 for meta in COMMAND_PROMPTS.values() if "batch_order" in meta)
    assert mock_enviar.call_count == total_batch_commands - 1

@patch('app.chat.iniciar_chat')
@patch('app.chat.enviar_mensagem')
def test_gerar_aventura_batch_formata_prompt_corretamente(mock_enviar, mock_iniciar):
    mock_iniciar.return_value = MagicMock()
    mock_enviar.return_value = "Conteúdo"

    # Dados para formatação
    kwargs = {
        "num_jogadores": 5,
        "sistema": "Pathfinder",
        "nivel_tier": "Nível 10",
        "gerar_personagens": True
    }

    gerar_aventura_batch(**kwargs)

    # Pega a chamada feita para o comando 'personagens'
    chamada_personagens = None
    for call in mock_enviar.call_args_list:
        # O segundo argumento da chamada é o prompt
        if "personagens de jogador" in call[0][1]:
            chamada_personagens = call[0][1]
            break

    assert chamada_personagens is not None
    # Verifica se o prompt foi formatado com os valores corretos
    assert "5 personagens" in chamada_personagens
    assert "Pathfinder" in chamada_personagens
    assert "Nível 10" in chamada_personagens
