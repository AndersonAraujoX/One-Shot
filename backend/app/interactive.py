# app/interactive.py


import json
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
from google.generativeai import types

from app.chat import iniciar_chat, enviar_mensagem, COMMAND_PROMPTS, ContentGenerationError, gerar_aventura_batch

# Inicializa o console do Rich
console = Console()

def _formatar_saida(data: dict, formato: str) -> str:
    """Formata os dados da aventura para o formato de saída desejado."""
    if formato == 'json':
        return json.dumps(data, indent=2, ensure_ascii=False)
    elif formato == 'yaml':
        return yaml.dump(data, allow_unicode=True, sort_keys=False)
    else:  # Markdown (padrão)
        markdown_parts = []
        for secao, conteudo in data.items():
            secao_formatada = secao.replace('_', ' ').title()
            markdown_parts.append(f"## {secao_formatada}\n\n{conteudo}\n\n---\n\n")
        return "".join(markdown_parts)

def _gerar_conteudo_com_spinner(chat, prompt: str, painel_titulo: str) -> str:
    """Exibe um spinner enquanto gera conteúdo e retorna o resultado."""
    with Live(Spinner("dots", text=Text("Gerando...", style="cyan")), console=console) as live:
        try:
            response_text = enviar_mensagem(chat, prompt)
            live.stop()
            return response_text
        except ContentGenerationError as e:
            live.stop()
            console.print(Panel(f"Erro ao gerar conteúdo: {e}", title="[bold red]Erro[/bold red]", border_style="red"))
            return ""
        except Exception as e:
            live.stop()
            console.print(Panel(f"Ocorreu um erro inesperado: {e}", title="[bold red]Erro Inesperado[/bold red]", border_style="red"))
            return ""

def iniciar_sessao_criativa(**kwargs):
    """
    Inicia e gerencia a sessão de criação de RPG interativa com Rich.
    """
    try:
        chat = iniciar_chat()
        console.print(Panel("[bold green]🤖 Assistente de Criação de RPG iniciado.[/bold green] Use [cyan]/sair[/cyan] para terminar.", title="Bem-vindo!", border_style="green"))
        console.print(Panel("Primeiro, vamos definir o setup da sua aventura...", title="[bold cyan]Setup Inicial[/bold cyan]", border_style="cyan"))

        setup_prompt = f'''
        Vamos começar a criar nossa aventura. Aqui estão os parâmetros iniciais:
        - Sistema de Jogo: {kwargs["sistema"]} 
        - Gênero/Estilo: {kwargs["genero_estilo"]} 
        - Número de Jogadores: {kwargs["num_jogadores"]} 
        - Nível/Tier dos Personagens: {kwargs["nivel_tier"]} 
        - Tempo Estimado de Jogo: {kwargs["tempo_estimado"]} 

        Com base nisso, gere diretamente o 'Contexto (Background)' e a 'Sinopse' para uma aventura que se encaixe nesses parâmetros.
        '''
        
        response_text = _gerar_conteudo_com_spinner(chat, setup_prompt, "Contexto e Sinopse")
        if response_text:
            console.print(Panel(response_text, title="[bold yellow]🤖 IA Responde[/bold yellow]", border_style="yellow"))

    except (ValueError, ContentGenerationError) as e:
        console.print(Panel(f"Erro: {e}", title="[bold red]Erro na Sessão[/bold red]", border_style="red"))
        return
    except Exception as e:
        console.print(Panel(f"Ocorreu um erro inesperado: {e}", title="[bold red]Erro Crítico[/bold red]", border_style="red"))
        return

    # Loop principal (REPL)
    while True:
        comandos_str = ", ".join(f"[cyan]/{cmd}[/cyan]" for cmd in COMMAND_PROMPTS.keys())
        console.print(f"\n[magenta]Seus comandos:[/magenta] {comandos_str}, /sair")
        console.print("Você pode digitar múltiplos comandos de geração separados por espaço (ex: /vilao /locais).")
        user_input = Prompt.ask("[bold white]>[/bold white]")

        commands_to_run = user_input.strip().split()
        
        should_exit = False
        for i, command_full in enumerate(commands_to_run):
            
            # Tratamento especial para /regenerar, que contém um argumento
            if command_full.lower().startswith("regenerar"):
                # Pega o resto da string a partir do comando regenerar
                regenerate_part = " ".join(commands_to_run[i:])
                command_name = "regenerar"
                args = regenerate_part.split(" ", 1)[1] if " " in regenerate_part else ""
            else:
                command_name = command_full.lower().lstrip('/')
                args = ""

            if command_name == "sair":
                should_exit = True
                break
            
            if command_name == "salvar":
                filename = Prompt.ask("Digite o nome do arquivo para salvar a sessão", default="sessao_aventura.json")
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        history_to_save = [{"role": msg.role, "parts": [part.text for part in msg.parts]} for msg in chat.history]
                        json.dump(history_to_save, f, ensure_ascii=False, indent=2)
                    console.print(Panel(f"Sessão salva com sucesso em [bold green]{filename}[/bold green]!", title="Salvo!"))
                except Exception as e:
                    console.print(Panel(f"Erro ao salvar a sessão: {e}", title="[bold red]Erro[/bold red]"))
                continue

            if command_name == "carregar":
                filename = Prompt.ask("Digite o nome do arquivo para carregar a sessão", default="sessao_aventura.json")
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        history_loaded = json.load(f)
                    
                    chat = iniciar_chat()
                    chat.history = [types.Content(parts=[types.Part.from_text(part['text']) for part in msg['parts']], role=msg['role']) for msg in history_loaded]

                    console.print(Panel(f"Sessão carregada com sucesso de [bold green]{filename}[/bold green]!", title="Carregado!"))
                    console.print(Panel(chat.history[-1].parts[0].text, title="[bold yellow]🤖 Última Mensagem da IA[/bold yellow]", border_style="yellow"))
                except FileNotFoundError:
                    console.print(Panel(f"Arquivo '{filename}' não encontrado.", title="[bold red]Erro[/bold red]"))
                except Exception as e:
                    console.print(Panel(f"Erro ao carregar a sessão: {e}", title="[bold red]Erro[/bold red]"))
                # Interrompe o processamento de outros comandos na linha, pois o chat foi substituído
                break

            if command_name == "regenerar":
                if args:
                    secao = args
                    prompt_info = COMMAND_PROMPTS["regenerar"]
                    prompt = prompt_info["prompt"].format(secao=secao)
                    titulo_painel = f"Regenerando: {secao.title()}"
                    response_text = _gerar_conteudo_com_spinner(chat, prompt, titulo_painel)
                    if response_text:
                        console.print(Panel(response_text, title=f"[bold yellow]🤖 {titulo_painel}[/bold yellow]", border_style="yellow"))
                else:
                    console.print("[bold red]Uso: /regenerar [nome da seção][/bold red] (ex: /regenerar vilao)")
                # Como /regenerar consome o resto da linha, paramos aqui.
                break

            prompt_info = COMMAND_PROMPTS.get(command_name)
            if not prompt_info:
                console.print(f"[bold red]Comando '{command_name}' inválido.[/bold red]")
                continue
                
            titulo_painel = command_name.replace('_', ' ').title()
            response_text = _gerar_conteudo_com_spinner(chat, prompt_info['prompt'], titulo_painel)
            
            if response_text:
                console.print(Panel(response_text, title=f"[bold yellow]🤖 {titulo_painel}[/bold yellow]", border_style="yellow"))
        
        if should_exit:
            console.print(Panel("Sessão terminada. [bold green]Boa sorte com sua aventura![/bold green]", title="Até logo!", border_style="green"))
            break


def gerar_aventura_completa(**kwargs):
    """Gera a aventura inteira em modo batch, com suporte a múltiplos formatos e feedback visual."""
    output_file = kwargs.pop("output_file", None)
    formato = kwargs.pop("formato", "markdown")

    try:
        console.print(Panel("[bold green]🤖 Iniciando geração em modo BATCH.[/bold green]", border_style="green"))
        
        with Live(Spinner("dots", text=Text("Gerando aventura completa...", style="cyan")), console=console) as live:
            adventure_data = gerar_aventura_batch(**kwargs)
        
        final_content = _formatar_saida(adventure_data, formato)

        if output_file:
            try:
                if not output_file.endswith(f'.{formato}'):
                    output_file += f'.{formato}'
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(final_content)
                console.print(Panel(f"Geração concluída! Aventura salva em: [bold green]{output_file}[/bold green]", title="Sucesso!", border_style="green"))
            except IOError as e:
                console.print(Panel(f"Erro ao salvar o arquivo {output_file}: {e}", title="[bold red]Erro de Arquivo[/bold red]", border_style="red"))
        else:
            console.print(Panel("Geração em lote concluída!", title="Sucesso!", border_style="green"))
            console.print("\n--- CONTEÚDO GERADO ---\n")
            console.print(final_content)

    except (ValueError, ContentGenerationError) as e:
        console.print(Panel(f"Erro: {e}", title="[bold red]Erro na Geração[/bold red]", border_style="red"))
    except Exception as e:
        console.print(Panel(f"Ocorreu um erro inesperado: {e}", title="[bold red]Erro Crítico[/bold red]", border_style="red"))

