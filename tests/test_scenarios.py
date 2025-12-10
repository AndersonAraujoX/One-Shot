import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from backend.app.api import app
import json

client = TestClient(app)

@pytest.mark.parametrize("scenario", [
    {
        "name": "D&D 5e High Fantasy",
        "payload": {
            "sistema": "D&D 5e",
            "genero_estilo": "High Fantasy",
            "num_jogadores": 4,
            "nivel_tier": "Level 5",
            "tempo_estimado": "4h",
            "temperature": 0.7,
            "homebrew_rules": ""
        }
    },
    {
        "name": "Call of Cthulhu Horror",
        "payload": {
            "sistema": "Call of Cthulhu 7e",
            "genero_estilo": "Cosmic Horror",
            "num_jogadores": 3,
            "nivel_tier": "Investigators",
            "tempo_estimado": "3h",
            "temperature": 0.5,
            "homebrew_rules": "Sanity loss is doubled."
        }
    },
    {
        "name": "Tormenta 20 Action",
        "payload": {
            "sistema": "Tormenta 20",
            "genero_estilo": "Action Adventure",
            "num_jogadores": 5,
            "nivel_tier": "Nível 10",
            "tempo_estimado": "5h",
            "temperature": 0.9,
            "homebrew_rules": "Mana regeneration is slow."
        }
    },
    {
        "name": "Cyberpunk 2020",
        "payload": {
            "sistema": "Cyberpunk 2020",
            "genero_estilo": "Cyberpunk",
            "num_jogadores": 4,
            "nivel_tier": "Edgerunners",
            "tempo_estimado": "4h",
            "temperature": 0.8,
            "homebrew_rules": "Netrunning is simplified."
        }
    }
])
def test_adventure_scenarios(scenario):
    print(f"Testing Scenario: {scenario['name']}")
    
    # Mock the stream to avoid real API calls
    with patch("backend.app.api.gerar_aventura_stream") as mock_stream:
        def dummy_generator(**kwargs):
            yield json.dumps({"type": "progress", "message": f"Generating for {kwargs['sistema']}..."}) + "\n"
            yield json.dumps({"type": "data", "section": "contexto", "content": {"titulo": f"Adventure for {kwargs['sistema']}", "sinopse": "Test synopsis"}}) + "\n"
            
        mock_stream.side_effect = dummy_generator
        
        response = client.post("/api/generate_adventure", json=scenario["payload"])
        assert response.status_code == 200
        
        content = b"".join(response.iter_bytes())
        assert f"Generating for {scenario['payload']['sistema']}...".encode() in content
        assert f"Adventure for {scenario['payload']['sistema']}".encode() in content

def test_homebrew_injection():
    # Verify that homebrew rules are actually passed to the chat initialization
    payload = {
        "sistema": "Generic",
        "genero_estilo": "Test",
        "num_jogadores": 1,
        "nivel_tier": "1",
        "tempo_estimado": "1h",
        "temperature": 0.7,
        "homebrew_rules": "ALL CAPS ONLY."
    }
    
    with patch("backend.app.api.iniciar_chat") as mock_init:
        # We need to mock the stream which calls iniciar_chat, 
        # but since we are testing api.py -> chat.py integration, 
        # we might need to let api.py call the real chat.gerar_aventura_stream 
        # but mock what's inside it.
        
        # Actually, api.py imports gerar_aventura_stream from chat.py.
        # So if we want to test that parameters are passed correctly down to iniciar_chat,
        # we should test chat.gerar_aventura_stream directly or mock it in api.py and inspect call args?
        # No, api.py calls gerar_aventura_stream(**config.model_dump()).
        # So we trust api.py passes it.
        # We should test backend/app/chat.py's gerar_aventura_stream to see if it calls iniciar_chat with correct params.
        
        from backend.app.chat import gerar_aventura_stream
        
        # Mock iniciar_chat inside chat.py context
        with patch("backend.app.chat.iniciar_chat") as mock_chat_init:
            mock_chat_obj = MagicMock()
            mock_chat_init.return_value = mock_chat_obj
            
            # Mock enviar_mensagem to avoid API calls
            with patch("backend.app.chat.enviar_mensagem") as mock_send:
                mock_send.return_value = "{}"
                
                # Run the generator
                gen = gerar_aventura_stream(**payload)
                # Consume at least one item
                next(gen)
                
                # Check if iniciar_chat was called with homebrew_rules
                mock_chat_init.assert_called_once()
                call_kwargs = mock_chat_init.call_args[1]
                assert call_kwargs["homebrew_rules"] == "ALL CAPS ONLY."
                assert call_kwargs["temperature"] == 0.7
