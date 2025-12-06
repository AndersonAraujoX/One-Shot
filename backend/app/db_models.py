from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class Adventure(Base):
    __tablename__ = "adventures"

    id = Column(String, primary_key=True, index=True) # UUID
    title = Column(String, index=True, default="Nova Aventura")
    synopsis = Column(Text, nullable=True)
    system = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Stores the full generated JSON structure
    data = Column(JSON, default={})

    chat_sessions = relationship("ChatSession", back_populates="adventure")

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, index=True) # UUID
    adventure_id = Column(String, ForeignKey("adventures.id"))
    
    # Serialized chat history (list of dicts)
    history = Column(JSON, default=[])
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    adventure = relationship("Adventure", back_populates="chat_sessions")
