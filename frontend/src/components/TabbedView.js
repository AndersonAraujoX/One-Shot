import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import './TabbedView.css';

const Section = ({ title, content, onCopy }) => (
    <div className="adventure-section">
        <div className="section-header">
            <h2>{title}</h2>
            <button onClick={onCopy} className="copy-button">Copiar Seção</button>
        </div>
        <div className="section-content">
            {content}
        </div>
    </div>
);

function TabbedView({ adventure }) {
    const [activeTab, setActiveTab] = useState('sinopse');

    if (!adventure) return null;

    const adventureAsMarkdown = () => {
        let md = `# ${adventure.titulo}\n\n`;
        md += `## Sinopse\n\n${adventure.sinopse}\n\n`;
        if (adventure.ganchos) md += `## Ganchos da Trama\n\n${adventure.ganchos.map(g => `- ${g}`).join('\n')}\n\n`;
        if (adventure.personagens_chave) {
            md += `## Personagens Chave\n\n`;
            adventure.personagens_chave.forEach(p => {
                md += `### ${p.nome}\n\n`;
                md += `**Aparência:** ${p.aparencia}\n\n`;
                if (p.url_imagem) md += `![${p.nome}](${p.url_imagem})\n\n`;
            });
        }
        if (adventure.locais_importantes) {
            md += `## Locais Importantes\n\n`;
            adventure.locais_importantes.forEach(l => {
                md += `### ${l.nome}\n\n`;
                md += `**Atmosfera:** ${l.atmosfera}\n\n`;
                if (l.url_imagem) md += `![${l.nome}](${l.url_imagem})\n\n`;
            });
        }
        if (adventure.desafios) md += `## Desafios\n\n${adventure.desafios.map(d => `- ${d}`).join('\n')}\n\n`;
        if (adventure.resumo_da_aventura) md += `## Resumo da Aventura\n\n${adventure.resumo_da_aventura}\n\n`;

        return md;
    };

    const handleExport = () => {
        const markdown = adventureAsMarkdown();
        const blob = new Blob([markdown], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${adventure.titulo.replace(/ /g, '_')}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    };

    const handleCopy = (content) => {
        navigator.clipboard.writeText(content).then(() => {
            alert('Conteúdo copiado!');
        }, (err) => {
            console.error('Erro ao copiar: ', err);
        });
    };

    const getTabContent = (tab) => {
        switch (tab) {
            case 'sinopse': return adventure.sinopse;
            case 'personagens': return adventure.personagens_chave.map(p => `### ${p.nome}\n**Aparência:** ${p.aparencia}`).join('\n\n');
            case 'locais': return adventure.locais_importantes.map(l => `### ${l.nome}\n**Atmosfera:** ${l.atmosfera}`).join('\n\n');
            default:
                const content = adventure[tab];
                if (Array.isArray(content)) return content.map(item => `- ${item}`).join('\n');
                return content;
        }
    };
    
    const renderContent = () => {
        const rawContent = getTabContent(activeTab);
        const title = activeTab === 'sinopse' ? adventure.titulo : activeTab.replace(/_/g, ' ');

        return (
            <Section title={title} onCopy={() => handleCopy(rawContent)} content={
                activeTab === 'personagens' || activeTab === 'locais'
                    ? (adventure[activeTab === 'personagens' ? 'personagens_chave' : 'locais_importantes'] || []).map(item => (
                        <div key={item.nome} className="card">
                            <h3>{item.nome}</h3>
                            <ReactMarkdown>{item.aparencia || item.atmosfera}</ReactMarkdown>
                            {item.url_imagem && <img src={item.url_imagem} alt={item.nome} />}
                        </div>
                    ))
                    : <ReactMarkdown>{rawContent}</ReactMarkdown>
            } />
        );
    };

    const sections = [
        'sinopse', 
        ...Object.keys(adventure).filter(k => k !== 'titulo' && k !== 'sinopse' && k !== 'personagens_chave' && k !== 'locais_importantes')
    ];
    if (adventure.personagens_chave) sections.splice(1, 0, 'personagens');
    if (adventure.locais_importantes) sections.splice(2, 0, 'locais');


    return (
        <div className="tabbed-view">
            <div className="tab-buttons">
                {sections.map(section => (
                    <button
                        key={section}
                        className={activeTab === section ? 'active' : ''}
                        onClick={() => setActiveTab(section)}
                    >
                        {section.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </button>
                ))}
                <button onClick={handleExport} className="export-button">Exportar Aventura</button>
            </div>
            <div className="tab-content">
                {renderContent()}
            </div>
        </div>
    );
}

export default TabbedView;
