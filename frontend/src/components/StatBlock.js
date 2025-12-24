import React from 'react';
import ReactMarkdown from 'react-markdown';
import './StatBlock.css';

const StatBlock = ({ name, description, stats }) => {
    // Tenta detectar se 'stats' é uma string JSON ou objeto, ou texto livre
    // Se for texto livre, tentamos formatar basicão.

    return (
        <div className="stat-block">
            <div className="creature-heading">
                <h1>{name}</h1>
                <h2>{description}</h2>
            </div>
            <svg height="5" width="100%" className="tapered-rule">
                <polyline points="0,0 400,2.5 0,5"></polyline>
            </svg>
            <div className="top-stats">
                <div className="property-line">
                    <ReactMarkdown>{stats}</ReactMarkdown>
                </div>
            </div>
            <svg height="5" width="100%" className="tapered-rule">
                <polyline points="0,0 400,2.5 0,5"></polyline>
            </svg>
            {/* Aqui poderíamos adicionar Actions, Legendary Actions se o JSON fosse estruturado */}
        </div>
    );
};

export default StatBlock;
