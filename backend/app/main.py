# app/main.py

from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env ANTES de outras importações
load_dotenv()

import click
from app.interactive import iniciar_sessao_criativa, gerar_aventura_completa

@click.command()
# Parâmetros para definir a base da aventura
@click.option('--sistema', required=True, help='Sistema de regras (ex: "D&D 5e", "Pathfinder 2e").')
@click.option('--genero', 'genero_estilo', required=True, help='Gênero da aventura (ex: "Fantasia Sombria", "Sci-Fi").')
@click.option('--jogadores', 'num_jogadores', type=int, required=True, help='Número de jogadores.')
@click.option('--nivel', 'nivel_tier', required=True, help='Nível ou tier dos personagens (ex: "Nível 5").')
@click.option('--tempo', 'tempo_estimado', default="3-4 horas", show_default=True, help='Duração estimada da sessão.')

# Flags para controlar o modo de execução
@click.option('--batch', 'modo_batch', is_flag=True, help='Ativa o modo de geração completa sem interação.')
@click.option('--personagens', 'gerar_personagens', is_flag=True, help='(Modo Batch) Inclui a geração de personagens na aventura completa.')
@click.option('--formato', type=click.Choice(['markdown', 'json', 'yaml'], case_sensitive=False), default='markdown', show_default=True, help='Formato do arquivo de saída.')
@click.option('--output', 'output_file', help='(Modo Batch) Arquivo para salvar a aventura completa.')
@click.option('--secoes', help='(Modo Batch) Lista de seções para gerar, separadas por espaço (ex: "contexto ganchos vilao").')

def cli(sistema, genero_estilo, num_jogadores, nivel_tier, tempo_estimado, modo_batch, gerar_personagens, formato, output_file, secoes):
    """
    Assistente de Criação de RPG: uma ferramenta para gerar one-shots de forma colaborativa ou automática.
    """
    # Agrupa os parâmetros em um dicionário para facilitar o envio
    config = {
        "sistema": sistema,
        "genero_estilo": genero_estilo,
        "num_jogadores": num_jogadores,
        "nivel_tier": nivel_tier,
        "tempo_estimado": tempo_estimado,
    }

    if modo_batch:
        # Adiciona as opções específicas do modo batch ao dicionário de configuração
        config["output_file"] = output_file
        config["gerar_personagens"] = gerar_personagens
        config["formato"] = formato
        if secoes:
            config["secoes"] = secoes.split()
        
        gerar_aventura_completa(**config)
    else:
        # Inicia a sessão interativa padrão
        iniciar_sessao_criativa(**config)

if __name__ == '__main__':
    cli()