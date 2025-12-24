# backend/tests/test_cli.py
import pytest
from click.testing import CliRunner
from unittest.mock import patch
from app.main import cli

# Teste para o comando --help
def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'Usage: cli [OPTIONS]' in result.output
    assert 'Assistente de Criação de RPG' in result.output

# Teste básico para o modo batch
@patch('app.main.gerar_aventura_completa')
def test_cli_modo_batch(mock_gerar_aventura):
    runner = CliRunner()
    result = runner.invoke(cli, [
        '--sistema', 'D&D 5e',
        '--genero', 'Fantasia',
        '--jogadores', '4',
        '--nivel', '5',
        '--batch'
    ])
    assert result.exit_code == 0
    # Verifica se a função correta foi chamada
    mock_gerar_aventura.assert_called_once()
    
    # Verifica se os argumentos foram passados corretamente
    call_args, call_kwargs = mock_gerar_aventura.call_args
    assert call_kwargs['sistema'] == 'D&D 5e'
    assert call_kwargs['output_format'] == 'markdown' # Default

# Teste para o modo batch com parâmetros extras
@patch('app.main.gerar_aventura_completa')
def test_cli_modo_batch_com_extras(mock_gerar_aventura):
    runner = CliRunner()
    runner.invoke(cli, [
        '--sistema', 'Cyberpunk',
        '--genero', 'Sci-Fi',
        '--jogadores', '3',
        '--nivel', '1',
        '--batch',
        '--personagens',
        '--output-format', 'json',
        '--output', 'aventura.json'
    ])
    
    # Verifica os parâmetros específicos
    call_args, call_kwargs = mock_gerar_aventura.call_args
    assert call_kwargs['gerar_personagens'] is True
    assert call_kwargs['output_file'] == 'aventura.json'
    assert call_kwargs['output_format'] == 'json'

# Teste para o modo interativo
@patch('app.main.iniciar_sessao_criativa')
def test_cli_modo_interativo(mock_iniciar_sessao):
    runner = CliRunner()
    result = runner.invoke(cli, [
        '--sistema', 'Vampire',
        '--genero', 'Horror',
        '--jogadores', '2',
        '--nivel', '10'
    ])
    
    assert result.exit_code == 0
    # Modo interativo é o padrão (sem --batch)
    mock_iniciar_sessao.assert_called_once()
    
    # Verifica os argumentos
    call_args, call_kwargs = mock_iniciar_sessao.call_args
    assert call_kwargs['sistema'] == 'Vampire'
    assert call_kwargs['num_jogadores'] == 2

# Teste para comando com argumentos faltando
def test_cli_argumentos_faltando():
    runner = CliRunner()
    # Faltando --genero, --jogadores, --nivel
    result = runner.invoke(cli, ['--sistema', 'D&D 5e'])
    
    assert result.exit_code != 0 # Deve falhar
    assert 'Error: Missing option' in result.output
