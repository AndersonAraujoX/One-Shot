# Memória do Projeto: Assistente de Criação de RPG (ATUALIZADO)

Este arquivo serve como um resumo de contexto para o assistente de IA (Gemini) que trabalha neste projeto. Ele contém as informações essenciais sobre a arquitetura, funcionalidade e estado atual do código.

---

### 1. Visão Geral do Projeto

O objetivo deste projeto é criar uma aplicação que auxilia um Mestre de Jogo (GM) a criar aventuras de RPG de forma colaborativa e passo a passo, através de um terminal.

A aplicação consiste em um backend em Python que utiliza a API do Google Gemini para a geração de conteúdo. A interação do usuário é feita através de uma Interface de Linha de Comando (CLI) rica, construída com as bibliotecas `click` e `rich`.

### 2. Arquitetura e Tecnologias

- **Linguagem:** Python
<<<<<<< HEAD
- **Interface:** CLI (Command-Line Interface) interativo, construído com a biblioteca `click`.
- **IA Generativa:** A integração é feita com a biblioteca `google-generativeai`, utilizando um modelo de chat como o `gemini-2.5-pro`.
- **Gerenciamento de Chaves:** A chave da API do Gemini é gerenciada através de um arquivo `.env` na raiz do projeto.
- **Módulo Principal:** A lógica está centralizada no diretório `app/`, principalmente nos arquivos `main.py` (ponto de entrada e CLI) e `ai.py` (lógica de conversação e geração, prompts, tratamento de erros, gerenciamento de contexto).
=======
- **IA Generativa:** `google-generativeai`
- **Interface de Terminal (CLI):** `click` para argumentos de linha de comando e `rich` para formatação de saída.
- **Módulos Principais:**
    - `backend/app/main.py`: Ponto de entrada da CLI, define os comandos e opções com `click`.
    - `backend/app/interactive.py`: Contém a lógica para o modo interativo e modo batch.
    - `backend/app/chat.py`: Gerencia a comunicação com a API do Gemini, histórico, geração de conteúdo e lógica de batch.
    - `backend/app/models.py`: Modelagem de dados com Pydantic (se aplicável, não diretamente visível nas últimas interações).
    - `backend/app/prompts.py`: Armazena os prompts base para a IA.
>>>>>>> afd8acfc6d3a2623e8f607faadffcddecc9fcb9e

### 3. Como Executar (Localmente)

#### a. Preparação do Ambiente

<<<<<<< HEAD
1.  **Modo Interativo (Padrão):**
    - O usuário inicia a aplicação com os parâmetros básicos da aventura (sistema, gênero, etc.).
    - A aplicação entra em um loop REPL (Read-Eval-Print Loop).
    - O usuário digita "comandos" (ex: `/contexto`, `/personagens`, `/cenario`) para gerar partes da aventura de forma iterativa.
    - O comando `/personagens` possui um sub-loop interativo para criar cada personagem individualmente.
    - **Melhoria UX**: Indicadores de progresso visuais foram adicionados para feedback em tempo real durante as chamadas à IA.
    - **Gerenciamento de Contexto**: A janela de contexto da IA é gerenciada automaticamente para evitar limites de tokens.

2.  **Modo Batch (`--batch`):**
    - A aplicação gera uma aventura completa e linear, sem interação do usuário.
    - Ela executa uma sequência pré-definida de comandos (contexto, ganchos, personagens, npcs, locais, cenario, desafios, atos, etc.).
    - A IA é instruída a escolher um caminho de história e desenvolvê-lo diretamente.
    - O resultado completo pode ser salvo em diferentes formatos (Markdown, JSON, YAML) se a opção `--output` for fornecida.
    - **Melhoria UX**: Indicadores de progresso visuais foram adicionados para feedback em tempo real durante as chamadas à IA.

### 4. Novas Funcionalidades e Melhorias Recentes

1.  **Gerenciamento de Prompts Externo**: Todos os prompts e instruções da IA foram externalizados para o arquivo `app/prompts.json`. Isso permite uma fácil edição, versionamento e experimentação com diferentes prompts sem modificar o código-fonte principal.
2.  **Opções de Saída Aprimoradas**: O modo batch (`--batch`) agora suporta a exportação da aventura gerada para três formatos:
    *   **Markdown (`.md`)**: Formato padrão, ideal para leitura e documentação.
    *   **JSON (`.json`)**: Formato estruturado, útil para integração com outras ferramentas ou processamento de dados.
    *   **YAML (`.yaml`)**: Outro formato estruturado, legível por humanos e ideal para configuração ou intercâmbio de dados.
    A seleção do formato é feita através da nova opção `--output-format` (markdown, json, yaml).
3.  **Tratamento de Erros Robusto na API**: Foi implementado um wrapper centralizado (`call_gemini_api` em `app/ai.py`) para todas as chamadas à API da IA. Este wrapper inclui:
    *   **Retentativas Automáticas**: Utiliza a biblioteca `tenacity` com backoff exponencial para lidar com erros transitórios (ex: problemas de rede, serviço temporariamente indisponível).
    *   **Gerenciamento de Limite de Taxa**: Detecta e tenta novamente automaticamente quando o limite de taxa da API é excedido (`ResourceExhausted`).
    *   **Mensagens de Erro Informativas**: Exceções customizadas (`GeminiAPIError`) fornecem feedback claro ao usuário em caso de falhas persistentes ou inesperadas.
4.  **Melhorias na Experiência do Usuário (UX) do CLI - Indicadores de Progresso**: Foram adicionados indicadores de progresso explícitos via `click.echo` em ambos os modos (batch e interativo). Mensagens como "Gerando X..." e "Concluído." fornecem feedback em tempo real sobre o status das operações da IA, melhorando a percepção de responsividade.
5.  **Gerenciamento da Janela de Contexto da IA**: Para garantir que as conversas longas não excedam o limite de tokens da IA (do modelo `gemini-2.5-pro`), uma estratégia de truncamento foi implementada em `app/ai.py` (`manage_chat_history`). Ela monitora o uso de tokens da história do chat e remove as mensagens mais antigas (em pares Usuário/Modelo) quando o limite (`MAX_CONTEXT_TOKENS`) é atingido, mantendo a consistência narrativa e otimizando o uso da API.

### 5. Como Executar
=======
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
>>>>>>> afd8acfc6d3a2623e8f607faadffcddecc9fcb9e

O comando base é: `python3 -m app.main [OPÇÕES]`

**Modos de Execução:**

**1. Modo Interativo (Um Comando por Vez):**
Inicia uma sessão interativa. Após a geração inicial, você pode inserir um comando por vez (ex: `/vilao`).

```bash
python3 -m app.main --sistema "D&D 5e" --genero "Fantasia" --jogadores 4 --nivel 5
```

**2. Modo Interativo (Múltiplos Comandos):**
Na mesma sessão interativa, você pode agora inserir múltiplos comandos de geração de uma vez, separados por espaço.

<<<<<<< HEAD
**Exemplo (Modo Batch com Geração de Personagens e Saída JSON):**
```bash
python -m app.main --sistema "D&D 5e" --genero "Fantasia Medieval" --jogadores 4 --nivel "Nível 3" --batch --personagens --output-format json --output "aventura_gerada.json"
=======
*Exemplo de entrada no prompt `>`:*
>>>>>>> afd8acfc6d3a2623e8f607faadffcddecc9fcb9e
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

### 6. Histórico e Versionamento

- O projeto é versionado com Git.
- O repositório remoto está em: `https://github.com/AndersonAraujoX/One-Shot.git`.
<<<<<<< HEAD
- O arquivo `.gitignore` está configurado para ignorar arquivos de ambiente (`.env`), cache do Python (`__pycache__`) e os arquivos de aventura gerados (`*.md`, `*.json`, `*.yaml`, `*.zip`), com exceção do `README.md`.
---
=======
- O arquivo `.gitignore` está configurado para ignorar arquivos de ambiente e caches.
>>>>>>> afd8acfc6d3a2623e8f607faadffcddecc9fcb9e
