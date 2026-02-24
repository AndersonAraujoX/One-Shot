import React, { useEffect, useState } from 'react';
import { getAdventures } from '../services/api';

function AdventureList({ onSelectAdventure, onNewAdventure }) {
    const [adventures, setAdventures] = useState([]);
    const [loading, setLoading] = useState(true);
    const [fetchError, setFetchError] = useState(false);

    useEffect(() => {
        const fetchAdventures = async () => {
            try {
                const data = await getAdventures();
                setAdventures(data);
                setFetchError(false);
            } catch (error) {
                console.error("Failed to fetch adventures", error);
                setFetchError(true);
            } finally {
                setLoading(false);
            }
        };
        fetchAdventures();
    }, []);

    if (loading) return <div>Conectando ao servidor mágico... (O plano gratuito na nuvem pode levar até 1 minuto para acordar no primeiro acesso do dia!)</div>;

    return (
        <div className="adventure-list-view">
            <div className="list-header">
                <h2>Aventuras Salvas</h2>
                <button onClick={onNewAdventure} className="btn-primary">+ Nova Aventura</button>
            </div>
            <div className="list-container">
                {fetchError ? (
                    <div className="empty-state">
                        <p style={{ color: '#ff6b6b' }}>Servidor em repouso zZz... Ele entra em descanso após alguns minutos sem uso. Aguarde cerca de 1 minuto e recarregue a página para ele acordar!</p>
                    </div>
                ) : adventures.length === 0 ? (
                    <div className="empty-state">
                        <p>Nenhuma aventura encontrada. Comece criando uma!</p>
                    </div>
                ) : (
                    <ul>
                        {adventures.map(adv => (
                            <li key={adv.id} onClick={() => onSelectAdventure(adv)} className="adventure-item">
                                <strong>{adv.title || "Sem Título"}</strong>
                                <div className="tags">
                                    <span className="system-tag">{adv.system}</span>
                                </div>
                                <span className="date">Criado em: {new Date(adv.created_at).toLocaleDateString()}</span>
                            </li>
                        ))}
                    </ul>
                )}
            </div>
        </div>
    );
}

export default AdventureList;
