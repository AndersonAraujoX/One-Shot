# Memória do Projeto: Assistente de Criação de RPG (ATUALIZADO)

Este arquivo serve como um resumo de contexto para o assistente de IA (Gemini) que trabalha neste projeto. Ele contém as informações essenciais sobre a arquitetura, funcionalidade e estado atual do código.

---

### 1. Visão Geral do Projeto

O objetivo deste projeto é criar uma aplicação em Python chamada **"Assistente de Criação de RPG"**. A aplicação funciona como um CLI interativo que auxilia um Mestre de Jogo (GM) a criar aventuras de RPG de forma colaborativa e passo a passo.

A arquitetura é **conversacional**. A aplicação mantém um histórico de chat com a IA (usando o `google-generativeai`) para garantir que cada parte da aventura (atos, NPCs, etc.) seja gerada com consistência narrativa, baseando-se no que já foi criado.

### 2. Arquitetura e Tecnologias

- **Linguagem:** Python
- **Interface:** CLI (Command-Line Interface) interativo, construído com a biblioteca `click`.
- **IA Generativa:** A integração é feita com a biblioteca `google-generativeai`, utilizando um modelo de chat como o `gemini-2.5-pro`.
- **Gerenciamento de Chaves:** A chave da API do Gemini é gerenciada através de um arquivo `.env` na raiz do projeto.
- **Módulo Principal:** A lógica está centralizada no diretório `app/`, principalmente nos arquivos `main.py` (ponto de entrada e CLI) e `ai.py` (lógica de conversação e geração, prompts, tratamento de erros, gerenciamento de contexto).

### 3. Fluxos de Execução

O programa possui dois modos de operação principais, definidos no `app/main.py`:

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

O ponto de entrada é o módulo `app.main`. A execução deve ser feita a partir do diretório raiz do projeto (`gerador-one-shot/`).

**Exemplo (Modo Interativo):**
```bash
python -m app.main --sistema "D&D 5e" --genero "Fantasia Medieval" --jogadores 4 --nivel "Nível 3"
```

Após o início, você pode usar comandos como `/contexto`, `/personagens`, e `/cenario`.

**Exemplo (Modo Batch com Geração de Personagens e Saída JSON):**
```bash
python -m app.main --sistema "D&D 5e" --genero "Fantasia Medieval" --jogadores 4 --nivel "Nível 3" --batch --personagens --output-format json --output "aventura_gerada.json"
```

### 6. Histórico e Versionamento

- O projeto é versionado com Git.
- O repositório remoto está em: `https://github.com/AndersonAraujoX/One-Shot.git`.
- O arquivo `.gitignore` está configurado para ignorar arquivos de ambiente (`.env`), cache do Python (`__pycache__`) e os arquivos de aventura gerados (`*.md`, `*.json`, `*.yaml`, `*.zip`), com exceção do `README.md`.
---