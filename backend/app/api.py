# backend/app/api.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uuid
import traceback
import json
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from .chat import iniciar_chat, enviar_mensagem, ContentGenerationError, gerar_aventura_stream
from .models import Aventura
from .database import engine, get_db, Base
from . import db_models

from fastapi.staticfiles import StaticFiles

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Cria as tabelas do banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI()

import os

# Garante que o diretório static existe
os.makedirs("static", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

class AdventureConfig(BaseModel):
    sistema: str
    genero_estilo: str
    num_jogadores: int
    nivel_tier: str
    tempo_estimado: str
    temperature: float = 0.7
    homebrew_rules: str = ""

class ChatMessage(BaseModel):
    session_id: str
    prompt: str

@app.post("/api/start_chat")
async def start_chat_endpoint(config: AdventureConfig, db: Session = Depends(get_db)):
    """Inicia uma nova sessão de chat e a armazena no banco de dados."""
    session_id = str(uuid.uuid4())
    try:
        # Inicia o chat com a IA (stateless por enquanto, mas mantemos o objeto em memória se precisarmos de cache, 
        # ou recriamos com histórico do DB. Para simplificar, vamos manter o chat em memória E salvar no DB)
        # Nota: Para persistência real entre restarts, precisaríamos reconstruir o chat object a partir do histórico do DB.
        # Por enquanto, vamos focar em salvar o histórico.
        
        chat_session = iniciar_chat()
        
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
        
        # Salva no Banco de Dados
        # Primeiro cria uma aventura placeholder
        db_adventure = db_models.Adventure(id=str(uuid.uuid4()), system=config.sistema)
        db.add(db_adventure)
        db.commit()
        
        # Salva a sessão
        history = [{"role": "user", "parts": [setup_prompt]}, {"role": "model", "parts": [initial_response]}]
        db_session = db_models.ChatSession(id=session_id, adventure_id=db_adventure.id, history=history)
        db.add(db_session)
        db.commit()
        
        return {"session_id": session_id, "initial_response": initial_response, "adventure_id": db_adventure.id}
        
    except Exception as e:
        print("----- ERRO DETALHADO NO /api/start_chat -----")
        traceback.print_exc()
        print("---------------------------------------------")
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {e}")

@app.post("/api/generate_adventure")
async def generate_adventure_endpoint(config: AdventureConfig, db: Session = Depends(get_db)):
    """Gera uma aventura completa em modo batch via Streaming (SSE)."""
    
    # Cria a entrada no DB
    adventure_id = str(uuid.uuid4())
    db_adventure = db_models.Adventure(
        id=adventure_id, 
        system=config.sistema,
        data={} # Inicialmente vazio
    )
    db.add(db_adventure)
    db.commit()

    async def event_generator():
        full_data = {}
        try:
            # Pydantic V2 usa model_dump() em vez de dict()
            for chunk in gerar_aventura_stream(**config.model_dump()):
                # chunk já é uma string JSON formatada com \n
                # Vamos parsear para atualizar o DB progressivamente
                try:
                    data_chunk = json.loads(chunk.strip())
                    if data_chunk["type"] == "data":
                        section = data_chunk["section"]
                        content = data_chunk["content"]
                        
                        # Atualiza o objeto full_data
                        if section == "contexto" and isinstance(content, dict):
                            full_data.update(content)
                        else:
                            full_data[section] = content
                            
                        # Atualiza o DB a cada seção completada (opcional, pode ser pesado)
                        # db_adventure.data = full_data
                        # db.commit() 
                except:
                    pass
                
                yield chunk
            
            # Ao final, salva tudo no DB
            # Precisamos de uma nova sessão ou fazer merge, pois o yield pode demorar
            # e a sessão original pode ter expirado ou ter problemas de thread? 
            # SQLAlchemy Session não é thread-safe, mas aqui estamos na mesma corrotina.
            # Porém, StreamingResponse roda em thread separada? Não, é async.
            # Vamos tentar atualizar o objeto que já temos.
            
            # Re-query para garantir que está anexado
            # db.add(db_adventure) # Já está na sessão
            db_adventure.data = full_data
            if "titulo" in full_data:
                db_adventure.title = full_data["titulo"]
            if "sinopse" in full_data:
                db_adventure.synopsis = full_data["sinopse"]
                
            db.commit()
            
        except Exception as e:
            print(f"Erro no stream: {e}")
            yield json.dumps({"type": "error", "message": str(e)}) + "\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/api/send_message")
async def send_message_endpoint(message: ChatMessage, db: Session = Depends(get_db)):
    """Envia uma mensagem para uma sessão de chat existente."""
    
    # Recupera a sessão do DB
    db_session = db.query(db_models.ChatSession).filter(db_models.ChatSession.id == message.session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Sessão de chat não encontrada.")
    
    try:
        # Reconstrói o chat com histórico
        # Nota: O objeto 'chat' do google.generativeai espera histórico em formato específico
        # history=[{'role': 'user', 'parts': ['...']}, ...]
        
        chat_session = iniciar_chat()
        chat_session.history = db_session.history
        
        response = enviar_mensagem(chat_session, message.prompt)
        
        # Atualiza o histórico no DB
        # O chat.history é atualizado automaticamente pelo SDK, precisamos pegar de volta
        # Mas o SDK retorna objetos, precisamos serializar
        new_history = []
        for msg in chat_session.history:
            new_history.append({
                "role": msg.role,
                "parts": [part.text for part in msg.parts]
            })
            
        db_session.history = new_history
        db.commit()
        
        return {"response": response}
    except ContentGenerationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {e}")

@app.get("/api/adventures")
async def list_adventures(db: Session = Depends(get_db)):
    """Lista todas as aventuras salvas."""
    adventures = db.query(db_models.Adventure).order_by(db_models.Adventure.created_at.desc()).all()
    return adventures

@app.get("/api/adventures/{adventure_id}")
async def get_adventure(adventure_id: str, db: Session = Depends(get_db)):
    """Retorna os detalhes de uma aventura específica."""
    adventure = db.query(db_models.Adventure).filter(db_models.Adventure.id == adventure_id).first()
    if not adventure:
        raise HTTPException(status_code=404, detail="Aventura não encontrada")
    return adventure

from fastapi.responses import Response
from .pdf_exporter import PDFExporter

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