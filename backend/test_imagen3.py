
import os
import google.generativeai as genai
from dotenv import load_dotenv
import traceback

load_dotenv()

def test_imagen_3_genai():
    print("\n--- Testing Imagen 3 via Google Generative AI SDK ---")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not set.")
        return

    genai.configure(api_key=api_key)
    try:
        # Tenta instanciar o modelo Imagen 3
        # A classe correta no SDK novo pode ser diferente, mas vamos tentar o padrão.
        # Se falhar, vamos tentar listar métodos disponíveis no módulo.
        
        imagen_model = genai.ImageGenerationModel("imagen-3.0-generate-001")
        response = imagen_model.generate_images(
            prompt="A cute robot cat holding a sword",
        )
        
        print("Imagen 3 Response received.")
        print(response)
        response.images[0].save("test_imagen3.png")

    except Exception:
        print("Imagen 3 Gen Failed:")
        traceback.print_exc()

if __name__ == "__main__":
    test_imagen_3_genai()
