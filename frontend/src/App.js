import React, { useState } from 'react';
import { generateAdventure } from './services/api';
import AdventureForm from './components/AdventureForm';
import TabbedView from './components/TabbedView';
import LoadingSpinner from './components/common/LoadingSpinner';
import ErrorDisplay from './components/common/ErrorDisplay';
import './App.css';

function App() {
    const [adventure, setAdventure] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleGenerateAdventure = async (config) => {
        setLoading(true);
        setError(null);
        setAdventure(null);
        try {
            const data = await generateAdventure(config);
            setAdventure(data);
        } catch (err) {
            console.error('Error generating adventure:', err);
            setError('Não foi possível carregar a aventura. Verifique o console para mais detalhes.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="App">
            <header className="App-header">
                <h1>Assistente de Criação de RPG</h1>
            </header>
            <main>
                <AdventureForm
                    onGenerateAdventure={handleGenerateAdventure}
                    isGenerating={loading}
                />
                {loading && <LoadingSpinner />}
                <ErrorDisplay message={error} />
                {adventure && (
                    <TabbedView
                        adventure={adventure}
                    />
                )}
            </main>
        </div>
    );
}

export default App;
