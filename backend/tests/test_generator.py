# backend/tests/test_generator.py
import pytest
import json
from unittest.mock import Mock, patch
from pydantic import ValidationError
from app.generator import gerar_aventura
from app.models import Aventura

# Mock de uma resposta JSON válida da IA
VALID_JSON_RESPONSE = {
    "titulo": "A Tumba do Terror Rastejante",
    "sinopse": "Uma antiga tumba foi descoberta, mas um mal rastejante guarda seus segredos.",
    "gancho_trama": ["Um mapa misterioso", "Um pedido de um nobre desesperado"],
    "contexto": "O terror rastejante é um fungo inteligente que domina a tumba.",
    "estrutura": [{"titulo": "Ato 1", "descricao": "Os heróis encontram a tumba." }],
    "personagens_chave": [
        {
            "nome": "Elara",
            "aparencia": "Uma exploradora com olhos curiosos.",
            "motivacao": "Buscar conhecimento perdido.",
            "segredo": "Ela é secretamente uma descendente dos guardiões da tumba.",
            "estatisticas": "Scout (D&D 5e)"
        }
    ],
    "monstros_adversarios": ["Fungos Zumbis"],
    "locais_importantes": [{"nome": "A Entrada da Tumba", "atmosfera": "Úmida e escura.", "segredos_interacoes": "Uma armadilha de fosso." } ],
    "desafios_descobertas": ["Um enigma na porta principal."],
    "tesouros_recompensas": ["Uma espada mágica +1."]
}

# Teste de sucesso com JSON válido
def test_gerar_aventura_sucesso_com_json(mocker):
    mock_response = Mock()
    mock_response.text = f"```json\n{json.dumps(VALID_JSON_RESPONSE)}\n```"
    
    mocker.patch('app.generator.MODEL.generate_content', return_value=mock_response)
    
    resultado = gerar_aventura("D&D 5e", "Fantasia", "4", "3 horas")
    
    assert isinstance(resultado, Aventura)
    assert resultado.titulo == VALID_JSON_RESPONSE["titulo"]
    assert len(resultado.estrutura) == 1
    assert resultado.estrutura[0].titulo == "Ato 1"

# Teste para JSON malformado
def test_gerar_aventura_json_invalido(mocker):
    mock_response = Mock()
    mock_response.text = "```json\n{\"titulo\": \"Incompleto...\" \n```" # JSON inválido
    
    mocker.patch('app.generator.MODEL.generate_content', return_value=mock_response)
    
    with pytest.raises(ValidationError):
        gerar_aventura("D&D 5e", "Fantasia", "4", "3 horas")

# Teste para dados que não correspondem ao modelo Pydantic
def test_gerar_aventura_dados_nao_conformes(mocker):
    invalid_data = VALID_JSON_RESPONSE.copy()
    invalid_data["titulo"] = 12345  # Título deveria ser string
    
    mock_response = Mock()
    mock_response.text = f"```json\n{json.dumps(invalid_data)}\n```"
    
    mocker.patch('app.generator.MODEL.generate_content', return_value=mock_response)
    
    with pytest.raises(ValidationError):
        gerar_aventura("D&D 5e", "Fantasia", "4", "3 horas")

# Teste para resposta vazia da API
def test_gerar_aventura_resposta_vazia_da_api(mocker):
    mock_response = Mock()
    mock_response.text = ""
    
    mocker.patch('app.generator.MODEL.generate_content', return_value=mock_response)
    
    with pytest.raises(ValueError, match="A resposta da IA estava vazia."):
        gerar_aventura("D&D 5e", "Fantasia", "4", "3 horas")

# Teste para exceção genérica da API
def test_gerar_aventura_excecao_generica_api(mocker):
    mocker.patch('app.generator.MODEL.generate_content', side_effect=Exception("Erro de rede"))
    
    with pytest.raises(Exception, match="Erro de rede"):
        gerar_aventura("D&D 5e", "Fantasia", "4", "3 horas")