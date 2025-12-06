import React, { useEffect, useState } from 'react';
import { getAdventures } from '../services/api';

function AdventureList({ onSelectAdventure, onNewAdventure }) {
    const [adventures, setAdventures] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAdventures = async () => {
            try {
                const data = await getAdventures();
                setAdventures(data);
            } catch (error) {
                console.error("Failed to fetch adventures", error);
            } finally {
                setLoading(false);
            }
        };
        fetchAdventures();
    }, []);

    if (loading) return <div>Carregando aventuras...</div>;

    return (
        <div className="adventure-list">
            <h2>Aventuras Salvas</h2>
            <button onClick={onNewAdventure} className="btn-primary">Nova Aventura</button>
            <div className="list-container">
                {adventures.length === 0 ? (
                    <p>Nenhuma aventura encontrada.</p>
                ) : (
                    <ul>
                        {adventures.map(adv => (
                            <li key={adv.id} onClick={() => onSelectAdventure(adv)} className="adventure-item">
                                <strong>{adv.title || "Sem Título"}</strong>
                                <span className="system-tag">{adv.system}</span>
                                <span className="date">{new Date(adv.created_at).toLocaleDateString()}</span>
                            </li>
                        ))}
                    </ul>
                )}
            </div>
        </div>
    );
}

export default AdventureList;
