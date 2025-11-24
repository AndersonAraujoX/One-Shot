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
    mock_enviar.return_value = "Conteúdo gerado"

    # Chama a função
    adventure_data = gerar_aventura_batch(gerar_personagens=True, sistema="D&D 5e", num_jogadores=4, nivel_tier="1")

    # Verifica se os comandos foram chamados na ordem correta
    comandos_esperados = sorted(
        [cmd for cmd, meta in COMMAND_PROMPTS.items() if meta.get("batch_order")],
        key=lambda cmd: COMMAND_PROMPTS[cmd]["batch_order"]
    )
    
    assert mock_enviar.call_count == len(comandos_esperados)
    
    # Verifica as chaves no dicionário retornado
    for cmd in comandos_esperados:
        assert cmd in adventure_data

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
