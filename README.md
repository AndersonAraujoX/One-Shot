    ```

2.  **Configure sua API Key:**
    - Renomeie o arquivo `.env.example` para `.env`.
    - Abra o arquivo `.env` e insira sua chave da API do Google Gemini na variável `GEMINI_API_KEY`.

## Como Usar (CLI)

Execute o script `main.py` a partir do diretório `app` com os parâmetros desejados.

**Exemplo:**

```bash
python app/main.py --sistema "D&D 5e" --genero "Fantasia Sombria" --jogadores "4" --tempo "3-4 horas" --nivel "Nível 3" --output "minha_aventura.md"
```

Use `python app/main.py --help` para ver todas as opções disponíveis.

## GitHub Actions (CI/CD)

Este projeto está configurado para rodar no GitHub Actions!

### 1. Configuração de Secrets
Para que os workflows funcionem, você precisa adicionar sua chave da API como um Secret no repositório:
1. Vá em **Settings** > **Secrets and variables** > **Actions**.
2. Clique em **New repository secret**.
3. Nome: `GEMINI_API_KEY`
4. Valor: (Sua chave da API do Google Gemini)

### 2. Workflows Disponíveis

- **CI (Integração Contínua)**: Roda os testes automaticamente a cada `push` ou `pull_request` na branch `main`.
- **Gerar Aventura**: Execução manual para gerar one-shots na nuvem.
    1. Vá na aba **Actions**.
    2. Selecione o workflow **Gerar Aventura**.
    3. Clique em **Run workflow**.
    4. Escolha os parâmetros (Sistema, Gênero, Nível, etc.).
    5. Após a conclusão, baixe o arquivo `.zip` ou `.md` nos **Artifacts** da execução.
=======
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
>>>>>>> afd8acfc6d3a2623e8f607faadffcddecc9fcb9e
