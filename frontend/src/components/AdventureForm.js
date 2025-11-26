import React, { useState } from 'react';
import './AdventureForm.css';

const AdventureForm = ({ onGenerateAdventure, isGenerating }) => {
    const [config, setConfig] = useState({
        sistema: 'D&D 5e',
        genero_estilo: 'Fantasia Sombria',
        num_jogadores: 4,
        nivel_tier: 'Nível 5',
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setConfig(prevConfig => ({
            ...prevConfig,
            [name]: name === 'num_jogadores' ? parseInt(value, 10) : value
        }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onGenerateAdventure(config);
    };

    return (
        <div className="adventure-form-container">
            <form onSubmit={handleSubmit} className="adventure-form">
                <h2>Configure sua Aventura</h2>
                <div className="form-grid">
                    <label>
                        Sistema
                        <input type="text" name="sistema" value={config.sistema} onChange={handleChange} />
                    </label>
                    <label>
                        Gênero/Estilo
                        <input type="text" name="genero_estilo" value={config.genero_estilo} onChange={handleChange} />
                    </label>
                    <label>
                        Nº de Jogadores
                        <input type="number" name="num_jogadores" value={config.num_jogadores} onChange={handleChange} min="1" />
                    </label>
                    <label>
                        Nível dos Personagens
                        <input type="text" name="nivel_tier" value={config.nivel_tier} onChange={handleChange} />
                    </label>
                </div>
                <button type="submit" disabled={isGenerating}>
                    {isGenerating ? 'Gerando...' : 'Gerar Aventura Completa'}
                </button>
            </form>
        </div>
    );
};

export default AdventureForm;
