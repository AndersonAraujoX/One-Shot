# app/generator.py
import os
import json
import google.generativeai as genai
from app.prompts import PROMPT_TEMPLATE
from app.models import Aventura
from app.chat import gerar_imagem

# Configuração da API Key a partir de variáveis de ambiente
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
except KeyError:
    raise EnvironmentError("A variável de ambiente 'GEMINI_API_KEY' não foi definida.")

# Modelo de IA recomendado
MODEL = genai.GenerativeModel('gemini-1.5-flash')

def gerar_aventura(
    sistema: str,
    genero_estilo: str,
    num_jogadores: str,
    tempo_estimado: str,
    tom_adicional: str = "Nenhum",
    nivel_tier: str = "Não especificado"
) -> Aventura:
    """
    Formata o prompt, chama a API de IA, valida a resposta e gera imagens.
    """
    print("Construindo prompt e contatando a IA...")

    prompt_final = PROMPT_TEMPLATE.replace('{sistema}', sistema)
    prompt_final = prompt_final.replace('{genero_estilo}', genero_estilo)
    prompt_final = prompt_final.replace('{tom_adicional}', tom_adicional)
    prompt_final = prompt_final.replace('{num_jogadores}', num_jogadores)
    prompt_final = prompt_final.replace('{nivel_tier}', nivel_tier)
    prompt_final = prompt_final.replace('{tempo_estimado}', tempo_estimado)

    try:
        response = MODEL.generate_content(prompt_final)
        
        if not response.text:
            raise ValueError("A resposta da IA estava vazia.")
        
        json_text = response.text.strip().replace('```json', '').replace('```', '')
        
        aventura_data = Aventura.model_validate_json(json_text)
        
        # Gera imagens
        for npc in aventura_data.personagens_chave:
            if npc.prompt_imagem:
                npc.url_imagem = gerar_imagem(npc.prompt_imagem)
        
        for local in aventura_data.locais_importantes:
            if local.prompt_imagem:
                local.url_imagem = gerar_imagem(local.prompt_imagem)
                
        return aventura_data
        
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Erro ao decodificar ou validar o JSON da IA: {e}")
        raise
    except Exception as e:
        print(f"Ocorreu um erro ao chamar a API de IA: {e}")
        raise