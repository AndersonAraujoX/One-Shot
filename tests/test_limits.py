import pytest
from unittest.mock import MagicMock, patch
from backend.app.api import app, AdventureConfig
from backend.app.chat import enviar_mensagem, ContentGenerationError
from fastapi.testclient import TestClient

client = TestClient(app)

def test_adventure_config_limits():
    # Test valid config
    config = AdventureConfig(
        sistema="D&D", genero_estilo="Fantasy", num_jogadores=4, 
        nivel_tier="1", tempo_estimado="4h", temperature=0.7, homebrew_rules=""
    )
    assert config.num_jogadores == 4

    # Test extreme values (Pydantic standard validation allows these unless constrained)
    config_extreme = AdventureConfig(
        sistema="A" * 1000, # Long string
        genero_estilo="B" * 1000,
        num_jogadores=1000000,
        nivel_tier="C" * 1000,
        tempo_estimado="D" * 1000,
        temperature=2.0, # Gemini usually caps at 1.0 or 2.0 depending on model, but let's see if app accepts
        homebrew_rules="E" * 10000
    )
    assert config_extreme.num_jogadores == 1000000
    assert len(config_extreme.homebrew_rules) == 10000

def test_history_truncation():
    # Mock chat object
    mock_chat = MagicMock()
    # Create a fake history with 20 items
    mock_chat.history = [MagicMock() for _ in range(20)]
    
    # Call enviar_mensagem with max_history_tokens=10
    # We need to mock chat.send_message to avoid real call
    mock_chat.send_message.return_value.text = "Response"
    
    enviar_mensagem(mock_chat, "Prompt", max_history_tokens=10)
    
    # Check if history was truncated to 10
    assert len(mock_chat.history) == 10

def test_large_payload_api():
    # Test sending a large payload to the API
    large_text = "A" * 50000
    payload = {
        "sistema": large_text,
        "genero_estilo": "Fantasy",
        "num_jogadores": 4,
        "nivel_tier": "1",
        "tempo_estimado": "1h"
    }
    
    # We expect the server to handle it (or fail gracefully if too big, but 50k chars is fine for FastAPI)
    # We mock the stream to avoid processing this huge text in Gemini
    with patch("backend.app.api.gerar_aventura_stream") as mock_stream:
        mock_stream.return_value = iter([]) # Empty stream
        response = client.post("/api/generate_adventure", json=payload)
        assert response.status_code == 200

def test_temperature_validation():
    # Ideally, we should validate temperature is between 0.0 and 1.0 (or 2.0)
    # Currently the code doesn't enforce it, so this test documents current behavior
    # or fails if we decide to enforce it.
    
    # Let's try to pass a string to temperature
    payload = {
        "sistema": "D&D",
        "genero_estilo": "Fantasy",
        "num_jogadores": 4,
        "nivel_tier": "1",
        "tempo_estimado": "1h",
        "temperature": "invalid"
    }
    response = client.post("/api/generate_adventure", json=payload)
    assert response.status_code == 422 # Validation error expected
