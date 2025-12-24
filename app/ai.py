# app/ai.py

import os
import json
import google.generativeai as genai
import time
import requests
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable, GatewayTimeout, InternalServerError, Aborted
import os
import json
import google.generativeai as genai
import time
import requests
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable, GatewayTimeout, InternalServerError, Aborted
import google.generativeai.protos as protos # Import protos

PROMPTS_FILE_PATH = os.path.join(os.path.dirname(__file__), "prompts.json")

# Define Token Limits (conservative estimates, always refer to official docs)
MAX_CONTEXT_TOKENS = 32000  # Max input tokens for gemini-pro (using as a baseline)
TOKEN_BUFFER = 1000         # Buffer for AI response + safety margin

class GeminiAPIError(Exception):
    """Custom exception for Gemini API errors."""
    pass

def _load_prompts():
    with open(PROMPTS_FILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

_prompts_data = _load_prompts()
SYSTEM_INSTRUCTION = _prompts_data["system_instruction"]
COMMAND_PROMPTS = _prompts_data["command_prompts"]
SETUP_PROMPT_TEMPLATE = _prompts_data["setup_prompt_template"]
CHARACTER_CREATION_PROMPTS = _prompts_data["character_creation_prompts"]

def _get_token_count(model, messages: list[protos.Content]) -> int:
    """Helper to count tokens in a list of messages."""
    contents = []
    for message in messages:
        contents.append(message)
    
    return model.count_tokens(contents=contents).total_tokens

def manage_chat_history(model: genai.GenerativeModel, chat: genai.ChatSession, new_message_content: str):
    """
    Manages the chat history to keep it within the token limit using a truncation strategy.
    Removes oldest User/Model message pairs from history if limit is exceeded.
    """
    current_history_tokens = _get_token_count(model, chat.history)
    new_message_tokens = model.count_tokens([new_message_content]).total_tokens

    total_tokens = current_history_tokens + new_message_tokens + TOKEN_BUFFER

    while total_tokens > MAX_CONTEXT_TOKENS and len(chat.history) > 0:
        # Remove the oldest pair of messages (User and Model)
        if len(chat.history) >= 2:
            removed_user_msg = chat.history.pop(0)
            removed_model_msg = chat.history.pop(0)
            
            # Recalculate tokens after removal
            current_history_tokens = _get_token_count(model, chat.history)
            total_tokens = current_history_tokens + new_message_tokens + TOKEN_BUFFER
            # print(f"DEBUG: Removed old messages. New total tokens: {total_tokens}")
        else:
            break
    
    if total_tokens > MAX_CONTEXT_TOKENS:
        print(f"WARNING: Even after truncating history, the message + remaining history exceeds MAX_CONTEXT_TOKENS ({MAX_CONTEXT_TOKENS}). Proceeding, but may lead to API errors.")


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(5),
    retry=(retry_if_exception_type(ResourceExhausted) | # Rate limit
           retry_if_exception_type(ServiceUnavailable) |
           retry_if_exception_type(GatewayTimeout) |
           retry_if_exception_type(InternalServerError) |
           retry_if_exception_type(Aborted) |
           retry_if_exception_type(requests.exceptions.RequestException)),
    reraise=True
)
def call_gemini_api(api_call_func, *args, **kwargs):
    """
    Wrapper function to call Gemini API with retry logic.
    Handles transient errors and rate limits with exponential backoff.
    Also manages chat history token limits if api_call_func is chat.send_message.
    """
    chat_obj = None
    new_message_content = None

    # Identify if it's a chat.send_message call
    if hasattr(api_call_func, '__self__') and isinstance(api_call_func.__self__, genai.ChatSession): # Modified type check
        chat_obj = api_call_func.__self__
        model_obj = chat_obj.model # Access model from chat object
        # Assuming the first arg to send_message is the message content
        new_message_content = args[0] if args else kwargs.get('content')
        if new_message_content and model_obj:
            manage_chat_history(model_obj, chat_obj, new_message_content)

    try:
        response = api_call_func(*args, **kwargs)
        # Check for specific error responses from the API if not raised as exceptions
        if hasattr(response, 'candidates') and not response.candidates:
            # This can happen if the prompt was blocked or generated no content
            raise GeminiAPIError("Gemini API call returned no candidates (content blocked or empty response).")
        return response
    except ResourceExhausted as e:
        print(f"Rate limit exceeded (ResourceExhausted). Retrying... {e}")
        raise
    except requests.exceptions.RequestException as e:
        print(f"Network or request error. Retrying... {e}")
        raise
    except Exception as e:
        # Catch other unexpected errors that might not be transient
        print(f"An unexpected error occurred during Gemini API call: {e}")
        raise GeminiAPIError(f"Unexpected API error: {e}")

def iniciar_modelo_e_chat():
    """Helper para configurar o modelo e iniciar o chat."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("A variável de ambiente GEMINI_API_KEY não foi definida.")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-2.5-pro",
        system_instruction=SYSTEM_INSTRUCTION
    )
    # Return both model and chat session
    return model, model.start_chat(history=[])

def enviar_setup_inicial(model, chat, **kwargs): # Added model as argument
    """Envia a configuração inicial para a IA e já pede o primeiro passo."""
    setup_prompt = SETUP_PROMPT_TEMPLATE.format(
        sistema=kwargs["sistema"],
        genero_estilo=kwargs["genero_estilo"],
        num_jogadores=kwargs["num_jogadores"],
        nivel_tier=kwargs["nivel_tier"],
        tempo_estimado=kwargs["tempo_estimado"]
    )
    # The initial setup prompt is sent with an empty history, so token management for history is not critical here.
    # However, for consistency, we can still call it if the API requires the model context
    # manage_chat_history(model, chat, setup_prompt) # Now requires model as argument
    
    response = call_gemini_api(chat.send_message, setup_prompt)
    return response.text

def gerar_e_salvar_imagem(prompt: str, output_dir: str = "aventura_gerada/imagens") -> str:
    """
    Gera uma imagem usando a IA com base em um prompt de texto e a salva localmente.

    Args:
        prompt: O texto que descreve a imagem a ser gerada.
        output_dir: O diretório onde a imagem será salva.

    Returns:
        O caminho do arquivo da imagem salva.
    """
    # Garante que o diretório de output exista
    os.makedirs(output_dir, exist_ok=True)

    click.echo(click.style("Conectando ao modelo de geração de imagem...", fg="cyan"))
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-image') 
        response = call_gemini_api(model.generate_content, prompt, stream=True)
        response.resolve()

        if hasattr(response, 'parts') and response.parts:
            image_data = response.parts[0].inline_data.data
            
            safe_filename = "".join(x for x in prompt if x.isalnum())[:20] + ".png"
            image_path = os.path.join(output_dir, safe_filename)
            
            with open(image_path, "wb") as f:
                f.write(image_data)
            
            return image_path
        else:
            raise GeminiAPIError("A resposta da IA não continha dados de imagem válidos.")

    except GeminiAPIError as e:
        click.echo(click.style(f"Falha na API Gemini ao gerar imagem: {e}", fg="red"))
        click.echo(click.style("Gerando uma imagem de placeholder.", fg="yellow"))
        
        try:
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new('RGB', (512, 512), color = 'darkgray')
            d = ImageDraw.Draw(img)
            
            try:
                fnt = ImageFont.truetype("arial.ttf", 20)
            except IOError:
                fnt = ImageFont.load_default()

            text = f"Placeholder para:\n{prompt}"
            d.text((10,10), text, font=fnt, fill=(255,255,255))
            
            safe_filename = "".join(x for x in prompt if x.isalnum())[:20] + "_placeholder.png"
            placeholder_path = os.path.join(output_dir, safe_filename)
            img.save(placeholder_path)
            return placeholder_path
        except Exception as placeholder_e:
            raise RuntimeError(f"Falha ao gerar imagem com IA e também ao criar placeholder: {placeholder_e}")
    except Exception as e:
        click.echo(click.style(f"Erro inesperado ao gerar imagem: {e}", fg="red"))
        click.echo(click.style("Gerando uma imagem de placeholder.", fg="yellow"))
        try:
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new('RGB', (512, 512), color = 'darkgray')
            d = ImageDraw.Draw(img)
            try:
                fnt = ImageFont.truetype("arial.ttf", 20)
            except IOError:
                fnt = ImageFont.load_default()
            text = f"Placeholder para:\n{prompt}"
            d.text((10,10), text, font=fnt, fill=(255,255,255))
            safe_filename = "".join(x for x in prompt if x.isalnum())[:20] + "_placeholder.png"
            placeholder_path = os.path.join(output_dir, safe_filename)
            img.save(placeholder_path)
            return placeholder_path
        except Exception as placeholder_e:
            raise RuntimeError(f"Falha ao gerar imagem com IA e também ao criar placeholder: {placeholder_e}")


# Define Token Limits (conservative estimates, always refer to official docs)
MAX_CONTEXT_TOKENS = 32000  # Max input tokens for gemini-pro (using as a baseline)
TOKEN_BUFFER = 1000         # Buffer for AI response + safety margin

class GeminiAPIError(Exception):
    """Custom exception for Gemini API errors."""
    pass

def _load_prompts():
    with open(PROMPTS_FILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

_prompts_data = _load_prompts()
SYSTEM_INSTRUCTION = _prompts_data["system_instruction"]
COMMAND_PROMPTS = _prompts_data["command_prompts"]
SETUP_PROMPT_TEMPLATE = _prompts_data["setup_prompt_template"]
CHARACTER_CREATION_PROMPTS = _prompts_data["character_creation_prompts"]

def _get_token_count(model, messages: list[protos.Content]) -> int:
    """Helper to count tokens in a list of messages."""
    contents = []
    for message in messages:
        contents.append(message)
    
    return model.count_tokens(contents=contents).total_tokens

def manage_chat_history(model: genai.GenerativeModel, chat: genai.ChatSession, new_message_content: str):
    """
    Manages the chat history to keep it within the token limit using a truncation strategy.
    Removes oldest User/Model message pairs from history if limit is exceeded.
    """
    # Create a dummy model to count tokens.
    # The actual model is available in iniciar_modelo_e_chat.
    # For simplicity, we'll assume the chat object has access to its model's count_tokens.
    # A more robust solution might pass the model object explicitly.
    model = chat.model 

    current_history_tokens = _get_token_count(model, chat.history)
    new_message_tokens = model.count_tokens([new_message_content]).total_tokens

    total_tokens = current_history_tokens + new_message_tokens + TOKEN_BUFFER

    while total_tokens > MAX_CONTEXT_TOKENS and len(chat.history) > 0:
        # Remove the oldest pair of messages (User and Model)
        # Assuming history is [user_msg, model_msg, user_msg, model_msg, ...]
        if len(chat.history) >= 2:
            removed_user_msg = chat.history.pop(0)
            removed_model_msg = chat.history.pop(0)
            
            # Recalculate tokens after removal
            current_history_tokens = _get_token_count(model, chat.history)
            total_tokens = current_history_tokens + new_message_tokens + TOKEN_BUFFER
            # print(f"DEBUG: Removed old messages. New total tokens: {total_tokens}")
        else:
            # If only one message left and still over limit, something is wrong or message too long
            break
    
    if total_tokens > MAX_CONTEXT_TOKENS:
        print(f"WARNING: Even after truncating history, the message + remaining history exceeds MAX_CONTEXT_TOKENS ({MAX_CONTEXT_TOKENS}). Proceeding, but may lead to API errors.")


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(5),
    retry=(retry_if_exception_type(ResourceExhausted) | # Rate limit
           retry_if_exception_type(ServiceUnavailable) |
           retry_if_exception_type(GatewayTimeout) |
           retry_if_exception_type(InternalServerError) |
           retry_if_exception_type(Aborted) |
           retry_if_exception_type(requests.exceptions.RequestException)),
    reraise=True
)
def call_gemini_api(api_call_func, *args, **kwargs):
    """
    Wrapper function to call Gemini API with retry logic.
    Handles transient errors and rate limits with exponential backoff.
    Also manages chat history token limits if api_call_func is chat.send_message.
    """
    chat_obj = None
    new_message_content = None

    # Identify if it's a chat.send_message call
    if hasattr(api_call_func, '__self__') and isinstance(api_call_func.__self__, core.ChatSession):
        chat_obj = api_call_func.__self__
        # Assuming the first arg to send_message is the message content
        new_message_content = args[0] if args else kwargs.get('content')
        if new_message_content:
            manage_chat_history(chat_obj, new_message_content)

    try:
        response = api_call_func(*args, **kwargs)
        # Check for specific error responses from the API if not raised as exceptions
        if hasattr(response, 'candidates') and not response.candidates:
            # This can happen if the prompt was blocked or generated no content
            raise GeminiAPIError("Gemini API call returned no candidates (content blocked or empty response).")
        return response
    except ResourceExhausted as e:
        print(f"Rate limit exceeded (ResourceExhausted). Retrying... {e}")
        raise
    except requests.exceptions.RequestException as e:
        print(f"Network or request error. Retrying... {e}")
        raise
    except Exception as e:
        # Catch other unexpected errors that might not be transient
        print(f"An unexpected error occurred during Gemini API call: {e}")
        raise GeminiAPIError(f"Unexpected API error: {e}")

def iniciar_modelo_e_chat():
    """Helper para configurar o modelo e iniciar o chat."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("A variável de ambiente GEMINI_API_KEY não foi definida.")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-2.5-pro",
        system_instruction=SYSTEM_INSTRUCTION
    )
    # Return both model and chat session
    return model, model.start_chat(history=[])

def enviar_setup_inicial(model, chat, **kwargs): # Added model as argument
    """Envia a configuração inicial para a IA e já pede o primeiro passo."""
    setup_prompt = SETUP_PROMPT_TEMPLATE.format(
        sistema=kwargs["sistema"],
        genero_estilo=kwargs["genero_estilo"],
        num_jogadores=kwargs["num_jogadores"],
        nivel_tier=kwargs["nivel_tier"],
        tempo_estimado=kwargs["tempo_estimado"]
    )
    # The initial setup prompt is sent with an empty history, so token management for history is not critical here.
    # However, for consistency, we can still call it if the API requires the model context
    # manage_chat_history(chat, setup_prompt) # Not strictly necessary for initial setup if history is empty
    
    response = call_gemini_api(chat.send_message, setup_prompt)
    return response.text

def gerar_e_salvar_imagem(prompt: str, output_dir: str = "aventura_gerada/imagens") -> str:
    """
    Gera uma imagem usando a IA com base em um prompt de texto e a salva localmente.

    Args:
        prompt: O texto que descreve a imagem a ser gerada.
        output_dir: O diretório onde a imagem será salva.

    Returns:
        O caminho do arquivo da imagem salva.
    """
    # Garante que o diretório de output exista
    os.makedirs(output_dir, exist_ok=True)

    click.echo(click.style("Conectando ao modelo de geração de imagem...", fg="cyan"))
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-image') 
        response = call_gemini_api(model.generate_content, prompt, stream=True)
        response.resolve()

        if hasattr(response, 'parts') and response.parts:
            image_data = response.parts[0].inline_data.data
            
            safe_filename = "".join(x for x in prompt if x.isalnum())[:20] + ".png"
            image_path = os.path.join(output_dir, safe_filename)
            
            with open(image_path, "wb") as f:
                f.write(image_data)
            
            return image_path
        else:
            raise GeminiAPIError("A resposta da IA não continha dados de imagem válidos.")

    except GeminiAPIError as e:
        click.echo(click.style(f"Falha na API Gemini ao gerar imagem: {e}", fg="red"))
        click.echo(click.style("Gerando uma imagem de placeholder.", fg="yellow"))
        
        try:
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new('RGB', (512, 512), color = 'darkgray')
            d = ImageDraw.Draw(img)
            
            try:
                fnt = ImageFont.truetype("arial.ttf", 20)
            except IOError:
                fnt = ImageFont.load_default()

            text = f"Placeholder para:\n{prompt}"
            d.text((10,10), text, font=fnt, fill=(255,255,255))
            
            safe_filename = "".join(x for x in prompt if x.isalnum())[:20] + "_placeholder.png"
            placeholder_path = os.path.join(output_dir, safe_filename)
            img.save(placeholder_path)
            return placeholder_path
        except Exception as placeholder_e:
            raise RuntimeError(f"Falha ao gerar imagem com IA e também ao criar placeholder: {placeholder_e}")
    except Exception as e:
        click.echo(click.style(f"Erro inesperado ao gerar imagem: {e}", fg="red"))
        click.echo(click.style("Gerando uma imagem de placeholder.", fg="yellow"))
        try:
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new('RGB', (512, 512), color = 'darkgray')
            d = ImageDraw.Draw(img)
            try:
                fnt = ImageFont.truetype("arial.ttf", 20)
            except IOError:
                fnt = ImageFont.load_default()
            text = f"Placeholder para:\n{prompt}"
            d.text((10,10), text, font=fnt, fill=(255,255,255))
            safe_filename = "".join(x for x in prompt if x.isalnum())[:20] + "_placeholder.png"
            placeholder_path = os.path.join(output_dir, safe_filename)
            img.save(placeholder_path)
            return placeholder_path
        except Exception as placeholder_e:
            raise RuntimeError(f"Falha ao gerar imagem com IA e também ao criar placeholder: {placeholder_e}")
