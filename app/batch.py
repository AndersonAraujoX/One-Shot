# app/batch.py

import click
import os
import zipfile
import tempfile
import shutil
import json
import yaml # Import PyYAML
from app.ai import COMMAND_PROMPTS, iniciar_modelo_e_chat, enviar_setup_inicial, CHARACTER_CREATION_PROMPTS, call_gemini_api, GeminiAPIError # Added call_gemini_api, GeminiAPIError

def gerar_aventura_completa(**kwargs):
    """Gera a aventura inteira em modo batch, executando todos os comandos em sequência."""
    output_file = kwargs.pop("output_file", None)
    output_format = kwargs.pop("output_format", "markdown") # New: Get output format
    gerar_personagens = kwargs.pop("gerar_personagens", False)
    zip_output = kwargs.pop("zip_output", False)

    try: # Start of try block for API errors
        model, chat = iniciar_modelo_e_chat() # Modified: receive both model and chat
        click.echo(click.style("🤖 Iniciando geração em modo BATCH.", fg="green"))
        
        adventure_data = {} # New: Structured data for the adventure
        markdown_content_parts = [] # For Markdown specific output

        # 1. Envia setup e já gera o contexto/sinopse
        click.echo(click.style("1. Gerando Contexto e Sinopse inicial...", fg="cyan"), nl=False)
        initial_response = enviar_setup_inicial(model, chat, **kwargs) # Modified: pass model
        click.echo(click.style(" Concluído.", fg="green"))
        adventure_data["contexto_sinopse"] = initial_response
        markdown_content_parts.append(f"# Contexto e Sinopse\n\n{initial_response}\n\n---\n\n")
        click.echo(click.style("\n🤖 IA:", fg="yellow") + f" {initial_response}")

        # 2. Define a lista de comandos para execução automática
        comandos_para_executar = ["ganchos"] # Changed to not include leading '/'
        if gerar_personagens:
            comandos_para_executar.append("personagens")
        
        comandos_para_executar.extend([
            "npcs_principais", "locais", "cenario", "desafios", 
            "ato1", "ato2", "ato3", "ato4", "ato5", "resumo"
        ])

        # 3. Executa cada comando em sequência
        for i, comando_key in enumerate(comandos_para_executar, 2):
            # Formata o prompt se for para gerar personagens, para incluir detalhes dinâmicos
            if comando_key == "personagens":
                prompt_text = COMMAND_PROMPTS[comando_key].format( # Access without leading '/'
                    num_jogadores=kwargs.get('num_jogadores', 4),
                    sistema=kwargs.get('sistema', 'D&D 5e'),
                    nivel_tier=kwargs.get('nivel_tier', 'Nível 1')
                )
            else:
                prompt_text = COMMAND_PROMPTS[comando_key] # Access without leading '/'

            click.echo(click.style(f"\n{i}. Gerando {comando_key.replace('_', ' ').title()}...", fg="cyan"), nl=False)
            response = call_gemini_api(chat.send_message, prompt_text) # Use call_gemini_api
            click.echo(click.style(" Concluído.", fg="green"))
            
            adventure_data[comando_key] = response.text # Store structured data
            
            # Uses the command key as section title for Markdown
            titulo_secao = comando_key.replace('_', ' ').title()
            markdown_content_parts.append(f"## {titulo_secao}\n\n{response.text}\n\n---\n\n")
            click.echo(click.style("\n🤖 IA:", fg="yellow") + f" {response.text}")

        final_output_content = ""
        output_ext = ""

        if output_format == "markdown":
            final_output_content = "".join(markdown_content_parts)
            output_ext = ".md"
        elif output_format == "json":
            final_output_content = json.dumps(adventure_data, indent=2, ensure_ascii=False)
            output_ext = ".json"
        elif output_format == "yaml":
            final_output_content = yaml.dump(adventure_data, allow_unicode=True, sort_keys=False)
            output_ext = ".yaml"


        if output_file:
            # Ensure correct file extension
            if not output_file.lower().endswith(output_ext):
                output_file = f"{output_file}{output_ext}"
            

            if zip_output:
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Salva o arquivo da aventura no formato correto no diretório temporário
                    adventure_path = os.path.join(temp_dir, f"aventura{output_ext}")
                    with open(adventure_path, 'w', encoding='utf-8') as f:
                        f.write(final_output_content)

                    # Move as imagens geradas para o diretório temporário
                    imagens_dir = "aventura_gerada/imagens"
                    if os.path.exists(imagens_dir):
                        shutil.move(imagens_dir, os.path.join(temp_dir, "imagens"))

                    # Cria o arquivo zip
                    zip_path = output_file if output_file.lower().endswith('.zip') else f"{output_file}.zip"
                    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        for root, _, files in os.walk(temp_dir):
                            for file in files:
                                arcname = os.path.relpath(os.path.join(root, file), temp_dir)
                                zipf.write(os.path.join(root, file), arcname)
                    click.echo(click.style(f"\n\nGeração em lote concluída! Aventura salva em: {zip_path}", fg="green", bold=True))

            else:
                try:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(final_output_content)
                    click.echo(click.style(f"\n\nGeração em lote concluída! Aventura salva em: {output_file}", fg="green", bold=True))
                except IOError as e:
                    click.echo(click.style(f"Erro ao salvar o arquivo {output_file}: {e}", fg="red"))
        else:
            click.echo(click.style("\n\nGeração em lote concluída! (Nenhum arquivo de saída especificado)", fg="green", bold=True))

    except GeminiAPIError as e: # Catch custom API errors
        click.echo(click.style(f"Erro na API Gemini durante a geração em lote: {e}", fg="red"))
    except Exception as e: # Catch other unexpected errors
        click.echo(click.style(f"Erro inesperado durante a geração em lote: {e}", fg="red"))
