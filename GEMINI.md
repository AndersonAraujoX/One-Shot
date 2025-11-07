# Memória do Projeto: Assistente de Criação de RPG

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
- **Módulo Principal:** A lógica está centralizada no diretório `app/`, principalmente nos arquivos `main.py` (ponto de entrada e CLI) e `chat.py` (lógica de conversação e geração).

### 3. Fluxos de Execução

O programa possui dois modos de operação principais, definidos no `app/main.py`:

1.  **Modo Interativo (Padrão):**
    - O usuário inicia a aplicação com os parâmetros básicos da aventura (sistema, gênero, etc.).
    - A aplicação entra em um loop REPL (Read-Eval-Print Loop).
    - O usuário digita "comandos" (ex: `/contexto`, `/personagens`, `/cenario`) para gerar partes da aventura de forma iterativa.
    - O comando `/personagens` possui um sub-loop interativo para criar cada personagem individualmente.

2.  **Modo Batch (`--batch`):
    - A aplicação gera uma aventura completa e linear, sem interação do usuário.
    - Ela executa uma sequência pré-definida de comandos (contexto, ganchos, personagens, npcs, locais, cenario, desafios, atos, etc.).
    - A IA é instruída a escolher um caminho de história e desenvolvê-lo diretamente.
    - O resultado completo é salvo em um arquivo Markdown se a opção `--output` for fornecida.

### 4. Como Executar

O ponto de entrada é o módulo `app.main`. A execução deve ser feita a partir do diretório raiz do projeto (`gerador-one-shot/`).

**Exemplo (Modo Interativo):**
```bash
python -m app.main --sistema "D&D 5e" --genero "Fantasia Medieval" --jogadores 4 --nivel "Nível 3"
```

Após o início, você pode usar comandos como `/contexto`, `/personagens`, e `/cenario`.

**Exemplo (Modo Batch com Geração de Personagens):**
```bash
python -m app.main --sistema "D&D 5e" --genero "Fantasia Medieval" --jogadores 4 --nivel "Nível 3" --batch --personagens --output "aventura_gerada.md"
```

### 5. Histórico e Versionamento

- O projeto é versionado com Git.
- O repositório remoto está em: `https://github.com/AndersonAraujoX/One-Shot.git`.
- O arquivo `.gitignore` está configurado para ignorar arquivos de ambiente (`.env`), cache do Python (`__pycache__`) e os arquivos de aventura gerados (`*.md`, `*.zip`), com exceção do `README.md`.
