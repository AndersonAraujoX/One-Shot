# Gerador de One-Shots de RPG

Este projeto utiliza IA Generativa para criar aventuras de RPG "one-shot" prontas para jogar.

## Como Usar a Interface Web

Esta é a forma recomendada de usar a aplicação.

### 1. Iniciar o Backend

Navegue até a pasta `backend` e inicie o servidor FastAPI:

```bash
cd backend
uvicorn app.api:app --reload
```

O servidor estará rodando em `http://127.0.0.1:8000`.

### 2. Iniciar o Frontend

Em outro terminal, navegue até a pasta `frontend` e inicie a aplicação React:

```bash
cd frontend
npm start
```

A interface web estará acessível em `http://localhost:3000`.

## Como Usar (CLI - Legado)

A interface de linha de comando ainda está disponível, mas a interface web é a forma preferida de interação.

### Configuração

1.  **Instale as dependências:**
    ```bash
    pip install -r backend/requirements.txt
    ```

2.  **Configure sua API Key:**
    - Crie um arquivo `.env` na pasta `backend`.
    - Abra o arquivo `.env` e insira sua chave da API do Google Gemini na variável `GEMINI_API_KEY`.

### Execução

Execute o módulo `app.main` a partir do diretório `backend` com os parâmetros desejados.

**Modo Interativo:**

```bash
python3 -m app.main --sistema "D&D 5e" --genero "Fantasia Sombria" --jogadores 4 --nivel "Nível 3"
```

**Modo Batch:**

```bash
python3 -m app.main --sistema "D&D 5e" --genero "Fantasia Sombria" --jogadores 4 --nivel "Nível 3" --batch --output "minha_aventura"
```

### Ajuda

```bash
python3 -m app.main --help
```