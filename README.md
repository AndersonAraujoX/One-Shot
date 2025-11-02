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
