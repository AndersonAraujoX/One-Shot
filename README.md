# Gerador de One-Shots de RPG

Este projeto utiliza IA Generativa para criar aventuras de RPG "one-shot" prontas para jogar.

## Configuração

1.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
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