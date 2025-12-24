# app/interactive.py

import click
import os
from PIL import Image
from app.ai import COMMAND_PROMPTS, iniciar_modelo_e_chat, enviar_setup_inicial, gerar_e_salvar_imagem, CHARACTER_CREATION_PROMPTS, call_gemini_api, GeminiAPIError

def iniciar_sessao_criativa(**kwargs):
    """
    Inicia e gerencia a sessão de criação de RPG interativa.
    """
    try:
        model, chat = iniciar_modelo_e_chat() # Modified: receive both model and chat
        click.echo(click.style("🤖 Assistente de Criação de RPG iniciado. ", fg="green") + "Use /sair para terminar.")
        click.echo(click.style("Primeiro, vamos definir o setup da sua aventura...", fg="cyan"), nl=False)

        initial_response = enviar_setup_inicial(model, chat, **kwargs) # Modified: pass model
        click.echo(click.style(" Concluído.", fg="green"))
        click.echo(click.style("\n🤖 IA:", fg="yellow") + f" {initial_response}")

    except GeminiAPIError as e:
        click.echo(click.style(f"Erro na API Gemini ao iniciar a sessão: {e}", fg="red"))
        return
    except (ValueError, Exception) as e:
        click.echo(click.style(f"Erro ao iniciar a sessão: {e}", fg="red"))
        return

    # Loop principal (REPL) que aguarda os comandos do usuário
    while True:
        comandos_disponiveis = ', '.join(COMMAND_PROMPTS.keys())
        click.echo(click.style(f"\nSeus comandos: {comandos_disponiveis}, /sair", fg="magenta"))
        user_input = click.prompt(click.style(">", fg="white"))

        if user_input.lower() == "/sair":
            click.echo(click.style("Sessão terminada. Boa sorte com sua aventura!", fg="green"))
            break
        
        if user_input.lower() == "/setup":
            click.echo(click.style("Modo de setup: Forneça os novos parâmetros.", fg="cyan"))
            # Armazena os novos kwargs na variável da sessão
            kwargs = {
                "sistema": click.prompt("Novo Sistema", default=kwargs.get('sistema')),
                "genero_estilo": click.prompt("Novo Gênero/Estilo", default=kwargs.get('genero_estilo')),
                "num_jogadores": click.prompt("Novo N° de Jogadores", type=int, default=kwargs.get('num_jogadores')),
                "nivel_tier": click.prompt("Novo Nível/Tier", default=kwargs.get('nivel_tier')),
                "tempo_estimado": click.prompt("Novo Tempo Estimado", default=kwargs.get('tempo_estimado'))
            }
            try:
                click.echo(click.style("Atualizando setup com a IA...", fg="cyan"), nl=False)
                response_text = enviar_setup_inicial(model, chat, **kwargs) # Modified: pass model
                click.echo(click.style(" Concluído.", fg="green"))
                click.echo(click.style("\n🤖 IA:", fg="yellow") + f" {response_text}")
            except GeminiAPIError as e:
                click.echo(click.style(f"\nErro na API Gemini ao atualizar o setup: {e}", fg="red"))
            except Exception as e:
                click.echo(click.style(f"\nErro ao atualizar o setup: {e}", fg="red"))
            continue

        if user_input.lower() == "/personagens":
            try:
                num_jogadores = kwargs.get("num_jogadores", 1)
                nivel_tier = kwargs.get("nivel_tier", "Nível 1")
                sistema = kwargs.get("sistema", "D&D 5e")
                click.echo(click.style(f"Iniciando criação interativa de {num_jogadores} personagem(ns) para {sistema} {nivel_tier}.", fg="cyan"))

                for i in range(num_jogadores):
                    click.echo(click.style(f"\n--- Criando Personagem {i+1}/{num_jogadores} ---", "yellow", bold=True))

                    # 1. Conceito
                    conceito = click.prompt(click.style(f"Descreva o conceito do Personagem {i+1} (ex: 'elfo ladino arqueiro com um passado nobre')", fg="white"))

                    # 2. Informações Básicas (Nome, Raça, Classe)
                    prompt_base = CHARACTER_CREATION_PROMPTS["base"].format(conceito=conceito, sistema=sistema, nivel_tier=nivel_tier)
                    click.echo(click.style("Gerando informações básicas...", fg="cyan"), nl=False)
                    response_base = call_gemini_api(chat.send_message, prompt_base)
                    click.echo(click.style(" Concluído.", fg="green"))
                    click.echo(click.style("\nSugestão da IA:", "yellow"))
                    click.echo(response_base.text)
                    if not click.confirm(click.style('Aceita esta sugestão?', fg='green'), default=True):
                        nome = click.prompt("Nome", default=response_base.text.split('\n')[0].split(': ')[1])
                        raca = click.prompt("Raça", default=response_base.text.split('\n')[1].split(': ')[1])
                        classe = click.prompt("Classe", default=response_base.text.split('\n')[2].split(': ')[1])
                    else:
                        nome = response_base.text.split('\n')[0].split(': ')[1]
                        raca = response_base.text.split('\n')[1].split(': ')[1]
                        classe = response_base.text.split('\n')[2].split(': ')[1]

                    personagem_atual = f"**Nome:** {nome}\n**Raça:** {raca}\n**Classe:** {classe}\n"
                    click.echo(click.style("\nPersonagem até agora:", "magenta") + f"\n{personagem_atual}")

                    # 3. Background
                    prompt_background = CHARACTER_CREATION_PROMPTS["background"].format(raca=raca, classe=classe, nome=nome, conceito=conceito)
                    click.echo(click.style("Gerando background...", fg="cyan"), nl=False)
                    response_bg = call_gemini_api(chat.send_message, prompt_background)
                    click.echo(click.style(" Concluído.", fg="green"))
                    click.echo(click.style("\nSugestão de Background:", "yellow"))
                    click.echo(response_bg.text)
                    if click.confirm(click.style('Aceita esta sugestão?', fg='green'), default=True):
                        background = response_bg.text
                    else:
                        background = click.edit(response_bg.text)
                    
                    personagem_atual += f"**Background:** {background}\n"
                    click.echo(click.style("\nPersonagem até agora:", "magenta") + f"\n{personagem_atual}")
                    
                    # 4. Personalidade e Objetivos
                    prompt_personalidade = CHARACTER_CREATION_PROMPTS["personality"].format(nome=nome, raca=raca, classe=classe, background=background)
                    click.echo(click.style("Gerando personalidade e objetivos...", fg="cyan"), nl=False)
                    response_pers = call_gemini_api(chat.send_message, prompt_personalidade)
                    click.echo(click.style(" Concluído.", fg="green"))
                    click.echo(click.style("\nSugestão de Personalidade e Objetivos:", "yellow"))
                    click.echo(response_pers.text)
                    if click.confirm(click.style('Aceita esta sugestão?', fg='green'), default=True):
                        personalidade_objetivos = response_pers.text
                    else:
                        personalidade_objetivos = click.edit(response_pers.text)

                    personagem_atual += f"{personalidade_objetivos}\n"
                    click.echo(click.style("\nPersonagem até agora:", "magenta") + f"\n{personagem_atual}")

                    # 5. Atributos e Equipamentos
                    prompt_final = CHARACTER_CREATION_PROMPTS["final"].format(raca=raca, classe=classe, nivel_tier=nivel_tier, nome=nome, sistema=sistema)
                    click.echo(click.style("Gerando atributos e equipamentos...", fg="cyan"), nl=False)
                    response_final = call_gemini_api(chat.send_message, prompt_final)
                    click.echo(click.style(" Concluído.", fg="green"))
                    click.echo(click.style("\nSugestão de Atributos e Equipamentos:", "yellow"))
                    click.echo(response_final.text)
                    if click.confirm(click.style('Aceita esta sugestão?', fg='green'), default=True):
                        atributos_equipamentos = response_final.text
                    else:
                        atributos_equipamentos = click.edit(response_final.text)
                        
                    personagem_atual += f"{atributos_equipamentos}\n"

                    # Exibe o personagem completo
                    click.echo(click.style(f"\n--- Personagem {i+1} Concluído ---", "green", bold=True))
                    click.echo(personagem_atual)
                    # Envia o personagem completo para o histórico do chat
                    call_gemini_api(chat.send_message, CHARACTER_CREATION_PROMPTS["acknowledgement"].format(personagem_atual=personagem_atual))


                click.echo(click.style("\nCriação de personagens concluída!", "green", bold=True))

            except GeminiAPIError as e:
                click.echo(click.style(f"\nErro na API Gemini durante a criação de personagens: {e}", "red"))
            except Exception as e:
                click.echo(click.style(f"\nErro durante a criação de personagens: {e}", "red"))
            continue


        if user_input.lower() == "/imagem":
            try:
                descricao_imagem = click.prompt(click.style("Descreva a imagem que você quer gerar", fg="white"))
                click.echo(click.style("Gerando imagem...", fg="cyan"), nl=False)
                caminho_imagem = gerar_e_salvar_imagem(descricao_imagem)
                click.echo(click.style(" Concluído.", fg="green"))
                click.echo(click.style(f"Imagem salva em: {caminho_imagem}", fg="green", bold=True))
            except GeminiAPIError as e:
                click.echo(click.style(f"\nErro na API Gemini durante a geração de imagem: {e}", "red"))
            except Exception as e:
                click.echo(click.style(f"\nErro durante a geração de imagem: {e}", "red"))
            continue

        # Lógica para todos os outros comandos
        prompt = COMMAND_PROMPTS.get(user_input.lower())
        if not prompt:
            click.echo(click.style("Comando inválido. Tente um dos comandos sugeridos.", fg="red"))
            continue

        try:
            click.echo(click.style("Gerando...", fg="cyan"), nl=False)
            response = call_gemini_api(chat.send_message, prompt)
            click.echo(click.style(" Concluído.", fg="green"))
            click.echo(click.style("\n🤖 IA:", fg="yellow") + f" {response.text}")
        except GeminiAPIError as e:
            click.echo(click.style(f"\nErro na API Gemini ao gerar conteúdo: {e}", fg="red"))
        except Exception as e:
            click.echo(click.style(f"\nErro ao gerar conteúdo: {e}", fg="red"))
            continue
