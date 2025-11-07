
import os
import click
import google.generativeai as genai

# --- INSTRUÇÃO DE SISTEMA ---
# Define o comportamento e o papel da IA durante toda a sessão.
SYSTEM_INSTRUCTION = """
Você é um Assistente de Mestre de Jogo (GM) para RPGs de mesa. Sua especialidade é a criação colaborativa de aventuras no formato "one-shot".
Seu objetivo é ajudar o usuário a construir uma aventura coesa e interessante, passo a passo.
Responda em português do Brasil.
Use formatação Markdown para organizar o texto de forma clara (títulos, listas, negrito).
Para cada parte da aventura, seja criativo e detalhado, sempre mantendo a consistência com o que já foi estabelecido em nosso histórico de conversa.
"""

# --- PROMPTS PARA COMANDOS ---
# Mapeia o comando do usuário para um prompt claro para a IA.
COMMAND_PROMPTS = {
    "/setup": "Vamos alterar os parâmetros iniciais da aventura. Por favor, aguarde as novas instruções.",
    "/contexto": "Baseado em todo o nosso histórico de conversa até agora, gere o 'Contexto (Background)' e a 'Sinopse' para esta aventura.",
    "/ganchos": "Excelente. Agora, baseado em todo o histórico, gere os 'Ganchos da Trama' para iniciar a aventura.",
    "/personagens": "Ótimo. Agora, gere {num_jogadores} personagens de jogador prontos para esta aventura, no sistema {sistema} e nível {nivel_tier}. Para cada um, detalhe: Nome, Raça/Origem, Classe/Arquétipo, um Background conciso, Personalidade, um Objetivo Pessoal e sugestões de Atributos e Equipamentos iniciais.",
    "/npcs_principais": "Ótimo. Descreva agora os 'NPCs Principais', incluindo o vilão e possíveis aliados, conectando-os à história.",
    "/locais": "Descreva os 'Locais Importantes' onde a aventura se desenrolará, dando vida ao cenário.",
    "/desafios": "Com base na trama e nos locais, gere os 'Desafios', como combates, quebra-cabeças ou interações sociais.",
    "/ato1": "Perfeito. Com base no que estabelecemos, gere o 'Ato 1: A Introdução', onde os jogadores se envolvem com a trama.",
    "/ato2": "Continuando nossa história, gere o 'Ato 2: A Complicação', o núcleo da investigação ou exploração.",
    "/ato3": "Vamos avançar. Gere o 'Ato 3: O Ponto de Virada', um momento que muda a dinâmica da aventura.",
    "/ato4": "Estamos chegando ao clímax. Gere o 'Ato 4: O Clímax', o confronto final ou a resolução do conflito principal.",
    "/ato5": "Para finalizar, gere o 'Ato 5: A Resolução', descrevendo as consequências e o que acontece após o clímax.",
    "/resumo": "Por favor, gere um resumo conciso de toda a aventura que criamos até agora, organizando os pontos principais.",
    "/cenario": "Baseado nos locais e desafios, gere 3 prompts de texto para um gerador de imagens de IA criar mapas de batalha 2D, estilo top-down, para os encontros mais prováveis."
}

def _iniciar_modelo_e_chat(system_instruction):
    """Helper para configurar o modelo e iniciar o chat."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("A variável de ambiente GEMINI_API_KEY não foi definida.")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-2.5-pro",
        system_instruction=system_instruction
    )
    return model.start_chat(history=[])

def _enviar_setup_inicial(chat, **kwargs):
    """Envia a configuração inicial para a IA e já pede o primeiro passo."""
    setup_prompt = f'''
    Vamos começar a criar nossa aventura. Aqui estão os parâmetros iniciais:
    - Sistema de Jogo: {kwargs["sistema"]}
    - Gênero/Estilo: {kwargs["genero_estilo"]}
    - Número de Jogadores: {kwargs["num_jogadores"]}
    - Nível/Tier dos Personagens: {kwargs["nivel_tier"]}
    - Tempo Estimado de Jogo: {kwargs["tempo_estimado"]}

    Com base nisso, gere diretamente o 'Contexto (Background)' e a 'Sinopse' para uma aventura que se encaixe nesses parâmetros.
    '''
    response = chat.send_message(setup_prompt)
    return response.text

def gerar_aventura_completa(**kwargs):
    """Gera a aventura inteira em modo batch, executando todos os comandos em sequência."""
    output_file = kwargs.pop("output_file", None)
    gerar_personagens = kwargs.pop("gerar_personagens", False)

    try:
        chat = _iniciar_modelo_e_chat(SYSTEM_INSTRUCTION)
        click.echo(click.style("🤖 Iniciando geração em modo BATCH.", fg="green"))
        
        full_adventure_content = []

        # 1. Envia setup e já gera o contexto/sinopse
        click.echo(click.style("1. Gerando Contexto e Sinopse...", fg="cyan"))
        initial_response = _enviar_setup_inicial(chat, **kwargs)
        full_adventure_content.append(f"# Contexto e Sinopse\n\n{initial_response}\n\n---\n\n")
        click.echo(click.style("\n🤖 IA:", fg="yellow") + f" {initial_response}")

        # 2. Define a lista de comandos para execução automática
        comandos_para_executar = ["/ganchos"]
        if gerar_personagens:
            comandos_para_executar.append("/personagens")
        
        comandos_para_executar.extend([
            "/npcs_principais", "/locais", "/cenario", "/desafios", 
            "/ato1", "/ato2", "/ato3", "/ato4", "/ato5", "/resumo"
        ])

        # 3. Executa cada comando em sequência
        for i, comando in enumerate(comandos_para_executar, 2):
            # Formata o prompt se for para gerar personagens, para incluir detalhes dinâmicos
            if comando == "/personagens":
                prompt = COMMAND_PROMPTS[comando].format(
                    num_jogadores=kwargs.get('num_jogadores', 4),
                    sistema=kwargs.get('sistema', 'D&D 5e'),
                    nivel_tier=kwargs.get('nivel_tier', 'Nível 1')
                )
            else:
                prompt = COMMAND_PROMPTS[comando]

            click.echo(click.style(f"\n{i}. Executando {comando}...", fg="cyan"))
            response = chat.send_message(prompt)
            # Usa o nome do comando como título da seção
            titulo_secao = comando.replace('/', '').replace('_', ' ').title()
            full_adventure_content.append(f"## {titulo_secao}\n\n{response.text}\n\n---\n\n")
            click.echo(click.style("\n🤖 IA:", fg="yellow") + f" {response.text}")

        final_content = "".join(full_adventure_content)

        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(final_content)
                click.echo(click.style(f"\n\nGeração em lote concluída! Aventura salva em: {output_file}", fg="green", bold=True))
            except IOError as e:
                click.echo(click.style(f"Erro ao salvar o arquivo {output_file}: {e}", fg="red"))
        else:
            click.echo(click.style("\n\nGeração em lote concluída!", fg="green", bold=True))

    except (ValueError, Exception) as e:
        click.echo(click.style(f"Erro durante a geração em lote: {e}", fg="red"))

def iniciar_sessao_criativa(**kwargs):
    """
    Inicia e gerencia a sessão de criação de RPG interativa.
    """
    try:
        chat = _iniciar_modelo_e_chat(SYSTEM_INSTRUCTION)
        click.echo(click.style("🤖 Assistente de Criação de RPG iniciado. ", fg="green") + "Use /sair para terminar.")
        click.echo(click.style("Primeiro, vamos definir o setup da sua aventura...", fg="cyan"))

        initial_response = _enviar_setup_inicial(chat, **kwargs)
        click.echo(click.style("\n🤖 IA:", fg="yellow") + f" {initial_response}")

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
                click.echo(click.style("Atualizando setup com a IA...", fg="cyan"))
                response_text = _enviar_setup_inicial(chat, **kwargs)
                click.echo(click.style("\n🤖 IA:", fg="yellow") + f" {response_text}")
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
                    desc_personagem = click.prompt(click.style(f"\nDescreva o conceito do Personagem {i+1} (ex: 'elfo ladino arqueiro com um passado nobre')", fg="white"))
                    
                    prompt_personagem = f"""Baseado no conceito a seguir, gere um personagem de jogador para o sistema '{sistema}', no {nivel_tier}.
                    Conceito: '{desc_personagem}'.

                    Leve em conta o contexto da nossa aventura. Detalhe os seguintes pontos em formato Markdown:
                    - **Nome:** (e apelido, se aplicável)
                    - **Raça/Origem:**
                    - **Classe/Arquétipo:**
                    - **Background:** (Um parágrafo conciso sobre sua história e origem)
                    - **Personalidade:** (Sugira traços, ideais, vínculos e defeitos)
                    - **Objetivo Pessoal:** (O que este personagem busca alcançar na aventura?)
                    - **Atributos:** (Sugira os valores principais de atributos, ex: For 16, Dex 14, etc.)
                    - **Perícias & Equipamentos:** (Sugira 2-3 perícias principais e o equipamento inicial relevante)
                    """
                    
                    click.echo(click.style("Gerando personagem...", fg="cyan"))
                    response = chat.send_message(prompt_personagem)
                    click.echo(click.style(f"\n--- Personagem {i+1} Gerado ---", "yellow"))
                    click.echo(response.text)
                
                click.echo(click.style("\nCriação de personagens concluída!", "green", bold=True))

            except Exception as e:
                click.echo(click.style(f"\nErro durante a criação de personagens: {e}", "red"))
            continue


        # Lógica para todos os outros comandos
        prompt = COMMAND_PROMPTS.get(user_input.lower())
        if not prompt:
            click.echo(click.style("Comando inválido. Tente um dos comandos sugeridos.", fg="red"))
            continue

        try:
            click.echo(click.style("Gerando...", fg="cyan"))
            response = chat.send_message(prompt)
            click.echo(click.style("\n🤖 IA:", fg="yellow") + f" {response.text}")
        except Exception as e:
            click.echo(click.style(f"\nErro ao gerar conteúdo: {e}", fg="red"))
            continue
