
import os
import google.generativeai as genai
from dotenv import load_dotenv
import traceback

load_dotenv()

def test_imagen_vertex():
    print("--- Testing Vertex AI (Current Implementation) ---")
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        print("GOOGLE_CLOUD_PROJECT not set. Skipping Vertex AI test.")
        return
    
    try:
        from google.cloud import aiplatform
        aiplatform.init(project=project_id, location="us-central1")
        model = aiplatform.ImageGenerationModel.from_pretrained("imagegeneration@006")
        response = model.generate_images(
            prompt="A futuristic city with flying cars",
            number_of_images=1,
            language="en",
            aspect_ratio="1:1"
        )
        if response:
            print("Vertex AI Success!")
    except Exception:
        print("Vertex AI Failed:")
        traceback.print_exc()

def test_gemini_image_gen():
    print("\n--- Testing Gemini 2.0 Image Gen (API Key) ---")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not set.")
        return

    genai.configure(api_key=api_key)
    try:
        # Tenta usar o modelo do Gemini 2.0 que suporta geração de imagens
        # O endpoint correto para imagens na API pública pode ser 'models/imagen-3.0-generate-001' 
        # ou 'models/gemini-2.0-flash-exp' se multimodal.
        # Vamos listar modelos compatíveis primeiro para debug
        
        print("Listing available generation models:")
        for m in genai.list_models():
             if 'generateContent' in m.supported_generation_methods or 'generateImages' in m.supported_generation_methods:
                 print(f"- {m.name} ({m.supported_generation_methods})")
                 
        target_model = "models/gemini-2.0-flash-exp" 
        # Note: A geração de imagens via google-generativeai SDK python pode ainda não estar 100% alinhada com os endpoints experimentais
        # Vamos tentar uma chamada generate_content pedindo imagem, que é o padrão multimodal.
        
        model = genai.GenerativeModel(target_model)
        # Prompt pedindo imagem explicitamente
        response = model.generate_content("Generate an image of a cute blue robot", generation_config={"response_mime_type": "image/jpeg"})
        
        print(f"Response type: {type(response)}")
        print(response)

    except Exception:
        print("Gemini Image Gen Failed:")
        traceback.print_exc()

if __name__ == "__main__":
    test_imagen_vertex()
    test_gemini_image_gen()
