// src/App.js
import React, { useState } from 'react';
import axios from 'axios';
import AdventureForm from './components/AdventureForm';
import Chat from './components/Chat';
import AdventureView from './components/AdventureView';
import './App.css';

const isDemoMode = window.location.hostname !== 'localhost';

const mockAdventure = {
  titulo: "A Tumba do Terror Rastejante (DEMO)",
  sinopse: "Uma antiga tumba foi descoberta, mas um mal rastejante guarda seus segredos. Esta é uma demonstração estática.",
  personagens_chave: [
    { nome: "Elara", aparencia: "Uma exploradora com olhos curiosos.", url_imagem: "https://i.imgur.com/tG3aL6G.png" }
  ],
  locais_importantes: [
    { nome: "A Entrada da Tumba", atmosfera: "Úmida e escura.", url_imagem: "https://i.imgur.com/OplgaB8.png" }
  ]
};

function App() {
    const [sessionId, setSessionId] = useState(null);
    const [initialResponse, setInitialResponse] = useState('');
    const [adventure, setAdventure] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleStartChat = async (config) => {
        setLoading(true);
        setAdventure(null);
        if (isDemoMode) {
            setSessionId('demo-session');
            setInitialResponse('Modo de demonstração: O chat real está desativado.');
        } else {
            try {
                const response = await axios.post('/api/start_chat', config);
                setSessionId(response.data.session_id);
                setInitialResponse(response.data.initial_response);
            } catch (error) {
                console.error('Error starting chat:', error);
            }
        }
        setLoading(false);
    };

    const handleGenerateAdventure = async (config) => {
        setLoading(true);
        setSessionId(null);
        if (isDemoMode) {
            setAdventure(mockAdventure);
        } else {
            try {
                const response = await axios.post('/api/generate_adventure', config);
                setAdventure(response.data);
            } catch (error) {
                console.error('Error generating adventure:', error);
            }
        }
        setLoading(false);
    };

    return (
        <div className="App">
            <header className="App-header">
                <h1>Assistente de Criação de RPG</h1>
            </header>
            <main>
                <AdventureForm
                    onStartChat={handleStartChat}
                    onGenerateAdventure={handleGenerateAdventure}
                />
                {loading && <div className="loading">Gerando...</div>}
                {sessionId && <Chat sessionId={sessionId} initialResponse={initialResponse} isDemo={isDemoMode} />}
                {adventure && <AdventureView adventure={adventure} />}
            </main>
        </div>
    );
}

export default App;
