# backend/app/chat.py
import os
import json
import google.generativeai as genai
from PIL import Image
import uuid
import re
import base64
from dotenv import load_dotenv
from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value
from .image_utils import create_token
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.api_core import exceptions as api_exceptions

# Carrega variáveis de ambiente
load_dotenv()

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
        "batch_order": 1,
        "json_mode": True
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
        "batch_order": 4,
        "json_mode": True
    },
    "locais_importantes": {
        "prompt": "Agora, usando o contexto e os personagens que você acabou de criar, descreva os 'Locais Importantes' onde a aventura se desenrolará. Garanta que os locais estejam conectados à trama do vilão. Formate a resposta como um array JSON, onde cada objeto representa um local e tem as chaves 'nome' (string), 'atmosfera' (string), e 'url_imagem' (string, uma URL de imagem placeholder).",
        "description": "Descreve os locais importantes.",
        "batch_order": 5,
        "json_mode": True
    },
    "cenario": {
        "prompt": "Baseado especificamente nos locais descritos acima, gere 3 prompts de texto para um gerador de imagens de IA criar mapas de batalha 2D, estilo top-down, para os encontros mais prováveis nesses locais.",
        "description": "Gera prompts para mapas de batalha.",
        "batch_order": 6
    },
    "desafios": {
        "prompt": "Com base na trama, nos personagens (especialmente o vilão) e nos locais estabelecidos, gere os 'Desafios' (combates, puzzles, interações).",
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
    },
    "gerar_imagem": {
        "prompt": "A logo for a CLI application that helps you create RPG adventures. The logo should be simple, modern, and represent creativity and adventure. The main colors should be blue, green, and black.",
        "description": "Gera uma imagem para o projeto.",
        "batch_order": 13
    }
}

class ContentGenerationError(Exception):
    """Exceção personalizada para erros durante a geração de conteúdo pela IA."""
    pass

def iniciar_chat(json_mode=False, sistema="Genérico", genero="Fantasia", temperature=0.7, homebrew_rules=""):
    """Configura o modelo e inicia a sessão de chat com instruções dinâmicas."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("A variável de ambiente GEMINI_API_KEY não foi definida.")
    
    genai.configure(api_key=api_key)
    
    # Dynamic System Instruction
    dynamic_instruction = SYSTEM_INSTRUCTION
    
    if "D&D" in sistema or "Dungeons & Dragons" in sistema:
        dynamic_instruction += "\n\n**Regras Específicas (D&D 5e):**\n- Use termos como 'Teste de Resistência', 'Classe de Armadura (CA)', 'Vantagem/Desvantagem'.\n- Estruture os blocos de estatísticas de monstros de forma simplificada mas compatível."
    elif "Cthulhu" in sistema:
        dynamic_instruction += "\n\n**Regras Específicas (Call of Cthulhu):**\n- Foque em 'Sanidade', 'Investigação' e horror cósmico.\n- Os desafios devem ser letais e psicológicos."
    elif "Tormenta" in sistema:
        dynamic_instruction += "\n\n**Regras Específicas (Tormenta 20):**\n- Use termos como 'Defesa', 'Pontos de Mana', 'Perícias'.\n- Inclua referências a Arton se apropriado."

    if homebrew_rules:
        dynamic_instruction += f"\n\n**REGRAS DA CASA / CONTEXTO ADICIONAL:**\n{homebrew_rules}\n"

    # Few-Shot Example (Simplified)
    dynamic_instruction += """
    
    **Exemplo de Estilo Esperado (Few-Shot):**
    
    Titulo: O Sussurro da Maré
    Sinopse: Os aventureiros são contratados para investigar o desaparecimento de pescadores em uma vila costeira, apenas para descobrir que um culto antigo despertou uma criatura das profundezas.
    Ganchos:
    1. Um pedido de socorro encontrado em uma garrafa.
    2. O prefeito da vila oferece uma recompensa generosa.
    """

    generation_config = {}
    if json_mode:
        generation_config["response_mime_type"] = "application/json"
    
    generation_config["temperature"] = temperature

    model = genai.GenerativeModel(
        model_name="gemini-2.5-pro",
        system_instruction=dynamic_instruction,
        generation_config=generation_config
    )
    return model.start_chat(history=[])

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(api_exceptions.InternalServerError),
    reraise=True  # Re-levanta a exceção se as tentativas falharem
)
def enviar_mensagem(chat, prompt: str, max_history_tokens: int = 10, json_mode: bool = False) -> str:
    """
    Envia uma mensagem para o chat com tratamento de erro e gerenciamento de histórico.
    """
    # Limita o histórico para evitar excesso de tokens
    if len(chat.history) > max_history_tokens:
        # Mantém a instrução de sistema e as N últimas interações
        chat.history = chat.history[-(max_history_tokens):]

    try:
        # Ajusta a configuração de geração dinamicamente se necessário
        # Nota: O SDK do Python pode não suportar mudar generation_config per call facilmente em versões antigas,
        # mas vamos assumir que o chat mantém a config inicial ou que podemos instanciar um novo chat se precisar mudar drasticamente.
        # Para simplificar, se precisarmos de JSON, vamos confiar que o prompt pede JSON e o modelo obedece,
        # ou idealmente, deveríamos ter chats separados ou reconfigurar.
        # Mas o Gemini 1.5+ suporta response_mime_type no generation_config.
        
        # Workaround: Se json_mode for True, tentamos forçar via prompt se a config não for mutável,
        # mas a melhor prática é configurar o modelo corretamente.
        # Como 'chat' é um objeto ChatSession, ele está atrelado a um modelo.
        
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
        # Verifica se as credenciais estão configuradas
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        if not project_id:
             print("GOOGLE_CLOUD_PROJECT não definido. Pulando geração de imagem.")
             return ""

        aiplatform.init(project=project_id, location="us-central1")

        model = aiplatform.ImageGenerationModel.from_pretrained("imagegeneration@006")
        
        response = model.generate_images(
            prompt=prompt,
            number_of_images=1,
            language="pt-BR",
            aspect_ratio="1:1",
            safety_filter_level="block_some",
            person_generation="allow_adult"
        )

        if response:
            filename = f"{uuid.uuid4()}.png"
            output_dir = "static/generated_images"
            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, filename)
            
            response[0].save(location=filepath, include_generation_parameters=False)
            
            # Gera Token VTT
            token_filename = f"token_{filename}"
            token_filepath = os.path.join(output_dir, token_filename)
            create_token(filepath, token_filepath)

            return f"/{filepath}"
            
        return ""

    except Exception as e:
        print(f"Erro ao gerar imagem: {e}")
        return ""

def gerar_aventura_stream(**kwargs):
    """
    Gera uma aventura completa em modo batch, yieldando resultados parciais (SSE).
    """
    # Inicia chat normal (sem JSON mode forçado globalmente, pois variamos)
    # Para usar JSON mode em chamadas específicas, precisaríamos reconfigurar,
    # mas por enquanto vamos confiar no prompt + parser ou instanciar clients diferentes.
    # O ideal para 'json_mode' é usar clients stateless ou configurar o chat.
    
    # Para simplificar e manter o histórico, vamos usar um único chat.
    # O Gemini é bom em seguir instruções de JSON no prompt mesmo sem o flag forçado,
    # mas o flag garante. Como não podemos mudar a config do chat no meio facilmente sem recriar,
    # vamos manter o chat padrão e usar prompts fortes.
    
    chat = iniciar_chat(
        sistema=kwargs.get("sistema", "Genérico"),
        genero=kwargs.get("genero_estilo", "Fantasia"),
        temperature=kwargs.get("temperature", 0.7),
        homebrew_rules=kwargs.get("homebrew_rules", "")
    )
    
    secoes_customizadas = kwargs.get("secoes")

    if secoes_customizadas:
        comandos_batch = sorted(
            [cmd for cmd in secoes_customizadas if cmd in COMMAND_PROMPTS and COMMAND_PROMPTS[cmd].get("batch_order")],
            key=lambda cmd: COMMAND_PROMPTS[cmd]["batch_order"]
        )
    else:
        comandos_batch = sorted(
            [cmd for cmd, meta in COMMAND_PROMPTS.items() if meta.get("batch_order")],
            key=lambda cmd: COMMAND_PROMPTS[cmd]["batch_order"]
        )

    json_commands = ["contexto", "personagens_chave", "locais_importantes"]

    for comando in comandos_batch:
        if comando == "personagens" and not kwargs.get("gerar_personagens", False):
            continue
        
        # Notifica o início da geração desta seção
        yield json.dumps({"type": "progress", "message": f"Gerando {comando}..."}) + "\n"
        
        if comando == "gerar_imagem":
            prompt_text = COMMAND_PROMPTS[comando]["prompt"]
            img_url = gerar_imagem(prompt_text)
            yield json.dumps({"type": "data", "section": comando, "content": img_url}) + "\n"
            continue

        prompt_info = COMMAND_PROMPTS[comando]
        prompt_text = prompt_info["prompt"].format(**kwargs) if "{" in prompt_info["prompt"] else prompt_info["prompt"]

        try:
            response_text = enviar_mensagem(chat, prompt_text)
            
            # Processa JSON se necessário
            if comando in json_commands:
                try:
                    # Limpeza básica de markdown json
                    clean_text = response_text.replace("```json", "").replace("```", "").strip()
                    data = json.loads(clean_text)
                    yield json.dumps({"type": "data", "section": comando, "content": data}) + "\n"
                except json.JSONDecodeError:
                    # Fallback se falhar o parse
                    yield json.dumps({"type": "data", "section": comando, "content": response_text}) + "\n"
            else:
                yield json.dumps({"type": "data", "section": comando, "content": response_text}) + "\n"
                
        except Exception as e:
            yield json.dumps({"type": "error", "message": str(e)}) + "\n"
