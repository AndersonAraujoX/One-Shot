# Memória do Projeto: Assistente de Criação de RPG

Este arquivo serve como um resumo de contexto para o assistente de IA (Gemini) que trabalha neste projeto. Ele contém as informações essenciais sobre a arquitetura, funcionalidade e estado atual do código.

---

### 1. Visão Geral do Projeto

O objetivo deste projeto é criar uma aplicação web que auxilia um Mestre de Jogo (GM) a criar aventuras de RPG de forma colaborativa e passo a passo.

A aplicação consiste em um backend FastAPI que serve a lógica de geração de conteúdo e um frontend React que fornece a interface do usuário. Uma versão de demonstração estática do frontend está disponível no GitHub Pages.

### 2. Arquitetura e Tecnologias

- **Backend:**
    - **Framework:** FastAPI
    - **Linguagem:** Python
    - **IA Generativa:** `google-generativeai`
    - **Modelagem de Dados:** Pydantic (`backend/app/models.py`)
    - **Módulos Principais:**
        - `backend/app/api.py`: Ponto de entrada da API FastAPI, define os endpoints.
        - `backend/app/chat.py`: Gerencia a comunicação com a API do Gemini, histórico, geração de imagens e lógica de batch.
        - `backend/app/generator.py`: Lógica para geração de aventura baseada em Pydantic.
        - `backend/app/vtt_exporter.py`: Lógica para exportação para FoundryVTT.
        - `backend/app/pdf_exporter.py`: Lógica para exportação para PDF.
        - `backend/app/interactive.py`: Contém a lógica para o modo interativo (CLI legado).

- **Frontend:**
    - **Framework:** React
    - **Linguagem:** JavaScript
    - **Componentes Principais:**
        - `frontend/src/App.js`: Componente principal, gerencia o estado e a comunicação com o backend/modo demo.
        - `frontend/src/components/AdventureForm.js`: Formulário para configuração da aventura.
        - `frontend/src/components/Chat.js`: Interface de chat para o modo interativo (com suporte a imagens).
        - `frontend/src/components/AdventureView.js`: Visualizador para a aventura gerada em modo batch (com suporte a imagens e botões de exportação).

### 3. Como Executar (Localmente)

#### Backend
1.  Navegue até a pasta `backend`.
2.  Instale as dependências: `pip install -r requirements.txt`.
3.  Crie um arquivo `.env` na pasta `backend` com sua `GEMINI_API_KEY`.
4.  Inicie o servidor: `uvicorn app.api:app --reload`.

#### Frontend
1.  Em outro terminal, navegue até a pasta `frontend`.
2.  Instale as dependências: `npm install`.
3.  Inicie o servidor de desenvolvimento: `npm start`.

A aplicação estará disponível em `http://localhost:3000`.

### 4. Deploy no GitHub Pages (Versão de Demonstração)

Uma versão estática do frontend (apenas demonstração com dados mockados, sem backend ativo) foi deployada no GitHub Pages.

**URL da Demonstração:** [https://AndersonAraujoX.github.io/One-Shot/](https://AndersonAraujoX.github.io/One-Shot/)

### 5. Histórico e Versionamento

- O projeto é versionado com Git.
- O repositório remoto está em: `https://github.com/AndersonAraujoX/One-Shot.git`.
- O arquivo `.gitignore` está configurado para ignorar arquivos de ambiente, caches e arquivos gerados (`*.md`, `*.json`, `*.yaml`, `*.zip`, `.env`, `__pycache__`, `static/generated_images/`).