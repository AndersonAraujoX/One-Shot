# 🎲 Gerador de One-Shots de RPG

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/AndersonAraujoX/One-Shot/ci.yml?style=for-the-badge&label=Tests)

![GitHub Pages](https://img.shields.io/github/deployments/AndersonAraujoX/One-Shot/github-pages?style=for-the-badge&label=Demo%20Online)

> Uma ferramenta alimentada por **IA Generativa (Google Gemini)** para criar aventuras de RPG "one-shot" completas, com mapas, personagens e trama, prontas para jogar em minutos.

## 🌐 Demo Online

Acesse o **Frontend** rodando no GitHub Pages:
[**🔗 Abrir Aplicação**](https://AndersonAraujoX.github.io/One-Shot)

> **⚠️ Nota Importante**: O GitHub Pages hospeda apenas o **Frontend (Interface)**. Como a IA roda no **Backend (Python)**, a versão online pode não funcionar completamente a menos que você rode o backend localmente e conecte, ou se o backend estiver hospedado em outro serviço (como Render/Railway).

## ✨ Funcionalidades

- **Criação Assistida**: Defina sistema, gênero, nível e deixe a IA criar o resto.
- **Interface Web Moderna**: Frontend em React para uma experiência de usuário fluida.
- **Modo CLI**: Uso via linha de comando para automação em lote.
- **Geração de Imagens**: Criação automática de mapas e retratos de personagens.
- **Exportação**: Baixe suas aventuras em Markdown, JSON ou ZIP.

---

## 🚀 Como Usar a Interface Web (Recomendado)

### 1. Iniciar o Backend
Navegue até a pasta `backend` e inicie o servidor FastAPI:

```bash
cd backend
pip install -r requirements.txt
uvicorn app.api:app --reload
```
*O servidor estará rodando em `http://127.0.0.1:8000`.*

### 2. Iniciar o Frontend
Em outro terminal, navegue até a pasta `frontend` e inicie a aplicação React:

```bash
cd frontend
npm install
npm start
```
*Acesse a aplicação em `http://localhost:3000`.*

---

## 🛠️ Como Usar (CLI)

Se preferir usar o terminal:

1.  **Configure sua API Key:**
    - Crie um arquivo `.env` na pasta `backend`.
    - Adicione: `GEMINI_API_KEY=sua_chave_aqui`

2.  **Execute:**
    ```bash
    cd backend
    python -m app.main --sistema "D&D 5e" --genero "Cyberpunk" --jogadores 4
    ```

---

## 🤖 GitHub Actions (CI/CD)

Este projeto utiliza automação do GitHub para testes e geração na nuvem.

### Configuração
Adicione o Secret `GEMINI_API_KEY` em **Settings > Secrets and variables > Actions**.

### Workflows
- **CI**: Roda testes automaticamente a cada push.
- **Gerar Aventura**: Vá na aba **Actions**, selecione o workflow e gere aventuras sem instalar nada localmente!

---
*Desenvolvido com ❤️ e IA.*
