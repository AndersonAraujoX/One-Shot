# backend/app/api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
from .chat import iniciar_chat, enviar_mensagem, ContentGenerationError, gerar_aventura_batch

from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Armazenamento de sessões de chat em memória (para fins de demonstração)
chat_sessions = {}

class AdventureConfig(BaseModel):
    sistema: str
    genero_estilo: str
    num_jogadores: int
    nivel_tier: str
    tempo_estimado: str

class ChatMessage(BaseModel):
    session_id: str
    prompt: str

@app.post("/api/start_chat")
async def start_chat_endpoint(config: AdventureConfig):
    """Inicia uma nova sessão de chat e a armazena."""
    session_id = str(uuid.uuid4())
    try:
        chat_session = iniciar_chat()
        chat_sessions[session_id] = chat_session
        
        # Envia o prompt de setup inicial
        setup_prompt = f'''
        Vamos começar a criar nossa aventura. Aqui estão os parâmetros iniciais:
        - Sistema de Jogo: {config.sistema}
        - Gênero/Estilo: {config.genero_estilo}
        - Número de Jogadores: {config.num_jogadores}
        - Nível/Tier dos Personagens: {config.nivel_tier}
        - Tempo Estimado de Jogo: {config.tempo_estimado}
        Com base nisso, gere o 'Contexto (Background)' e a 'Sinopse'.
        '''
        initial_response = enviar_mensagem(chat_session, setup_prompt)
        
        return {"session_id": session_id, "initial_response": initial_response}
        
    except (ValueError, ContentGenerationError) as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {e}")

@app.post("/api/send_message")
async def send_message_endpoint(message: ChatMessage):
    """Envia uma mensagem para uma sessão de chat existente."""
    chat_session = chat_sessions.get(message.session_id)
    if not chat_session:
        raise HTTPException(status_code=404, detail="Sessão de chat não encontrada.")
    
    try:
        response = enviar_mensagem(chat_session, message.prompt)
        return {"response": response}
    except ContentGenerationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {e}")

from fastapi.responses import Response
from .pdf_exporter import PDFExporter

...

@app.post("/api/export_pdf")
async def export_pdf_endpoint(aventura: Aventura):
    """Exporta a aventura para um arquivo PDF."""
    try:
        exporter = PDFExporter(aventura)
        pdf_bytes = exporter.export_to_pdf()
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={aventura.titulo.lower().replace(' ', '-')}.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao exportar para PDF: {e}")