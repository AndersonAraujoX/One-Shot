# backend/app/chat.py

import os
import json
import google.generativeai as genai
from google.api_core import exceptions as api_exceptions
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from PIL import Image
import uuid
import re

# --- INSTRUÇÃO DE SISTEMA ---
SYSTEM_INSTRUCTION = """
Você é um Assistente de Mestre de Jogo (GM) para RPGs de mesa. Sua especialidade é a criação colaborativa de aventuras no formato "one-shot".
Seu objetivo é ajudar o usuário a construir uma aventura coesa e interessante, passo a passo.
Responda em português do Brasil.
Use formatação Markdown para organizar o texto de forma clara (títulos, listas, negrito).
Para cada parte da aventura, seja criativo e detalhado, sempre mantendo a consistência com o que já foi estabelecido em nosso histórico de conversa.
"""

# --- PROMPTS PARA COMANDOS ---
COMMAND_PROMPTS = {
    "contexto": {
        "prompt": "Baseado em todo o nosso histórico de conversa até agora, gere o 'Contexto (Background)' e a 'Sinopse' para esta aventura. Formate a resposta como um objeto JSON com as chaves 'titulo' (string) e 'sinopse' (string).",
        "description": "Gera o background e a sinopse da aventura.",
        "batch_order": 1
    },
    "ganchos": {
        "prompt": "Excelente. Agora, baseado em todo o histórico, gere os 'Ganchos da Trama' para iniciar a aventura.",
        "description": "Cria os ganchos da trama.",
        "batch_order": 2
    },
    "personagens": {
        "prompt": "Ótimo. Agora, gere {num_jogadores} personagens de jogador prontos para esta aventura, no sistema {sistema} e nível {nivel_tier}. Para cada um, detalhe: Nome, Raça/Origem, Classe/Arquétipo, um Background conciso, Personalidade, um Objetivo Pessoal e sugestões de Atributos e Equipamentos iniciais.",
        "description": "Gera os personagens dos jogadores (requer a flag --personagens no modo batch).",
        "batch_order": 3
    },
    "personagens_chave": {
        "prompt": "Ótimo. Descreva agora os 'NPCs Principais', incluindo o vilão e possíveis aliados. Formate a resposta como um array JSON, onde cada objeto representa um NPC e tem as chaves 'nome' (string), 'aparencia' (string), e 'url_imagem' (string, uma URL de imagem placeholder).",
        "description": "Cria os NPCs principais da aventura.",
        "batch_order": 4
    },
    "locais_importantes": {
        "prompt": "Descreva os 'Locais Importantes' onde a aventura se desenrolará. Formate a resposta como um array JSON, onde cada objeto representa um local e tem as chaves 'nome' (string), 'atmosfera' (string), e 'url_imagem' (string, uma URL de imagem placeholder).",
        "description": "Descreve os locais importantes.",
        "batch_order": 5
    },
    "cenario": {
        "prompt": "Baseado nos locais e desafios, gere 3 prompts de texto para um gerador de imagens de IA criar mapas de batalha 2D, estilo top-down, para os encontros mais prováveis.",
        "description": "Gera prompts para mapas de batalha.",
        "batch_order": 6
    },
    "desafios": {
        "prompt": "Com base na trama e nos locais, gere os 'Desafios', como combates, quebra-cabeças ou interações sociais.",
        "description": "Cria os desafios da aventura.",
        "batch_order": 7
    },
    "ato1": {
        "prompt": "Perfeito. Com base no que estabelecemos, gere o 'Ato 1: A Introdução', onde os jogadores se envolvem com a trama.",
        "description": "Gera o primeiro ato da aventura.",
        "batch_order": 8
    },
    "ato2": {
        "prompt": "Continuando nossa história, gere o 'Ato 2: A Complicação', o núcleo da investigação ou exploração.",
        "description": "Gera o segundo ato da aventura.",
        "batch_order": 9
    },
    "ato3": {
        "prompt": "Vamos avançar. Gere o 'Ato 3: O Ponto de Virada', um momento que muda a dinâmica da aventura.",
        "description": "Gera o terceiro ato da aventura.",
        "batch_order": 10
    },
    "ato4": {
        "prompt": "Estamos chegando ao clímax. Gere o 'Ato 4: O Clímax', o confronto final ou a resolução do conflito principal.",
        "description": "Gera o quarto ato da aventura.",
        "batch_order": 11
    },
    "ato5": {
        "prompt": "Para finalizar, gere o 'Ato 5: A Resolução', descrevendo as consequências e o que acontece após o clímax.",
        "description": "Gera o quinto ato da aventura.",
        "batch_order": 12
    },
    "resumo": {
        "prompt": "Por favor, gere um resumo conciso de toda a aventura que criamos até agora, organizando os pontos principais.",
        "description": "Gera um resumo da aventura."
    },
    "regenerar": {
        "prompt": "Vamos refazer uma parte. Baseado em nosso histórico, regenere a seção sobre '{secao}' com uma nova abordagem.",
        "description": "Regenera uma seção específica da aventura."
    },
    "salvar": {
        "prompt": "Salva a sessão atual para continuar mais tarde.",
        "description": "Salva a sessão de chat."
    },
    "carregar": {
        "prompt": "Carrega uma sessão salva anteriormente.",
        "description": "Carrega uma sessão de chat."
    }
}

class ContentGenerationError(Exception):
    """Exceção personalizada para erros durante a geração de conteúdo pela IA."""
    pass

def iniciar_chat():
    """Configura o modelo e inicia a sessão de chat."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("A variável de ambiente GEMINI_API_KEY não foi definida.")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-2.5-pro",
        system_instruction=SYSTEM_INSTRUCTION
    )
    return model.start_chat(history=[])

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(api_exceptions.InternalServerError),
    reraise=True  # Re-levanta a exceção se as tentativas falharem
)
def enviar_mensagem(chat, prompt: str, max_history_tokens: int = 10) -> str:
    """
    Envia uma mensagem para o chat com tratamento de erro e gerenciamento de histórico.
    """
    # Limita o histórico para evitar excesso de tokens
    if len(chat.history) > max_history_tokens:
        # Mantém a instrução de sistema e as N últimas interações
        chat.history = chat.history[-(max_history_tokens):]

    try:
        response = chat.send_message(prompt)
        return response.text
    except api_exceptions.FailedPrecondition as e:
        raise ContentGenerationError(f"Erro de pré-condição da API: {e}")
    except api_exceptions.GoogleAPICallError as e:
        raise ContentGenerationError(f"Ocorreu um erro na API do Gemini: {e}")
    except genai.types.generation_types.StopCandidateException as e:
        raise ContentGenerationError(
            "A geração foi interrompida por políticas de segurança. "
            "Tente reformular o pedido."
        )
    except Exception as e:
        raise ContentGenerationError(f"Ocorreu um erro inesperado: {e}")

def gerar_imagem(prompt: str) -> str:
    """Gera uma imagem a partir de um prompt e a salva localmente."""
    try:
        model = genai.GenerativeModel('gemini-2.5-pro')
        response = model.generate_content(prompt, generation_config={"response_mime_type": "image/png"})
        
        # Extrai os dados da imagem
        image_data = response.parts[0].data
        
        # Cria um nome de arquivo único
        image_filename = f"static/generated_images/{uuid.uuid4()}.png"
        os.makedirs(os.path.dirname(image_filename), exist_ok=True)

        # Salva a imagem
        with open(image_filename, 'wb') as f:
            f.write(image_data)
            
        return f"/{image_filename}"

    except Exception as e:
        print(f"Erro ao gerar imagem: {e}")
        return ""

def gerar_aventura_batch(**kwargs) -> dict:
    """
    Gera uma aventura completa em modo batch de forma data-driven.
    Pode gerar um conjunto pré-definido de seções ou um conjunto customizado 
    passado através de kwargs['secoes'].
    """
    chat = iniciar_chat()
    adventure_data = {}
    
    secoes_customizadas = kwargs.get("secoes")

    if secoes_customizadas:
        # Filtra e ordena as seções customizadas que são válidas e têm uma ordem de batch
        comandos_batch = sorted(
            [cmd for cmd in secoes_customizadas if cmd in COMMAND_PROMPTS and COMMAND_PROMPTS[cmd].get("batch_order")],
            key=lambda cmd: COMMAND_PROMPTS[cmd]["batch_order"]
        )
        if not comandos_batch:
            raise ValueError("Nenhuma das seções fornecidas é válida para o modo batch. Seções válidas: " +
                             ", ".join([k for k, v in COMMAND_PROMPTS.items() if v.get("batch_order")]))
    else:
        # Comportamento padrão: pega todas as seções com 'batch_order'
        comandos_batch = sorted(
            [cmd for cmd, meta in COMMAND_PROMPTS.items() if meta.get("batch_order")],
            key=lambda cmd: COMMAND_PROMPTS[cmd]["batch_order"]
        )

    json_commands = ["contexto", "personagens_chave", "locais_importantes"]

    for comando in comandos_batch:
        if comando == "personagens" and not kwargs.get("gerar_personagens", False):
            continue

        prompt_info = COMMAND_PROMPTS[comando]
        prompt_text = prompt_info["prompt"].format(**kwargs) if "{" in prompt_info["prompt"] else prompt_info["prompt"]

        response_text = enviar_mensagem(chat, prompt_text)

        if comando in json_commands:
            print(f"--- RESPOSTA DA IA PARA '{comando}' ---")
            print(response_text)
            print("-----------------------------------------")
            try:
                json_string = ""
                # Tenta encontrar JSON dentro de ```json ... ```
                match = re.search(r"```json\s*(.*?)\s*```", response_text, re.DOTALL)
                if match:
                    json_string = match.group(1)
                else:
                    # Tenta encontrar JSON dentro de ``` ... ```
                    match = re.search(r"```\s*(.*?)\s*```", response_text, re.DOTALL)
                    if match:
                        json_string = match.group(1)
                    else:
                        # Se não encontrou blocos de código, assume que a resposta inteira é JSON
                        json_string = response_text.strip()

                data = json.loads(json_string)
                if comando == 'contexto':
                    # Adiciona titulo e sinopse ao nível principal
                    adventure_data.update(data)
                else:
                    adventure_data[comando] = data
            except json.JSONDecodeError as e:
                print(f"Alerta: Falha ao decodificar JSON para o comando '{comando}'. Erro: {e}")
                print(f"Resposta bruta da IA: \n{response_text[:500]}...") # Imprime os primeiros 500 caracteres para depuração
                if comando == 'contexto':
                    adventure_data['titulo'] = "Erro na Geração"
                    adventure_data['sinopse'] = "Não foi possível gerar o contexto."
                else:
                    adventure_data[comando] = [] # Retorna uma lista vazia em caso de falha
            except Exception as e:
                print(f"Alerta: Erro inesperado ao processar JSON para o comando '{comando}'. Erro: {e}")
                if comando == 'contexto':
                    adventure_data['titulo'] = "Erro na Geração"
                    adventure_data['sinopse'] = "Não foi possível gerar o contexto."
                else:
                    adventure_data[comando] = []
        else:
            adventure_data[comando] = response_text
            
    return adventure_data
