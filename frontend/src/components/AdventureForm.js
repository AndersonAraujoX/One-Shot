// src/components/AdventureForm.js
import React, { useState } from 'react';

const AdventureForm = ({ onStartChat, onGenerateAdventure }) => {
    const [config, setConfig] = useState({
        sistema: 'D&D 5e',
        genero_estilo: 'Fantasia',
        num_jogadores: 4,
        nivel_tier: 'Nível 3',
        tempo_estimado: '3-4 horas'
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setConfig(prevConfig => ({
            ...prevConfig,
            [name]: value
        }));
    };

    return (
        <div className="adventure-form">
            <h2>Crie sua Aventura</h2>
            <form>
                <label>
                    Sistema:
                    <input type="text" name="sistema" value={config.sistema} onChange={handleChange} />
                </label>
                <label>
                    Gênero/Estilo:
                    <input type="text" name="genero_estilo" value={config.genero_estilo} onChange={handleChange} />
                </label>
                <label>
                    Número de Jogadores:
                    <input type="number" name="num_jogadores" value={config.num_jogadores} onChange={handleChange} />
                </label>
                <label>
                    Nível/Tier:
                    <input type="text" name="nivel_tier" value={config.nivel_tier} onChange={handleChange} />
                </label>
                <label>
                    Tempo Estimado:
                    <input type="text" name="tempo_estimado" value={config.tempo_estimado} onChange={handleChange} />
                </label>
                <div className="buttons">
                    <button type="button" onClick={() => onStartChat(config)}>Iniciar Chat Interativo</button>
                    <button type="button" onClick={() => onGenerateAdventure(config)}>Gerar Aventura Completa</button>
                </div>
            </form>
        </div>
    );
};

export default AdventureForm;
