import React, { useState } from 'react';
import { generateAdventureStream } from './services/api';
import AdventureForm from './components/AdventureForm';
import TabbedView from './components/TabbedView';
import AdventureList from './components/AdventureList';
import NPCChat from './components/NPCChat';
import LoadingSpinner from './components/common/LoadingSpinner';
import ErrorDisplay from './components/common/ErrorDisplay';
import './App.css';

function App() {
    const [adventure, setAdventure] = useState(null);
    const [loading, setLoading] = useState(false);
    const [loadingMessage, setLoadingMessage] = useState('');
    const [error, setError] = useState(null);
    const [view, setView] = useState('list'); // 'list', 'create', 'view', 'chat'

    const handleGenerateAdventure = async (config) => {
        setLoading(true);
        setLoadingMessage('Iniciando geração...');
        setError(null);
        setAdventure({}); // Start with empty object
        setView('view');

        await generateAdventureStream(
            config,
            (chunk) => {
                if (chunk.type === 'progress') {
                    setLoadingMessage(chunk.message);
                } else if (chunk.type === 'data') {
                    setAdventure(prev => {
                        const newData = { ...prev };
                        if (chunk.section === 'contexto' && typeof chunk.content === 'object') {
                            return { ...newData, ...chunk.content };
                        }
                        newData[chunk.section] = chunk.content;
                        return newData;
                    });
                } else if (chunk.type === 'error') {
                    console.error("Stream error:", chunk.message);
                    setError(chunk.message);
                }
            },
            (err) => {
                console.error('Error generating adventure:', err);
                setError('Não foi possível carregar a aventura. Verifique o console.');
                setLoading(false);
            },
            () => {
                setLoading(false);
                setLoadingMessage('');
            }
        );
    };

    const handleSelectAdventure = (adv) => {
        setAdventure(adv.data || adv); // Handle both full DB object and flat data
        setView('view');
    };

    const handleUpdateAdventure = (section, content) => {
        setAdventure(prev => ({
            ...prev,
            [section]: content
        }));
    };

    const [theme, setTheme] = useState('dark');

    const toggleTheme = (newTheme) => {
        setTheme(newTheme);
        document.documentElement.setAttribute('data-theme', newTheme);
    };

    return (
        <div className="App">
            <header className="App-header">
                <h1>Assistente de Criação de RPG</h1>
                <div className="theme-switcher">
                    <select onChange={(e) => toggleTheme(e.target.value)} value={theme}>
                        <option value="dark">Dark</option>
                        <option value="light">Light</option>
                        <option value="fantasy">Fantasia</option>
                        <option value="cyberpunk">Cyberpunk</option>
                    </select>
                </div>
                <nav>
                    <button onClick={() => setView('list')}>Minhas Aventuras</button>
                    <button onClick={() => setView('create')}>Nova Aventura</button>
                    {adventure && <button onClick={() => setView('view')}>Aventura Atual</button>}
                    {adventure && <button onClick={() => setView('chat')}>Chat com NPC</button>}
                </nav>
            </header>
            <main>
                {view === 'list' && (
                    <AdventureList
                        onSelectAdventure={handleSelectAdventure}
                        onNewAdventure={() => setView('create')}
                    />
                )}

                {view === 'create' && (
                    <>
                        <AdventureForm
                            onGenerateAdventure={handleGenerateAdventure}
                            isGenerating={loading}
                        />
                        {loading && <LoadingSpinner message={loadingMessage} />}
                        <ErrorDisplay message={error} />
                    </>
                )}

                {view === 'view' && adventure && (
                    <>
                        {loading && <div className="streaming-indicator">Gerando: {loadingMessage}...</div>}
                        <TabbedView adventure={adventure} onUpdate={handleUpdateAdventure} />
                    </>
                )}

                {view === 'chat' && adventure && (
                    <NPCChat adventure={adventure} />
                )}
            </main>
        </div>
    );
}

export default App;
