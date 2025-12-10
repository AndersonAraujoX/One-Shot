#!/bin/bash

# Script para rodar o One-Shot RPG localmente (sem Docker)

echo "--- Verificando dependências ---"

if ! command -v python3 &> /dev/null; then
    echo "Erro: Python 3 não encontrado."
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "Erro: npm não encontrado."
    exit 1
fi

echo "--- Configurando Backend ---"
# Cria venv se não existir
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    if ! python3 -m venv venv; then
        echo "python3-venv falhou. Tentando com virtualenv..."
        # Tenta instalar virtualenv se não existir
        if ! command -v virtualenv &> /dev/null; then
             pip install --user virtualenv
             export PATH=$PATH:$HOME/.local/bin
        fi
        virtualenv venv
    fi
fi

source venv/bin/activate

echo "Instalando dependências Python..."
pip install -r backend/requirements.txt

# Garante que o diretório static existe
mkdir -p backend/static/generated_images

echo "--- Configurando Frontend ---"
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Instalando dependências Node..."
    npm install
fi
cd ..

echo "--- Limpando processos anteriores ---"
fuser -k 8000/tcp 3000/tcp > /dev/null 2>&1

echo "--- Iniciando Aplicação ---"
echo "Backend rodando em: http://localhost:8000"
echo "Frontend rodando em: http://localhost:3000"
echo "Pressione Ctrl+C para parar."

# Função de limpeza ao sair
cleanup() {
    echo "Parando processos..."
    kill $(jobs -p) 2>/dev/null
    exit
}
trap cleanup SIGINT SIGTERM

# Roda backend em background
source venv/bin/activate
uvicorn backend.app.api:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Espera o backend estar pronto
echo "Aguardando Backend iniciar..."
while ! curl -s http://localhost:8000/docs > /dev/null; do
    sleep 1
done
echo "Backend iniciado!"

# Roda frontend
cd frontend
npm start
