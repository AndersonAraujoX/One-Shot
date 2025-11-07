# app/generator.py (Exemplo com Gemini)

import os
import google.generativeai as genai
from app.prompts import PROMPT_TEMPLATE

# Configuração da API Key a partir de variáveis de ambiente
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
except KeyError:
    raise EnvironmentError("A variável de ambiente 'GEMINI_API_KEY' não foi definida.")

# Modelo de IA recomendado
MODEL = genai.GenerativeModel('gemini-2.5-flash')

def gerar_aventura(
    sistema: str,
    genero_estilo: str,
    num_jogadores: str,
    tempo_estimado: str,
    tom_adicional: str = "Nenhum",
    nivel_tier: str = "Não especificado"
) -> str:
    """
    Formata o prompt e chama a API de IA para gerar a aventura.

    Args:
        sistema: O sistema de regras (ex: "D&D 5e").
        genero_estilo: O gênero da aventura (ex: "Alta Fantasia").
        num_jogadores: O número de jogadores (ex: "3-5 jogadores").
        tempo_estimado: Duração da sessão (ex: "3-4 horas").
        tom_adicional: Palavras-chave para o tom (ex: "Sombrio").
        nivel_tier: Nível de poder dos personagens (ex: "Nível 3").

    Returns:
        A aventura completa em formato Markdown.
    """
    print("Construindo prompt e contatando a IA... Isso pode levar um momento.")

    # Preenche o template com as entradas do usuário
    prompt_final = PROMPT_TEMPLATE.format(
        sistema=sistema,
        genero_estilo=genero_estilo,
        tom_adicional=tom_adicional,
        num_jogadores=num_jogadores,
        nivel_tier=nivel_tier,
        tempo_estimado=tempo_estimado
    )

    try:
        # Faz a chamada para a API
        response = MODEL.generate_content(prompt_final)
        
        # Validação simples da resposta
        if not response.text:
            raise ValueError("A resposta da IA estava vazia.")
            
        return response.text
    except Exception as e:
        print(f"Ocorreu um erro ao chamar a API de IA: {e}")
        return f"## Erro na Geração\n\nNão foi possível gerar a aventura. Detalhes do erro: {e}"
