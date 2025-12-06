import pytest
from fastapi.testclient import TestClient
from backend.app.api import app
from backend.app.image_utils import create_token
from PIL import Image
import os
import uuid

client = TestClient(app)

def test_adventure_config_params():
    # Test if API accepts new parameters
    payload = {
        "sistema": "D&D 5e",
        "genero_estilo": "Dark Fantasy",
        "num_jogadores": 4,
        "nivel_tier": "Level 5",
        "tempo_estimado": "4h",
        "temperature": 0.9,
        "homebrew_rules": "No magic."
    }
    # We expect 500 because we are not mocking Gemini and it will fail to connect,
    # but we want to ensure validation passes (i.e., not 422).
    # Actually, without mocking, it might try to call start_chat which checks env var.
    # If env var is set, it tries to connect.
    # Let's just check if it parses the model correctly by checking the Pydantic model directly if possible,
    # or relying on the fact that 422 means validation error.
    
    response = client.post("/api/generate_adventure", json=payload)
    assert response.status_code != 422

def test_create_token(tmp_path):
    # Create a dummy image
    img_path = tmp_path / "test_image.png"
    out_path = tmp_path / "test_token.png"
    
    img = Image.new('RGB', (100, 100), color = 'red')
    img.save(img_path)
    
    # Run create_token
    result = create_token(str(img_path), str(out_path))
    
    assert result is not None
    assert os.path.exists(out_path)
    
    # Check if output is RGBA (transparent)
    out_img = Image.open(out_path)
    assert out_img.mode == "RGBA"
