# app/main.py

from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env ANTES de outras importações
load_dotenv()

import click
from app.generator import gerar_aventura

@click.command()
@click.option('--sistema', required=True, help='Sistema de regras (ex: "D&D 5e").')
@click.option('--genero', 'genero_estilo', required=True, help='Gênero da aventura (ex: "Terror Cósmico").')
@click.option('--jogadores', 'num_jogadores', required=True, help='Número de jogadores (ex: "4 jogadores").')
@click.option('--tempo', 'tempo_estimado', required=True, help='Duração estimada da sessão (ex: "3-4 horas").')
@click.option('--tom', 'tom_adicional', default="Nenhum", help='Tom adicional (ex: "Sombrio, Misterioso").')
@click.option('--nivel', 'nivel_tier', default="Não especificado", help='Nível ou tier dos personagens (ex: "Nível 5").')
@click.option('--output', 'output_file', help='(Opcional) Arquivo para salvar a aventura gerada.')
def cli(sistema, genero_estilo, num_jogadores, tempo_estimado, tom_adicional, nivel_tier, output_file):
    """
    Gerador de One-Shots de RPG usando IA Generativa.
    """
    click.echo("Iniciando a geração da sua aventura one-shot...")
    
    aventura_markdown = gerar_aventura(
        sistema=sistema,
        genero_estilo=genero_estilo,
        num_jogadores=num_jogadores,
        tempo_estimado=tempo_estimado,
        tom_adicional=tom_adicional,
        nivel_tier=nivel_tier
    )
    
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(aventura_markdown)
            click.echo(f"Aventura salva com sucesso em: {output_file}")
        except IOError as e:
            click.echo(f"Erro ao salvar o arquivo: {e}", err=True)
    else:
        # Imprime o resultado no console com uma separação clara
        click.echo("\n" + "="*80)
        click.echo("AVENTURA GERADA")
        click.echo("="*80 + "\n")
        click.echo(aventura_markdown)

if __name__ == '__main__':
    cli()
