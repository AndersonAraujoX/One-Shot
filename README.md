
# 🎲 Gerador de One-Shots de RPG (v2.0)

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Gemini 2.5](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-8E75B2?style=for-the-badge&logo=google)

> Uma ferramenta alimentada por **Google Gemini 2.5 Flash** para criar aventuras de RPG "one-shot" completas, com NPCs, trama granular, desafios e prompts visuais, prontas para jogar em minutos.

## ✨ Novidades da Versão 2.0

*   **⚡ Gemini 2.5 Flash**: Agora rodando no modelo mais rápido e recente da Google.
*   **🛡️ Geração Granular & Segura**: Nova arquitetura que cria a aventura passo-a-passo (Setup -> Ato 1 -> Ato 2...) para garantir que a história **nunca seja cortada** pela metade.
*   **🎨 Smart Image Prompts**: O sistema gera prompts visuais detalhados para Capa, NPCs e Locais.
    *   *Suporte Experimental*: Tenta usar `gemini-2.5-flash-image` se disponível na sua conta.
    *   *Fallback*: Se a cota de imagem acabar, ele gera o texto do prompt para você usar no Midjourney/DALL-E.
*   **📊 Feedback Visual**: Nova barra de progresso detalhada no Frontend.

---

## 🚀 Instalação e Uso

### Pré-requisitos
*   Python 3.10+
*   Node.js 16+
*   Uma chave de API do Google Gemini (Obtenha no [Google AI Studio](https://aistudio.google.com/))

### 1. Backend (API)

```bash
cd backend
# Crie seu ambiente virtual (opcional mas recomendado)
python -m venv venv
# Windows: venv\Scripts\activate | Linux: source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Crie o arquivo .env
echo GEMINI_API_KEY=sua_chave_aqui > .env

# Inicie o servidor
uvicorn app.api:app --reload
```
*O servidor rodará em `http://127.0.0.1:8000`.*

### 2. Frontend (Interface)

```bash
cd frontend
# Instale as dependências
npm install

# Inicie a aplicação
npm start
```
*Acesse em `http://localhost:3000`.*

---

## 🛠️ Detalhes Técnicos

### Estrutura
*   **Backend**: FastAPI com `google-generativeai`. Implementa retries inteligentes (backoff exponencial) para lidar com limites de taxa (Erro 429).
*   **Frontend**: React com componentes estilizados (Tabbed View, Stat Blocks). Consome a API via **Streaming** para mostrar o progresso em tempo real.

### Arquitetura de Geração
Para contornar limitações de tokens e timeouts, a aventura é gerada em **Batches Granulares**:
1.  **Imagem/Prompt**: Define a estética.
2.  **Mundo**: Cria contexto, ganchos e personagens.
3.  **NPCs & Locais**: Detalha o mundo.
4.  **Trama Sequencial**: Gera Ato 1, depois Ato 2, etc., garantindo coesão e completude.

---

## 🤝 Contribuição

Sinta-se livre para abrir Issues ou Pull Requests. O foco atual é melhorar a consistência dos prompts de imagem e expandir os sistemas de RPG suportados (atualmente focado em D&D 5e).

---
*Desenvolvido por Anderson Araújo com ajuda de Agentes de IA.*
