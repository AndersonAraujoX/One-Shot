import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from backend.app.api import app
import json

client = TestClient(app)

# Mocking the chat module to avoid real API calls
@pytest.fixture
def mock_chat():
    with patch("backend.app.api.iniciar_chat") as mock_init, \
         patch("backend.app.api.enviar_mensagem") as mock_send, \
         patch("backend.app.chat.gerar_imagem") as mock_img:
        
        # Setup mock chat object
        mock_chat_obj = MagicMock()
        mock_init.return_value = mock_chat_obj
        
        # Setup mock responses
        mock_send.return_value = "Conteúdo gerado simulado."
        mock_img.return_value = "/static/generated_images/test.png"
        
        yield mock_init, mock_send, mock_img

def test_list_adventures_empty():
    # Ensure we start with a clean DB or mock it. 
    # For simplicity, we just check if it returns a list (might be empty or have previous test data)
    response = client.get("/api/adventures")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_generate_adventure_mocked():
    # Mocking the generator in chat.py is tricky because api.py imports it.
    # We need to patch where it is used.
    # api.py imports gerar_aventura_stream from chat.
    
    with patch("backend.app.api.gerar_aventura_stream") as mock_stream:
        # Mock the generator to yield some dummy data
        def dummy_generator(**kwargs):
            yield json.dumps({"type": "progress", "message": "Iniciando..."}) + "\n"
            yield json.dumps({"type": "data", "section": "contexto", "content": {"titulo": "Teste", "sinopse": "Sinopse teste"}}) + "\n"
            yield json.dumps({"type": "complete"}) + "\n"
            
        mock_stream.side_effect = dummy_generator
        
        payload = {
            "sistema": "Teste System",
            "genero_estilo": "Teste Genre",
            "num_jogadores": 4,
            "nivel_tier": "1",
            "tempo_estimado": "1h",
            "temperature": 0.5,
            "homebrew_rules": "None"
        }
        
        response = client.post("/api/generate_adventure", json=payload)
        assert response.status_code == 200
        # Consume the stream
        content = b"".join(response.iter_bytes())
        assert b"Iniciando..." in content
        assert b"Sinopse teste" in content

def test_create_token_mocked():
    with patch("PIL.Image.open") as mock_open, \
         patch("PIL.Image.new") as mock_new, \
         patch("PIL.ImageOps.fit") as mock_fit, \
         patch("PIL.ImageDraw.Draw") as mock_draw:
        
        from backend.app.image_utils import create_token
        
        mock_img = MagicMock()
        mock_open.return_value = mock_img
        mock_img.convert.return_value = mock_img
        mock_img.size = (100, 100)
        
        mock_fit.return_value = mock_img
        
        result = create_token("dummy.png", "output.png")
        assert result == "output.png"
        mock_img.save.assert_called()

def test_api_endpoints_existence():
    # Check if all new endpoints exist
    assert "/api/adventures" in [route.path for route in app.routes]
    assert "/api/adventures/{adventure_id}" in [route.path for route in app.routes]
    assert "/api/send_message" in [route.path for route in app.routes]
