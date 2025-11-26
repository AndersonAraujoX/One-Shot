# Memória do Projeto: Assistente de Criação de RPG

Este arquivo serve como um resumo de contexto para o assistente de IA (Gemini) que trabalha neste projeto. Ele contém as informações essenciais sobre a arquitetura, funcionalidade e estado atual do código.

---

### 1. Visão Geral do Projeto

O objetivo deste projeto é criar uma aplicação que auxilia um Mestre de Jogo (GM) a criar aventuras de RPG de forma colaborativa e passo a passo, através de um terminal.

A aplicação consiste em um backend em Python que utiliza a API do Google Gemini para a geração de conteúdo. A interação do usuário é feita através de uma Interface de Linha de Comando (CLI) rica, construída com as bibliotecas `click` e `rich`.

### 2. Arquitetura e Tecnologias

- **Linguagem:** Python
- **IA Generativa:** `google-generativeai`
- **Interface de Terminal (CLI):** `click` para argumentos de linha de comando e `rich` para formatação de saída.
- **Módulos Principais:**
    - `backend/app/main.py`: Ponto de entrada da CLI, define os comandos e opções com `click`.
    - `backend/app/interactive.py`: Contém a lógica para o modo interativo e modo batch.
    - `backend/app/chat.py`: Gerencia a comunicação com a API do Gemini, histórico, geração de conteúdo e lógica de batch.
    - `backend/app/models.py`: Modelagem de dados com Pydantic (se aplicável, não diretamente visível nas últimas interações).
    - `backend/app/prompts.py`: Armazena os prompts base para a IA.

### 3. Como Executar (Localmente)

#### a. Preparação do Ambiente

1.  A partir da pasta raiz do projeto, navegue até o diretório do backend:
    ```bash
    cd backend
    ```
2.  Instale as dependências necessárias:
    ```bash
    pip install -r requirements.txt
    ```
3.  Crie um arquivo chamado `.env` nesta pasta (`backend/`) e adicione sua chave de API:
    ```
    GEMINI_API_KEY="sua_chave_de_api_aqui"
    ```

#### b. Execução da CLI

Para evitar erros de importação (`ModuleNotFoundError`), o script deve ser executado como um módulo Python a partir da pasta `backend`.

O comando base é: `python3 -m app.main [OPÇÕES]`

**Modos de Execução:**

**1. Modo Interativo (Um Comando por Vez):**
Inicia uma sessão interativa. Após a geração inicial, você pode inserir um comando por vez (ex: `/vilao`).

```bash
python3 -m app.main --sistema "D&D 5e" --genero "Fantasia" --jogadores 4 --nivel 5
```

**2. Modo Interativo (Múltiplos Comandos):**
Na mesma sessão interativa, você pode agora inserir múltiplos comandos de geração de uma vez, separados por espaço.

*Exemplo de entrada no prompt `>`:*
```
/ganchos /locais_importantes /npcs
```

**3. Modo Batch (Aventura Completa):**
Gera uma aventura completa com todas as seções pré-definidas e a salva em um arquivo.

```bash
python3 -m app.main --sistema "D&D 5e" --genero "Fantasia" --jogadores 4 --nivel 5 --batch --output aventura_completa.md
```

**4. Modo Batch (Seções Customizadas):**
Gera apenas as seções que você especificar, usando a flag `--secoes`.

```bash
python3 -m app.main --sistema "D&D 5e" --genero "Fantasia" --jogadores 4 --nivel 5 --batch --secoes "contexto ganchos personagens_chave"
```

### 4. Melhorias Recentes

- **Múltiplos Comandos:** O modo interativo agora suporta a inserção de vários comandos de geração de uma vez.
- **Batch Customizável:** Adicionada a flag `--secoes` para permitir que o usuário escolha quais partes da aventura gerar no modo batch.
- **Robustez na Análise de JSON:** O sistema de processamento de respostas da IA foi aprimorado para extrair JSON de forma mais confiável, mesmo quando ele está dentro de blocos de código Markdown.
- **Correções de Bugs:**
    - Resolvido um `ModuleNotFoundError` ao instruir a execução via `python3 -m app.main`.
    - Corrigido um erro de importação no comando `/carregar` no modo interativo.

### 5. Histórico e Versionamento

- O projeto é versionado com Git.
- O repositório remoto está em: `https://github.com/AndersonAraujoX/One-Shot.git`.
- O arquivo `.gitignore` está configurado para ignorar arquivos de ambiente e caches.
