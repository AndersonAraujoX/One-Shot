# backend/app/models.py
from pydantic import BaseModel, Field
from typing import List, Optional

class NPC(BaseModel):
    nome: str = Field(description="Nome do NPC")
    aparencia: str = Field(description="Descrição da aparência do NPC")
    motivacao: str = Field(description="Motivação principal do NPC")
    segredo: Optional[str] = Field(None, description="Segredo que o NPC guarda")
    estatisticas: str = Field(description="Sugestão de bloco de estatísticas do sistema de jogo")
    prompt_imagem: Optional[str] = Field(None, description="Prompt para gerar uma imagem do NPC")
    url_imagem: Optional[str] = Field(None, description="URL da imagem gerada para o NPC")

class Local(BaseModel):
    nome: str = Field(description="Nome do local")
    atmosfera: str = Field(description="Descrição da atmosfera do local")
    segredos_interacoes: str = Field(description="Segredos e interações possíveis no local")
    prompt_imagem: Optional[str] = Field(None, description="Prompt para gerar uma imagem do local")
    url_imagem: Optional[str] = Field(None, description="URL da imagem gerada para o local")

class Ato(BaseModel):
    titulo: str = Field(description="Título do ato")
    descricao: str = Field(description="Descrição detalhada do que acontece no ato")

class Aventura(BaseModel):
    titulo: str = Field(description="Título cativante da aventura")
    sinopse: str = Field(description="Parágrafo que resume a premissa da aventura")
    gancho_trama: List[str] = Field(description="Lista de opções de ganchos para a trama")
    contexto: str = Field(description="História de fundo que o Mestre precisa saber")
    estrutura: List[Ato] = Field(description="Lista de atos que compõem a estrutura da aventura")
    personagens_chave: List[NPC] = Field(description="Lista de NPCs importantes na aventura")
    monstros_adversarios: List[str] = Field(description="Lista de encontros com monstros e adversários")
    locais_importantes: List[Local] = Field(description="Lista de locais importantes na aventura")
    desafios_descobertas: List[str] = Field(description="Lista de desafios não relacionados a combate e pistas")
    tesouros_recompensas: List[str] = Field(description="Lista de tesouros e recompensas")