import json
from pathlib import Path

def load_prompt_template(file_path: Path) -> str:
    """Carrega o template de prompt de um arquivo JSON."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data["PROMPT_TEMPLATE"]
    except FileNotFoundError:
        # Você pode querer um logging melhor ou um tratamento de erro aqui
        raise
    except KeyError:
        # Trata o caso de o JSON não ter a chave esperada
        raise ValueError(f"A chave 'PROMPT_TEMPLATE' não foi encontrada em {file_path}")

# O caminho para o arquivo JSON de prompts.
# Usamos Path para ser independente de sistema operacional.
PROMPTS_FILE = Path(__file__).parent / "prompts.json"

# Carrega o template no momento da importação do módulo.
PROMPT_TEMPLATE = load_prompt_template(PROMPTS_FILE)

