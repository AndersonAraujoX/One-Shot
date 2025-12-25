import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import './TabbedView.css';
import StatBlock from './StatBlock';

const Section = ({ title, content, onCopy, onEdit, isEditing, onSave, onCancel }) => {
    const [editValue, setEditValue] = useState(content);

    useEffect(() => {
        setEditValue(content);
    }, [content]);

    return (
        <div className="adventure-section">
            <div className="section-header">
                <h2>{title}</h2>
                <div className="actions">
                    {!isEditing ? (
                        <>
                            <button onClick={onCopy} className="copy-button">Copiar</button>
                            <button onClick={onEdit} className="edit-button">Editar</button>
                        </>
                    ) : (
                        <>
                            <button onClick={() => onSave(editValue)} className="save-button">Salvar</button>
                            <button onClick={onCancel} className="cancel-button">Cancelar</button>
                        </>
                    )}
                </div>
            </div>
            <div className="section-content">
                {isEditing ? (
                    <textarea
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        className="edit-textarea"
                    />
                ) : (
                    typeof content === 'string' ? <ReactMarkdown>{content}</ReactMarkdown> : content
                )}
            </div>
        </div>
    );
};

function TabbedView({ adventure, onUpdate }) {
    const [activeTab, setActiveTab] = useState('sinopse');
    const [editingTab, setEditingTab] = useState(null);

    if (!adventure) return null;

    const adventureAsMarkdown = () => {
        let md = `# ${adventure.titulo}\n\n`;
        md += `## Sinopse\n\n${adventure.sinopse}\n\n`;
        if (adventure.ganchos) {
            md += `## Ganchos da Trama\n\n`;
            md += Array.isArray(adventure.ganchos)
                ? `${adventure.ganchos.map(g => `- ${g}`).join('\n')}\n\n`
                : `${adventure.ganchos}\n\n`;
        }
        if (adventure.personagens_chave) {
            md += `## Personagens Chave\n\n`;
            if (Array.isArray(adventure.personagens_chave)) {
                adventure.personagens_chave.forEach(p => {
                    md += `### ${p.nome}\n\n`;
                    md += `**Aparência:** ${p.aparencia}\n\n`;
                    if (p.url_imagem) md += `![${p.nome}](${p.url_imagem})\n\n`;
                });
            } else {
                md += `${typeof adventure.personagens_chave === 'string' ? adventure.personagens_chave : JSON.stringify(adventure.personagens_chave, null, 2)}\n\n`;
            }
        }
        if (adventure.locais_importantes) {
            md += `## Locais Importantes\n\n`;
            if (Array.isArray(adventure.locais_importantes)) {
                adventure.locais_importantes.forEach(l => {
                    md += `### ${l.nome}\n\n`;
                    md += `**Atmosfera:** ${l.atmosfera}\n\n`;
                    if (l.url_imagem) md += `![${l.nome}](${l.url_imagem})\n\n`;
                });
            } else {
                md += `${typeof adventure.locais_importantes === 'string' ? adventure.locais_importantes : JSON.stringify(adventure.locais_importantes, null, 2)}\n\n`;
            }
        }
        if (adventure.desafios) {
            md += `## Desafios\n\n`;
            md += Array.isArray(adventure.desafios)
                ? `${adventure.desafios.map(d => `- ${d}`).join('\n')}\n\n`
                : `${adventure.desafios}\n\n`;
        }
        if (adventure.resumo_da_aventura) md += `## Resumo da Aventura\n\n${adventure.resumo_da_aventura}\n\n`;

        return md;
    };

    const handleExport = () => {
        const markdown = adventureAsMarkdown();
        const blob = new Blob([markdown], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${adventure.titulo ? adventure.titulo.replace(/ /g, '_') : 'aventura'}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    };

    const handleCopy = (content) => {
        const textToCopy = typeof content === 'string' ? content : JSON.stringify(content, null, 2);
        navigator.clipboard.writeText(textToCopy).then(() => {
            alert('Conteúdo copiado!');
        }, (err) => {
            console.error('Erro ao copiar: ', err);
        });
    };

    const handleSave = (newContent) => {
        // If it was a list (like challenges), try to keep it as list if possible, or just save as string
        // For simplicity, we save as string for now, unless we parse it back.
        // The backend expects specific formats for some fields.
        // But since we are editing text, we might just update the text representation.

        // Special handling for array fields if we want to keep them as arrays
        // For now, let's assume the user edits the raw text and we save it as is.
        // If the original was an array, we might want to split by newline.

        let contentToSave = newContent;
        const originalContent = adventure[activeTab];

        if (Array.isArray(originalContent)) {
            contentToSave = newContent.split('\n').filter(line => line.trim().startsWith('-')).map(line => line.replace(/^- /, '').trim());
            if (contentToSave.length === 0) contentToSave = newContent.split('\n').filter(l => l.trim());
        }

        onUpdate(activeTab, contentToSave);
        setEditingTab(null);
    };

    const getTabContent = (tab) => {
        switch (tab) {
            case 'sinopse': return adventure.sinopse;
            case 'personagens': return adventure.personagens_chave; // Special rendering
            case 'locais': return adventure.locais_importantes; // Special rendering
            default: return adventure[tab];
        }
    };

    const content = getTabContent(activeTab);
    const title = activeTab === 'sinopse' ? adventure.titulo : activeTab.replace(/_/g, ' ');
    const isEditing = editingTab === activeTab;

    // Special handling for Sinopse to include Cover Prompt
    if (activeTab === 'sinopse') {
        return (
            <div className="adventure-section">
                <div className="section-header">
                    <h2>{title}</h2>
                    <div className="actions">
                        <button onClick={() => handleCopy(content)} className="copy-button">Copiar Sinopse</button>
                        {adventure.prompt_imagem_capa && (
                            <button onClick={() => handleCopy(adventure.prompt_imagem_capa)} className="copy-button" style={{ backgroundColor: '#e91e63' }}>Copiar Prompt Capa</button>
                        )}
                    </div>
                </div>
                <div className="section-content">
                    {adventure.prompt_imagem_capa && (
                        <div className="prompt-box" style={{ background: '#f0f0f0', padding: '10px', borderRadius: '5px', marginBottom: '15px', borderLeft: '4px solid #e91e63' }}>
                            <strong>🎨 Prompt sugerido para Capa:</strong>
                            <p style={{ fontStyle: 'italic', fontSize: '0.9rem' }}>{adventure.prompt_imagem_capa}</p>
                        </div>
                    )}
                    <ReactMarkdown>{content}</ReactMarkdown>
                </div>
            </div>
        );
    }

    // Special handling for complex objects like Characters and Locations
    if ((activeTab === 'personagens' || activeTab === 'locais') && !isEditing) {
        return (
            <div className="adventure-section">
                <div className="section-header">
                    <h2>{title}</h2>
                    {/* Editing complex objects is harder, let's skip for now or implement JSON edit */}
                    <button onClick={() => handleCopy(JSON.stringify(content, null, 2))} className="copy-button">Copiar JSON</button>
                </div>
                <div className="section-content cards-container">
                    {Array.isArray(content) ? (
                        content.map((item, idx) => (
                            <div key={idx} className="card-wrapper">
                                {activeTab === 'personagens' ? (
                                    <div className="card">
                                        <h3>{item.nome}</h3>
                                        <p><strong>Aparência:</strong> {item.aparencia}</p>
                                        {item.prompt_imagem && (
                                            <div className="mini-prompt" style={{ marginTop: '10px', fontSize: '0.8rem', color: '#666' }}>
                                                <strong>🎨 Prompt:</strong> {item.prompt_imagem}
                                            </div>
                                        )}
                                    </div>
                                ) : (
                                    <div className="card">
                                        <h3>{item.nome}</h3>
                                        <p><strong>Atmosfera:</strong> {item.atmosfera}</p>
                                        {item.prompt_imagem && (
                                            <div className="mini-prompt" style={{ marginTop: '10px', fontSize: '0.8rem', color: '#666' }}>
                                                <strong>🎨 Prompt:</strong> {item.prompt_imagem}
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        ))
                    ) : (
                        <div className="card">
                            <ReactMarkdown>{typeof content === 'string' ? content : JSON.stringify(content)}</ReactMarkdown>
                        </div>
                    )}
                </div>
            </div>
        );
    }

    // Prepare content for display/edit
    let displayContent = content;
    if (Array.isArray(content)) {
        displayContent = content.map(item => `- ${item}`).join('\n');
    }

    return (
        <Section
            title={title}
            content={displayContent}
            onCopy={() => handleCopy(displayContent)}
            onEdit={() => setEditingTab(activeTab)}
            isEditing={isEditing}
            onSave={handleSave}
            onCancel={() => setEditingTab(null)}
        />
    );
};

const sectionOrder = [
    'sinopse', 'ganchos', 'personagens', 'personagens_chave', 'locais_importantes',
    'cenario', 'desafios',
    'ato1', 'ato2', 'ato3', 'ato4', 'ato5',
    'resumo'
];

const sections = Object.keys(adventure).sort((a, b) => {
    const indexA = sectionOrder.indexOf(a);
    const indexB = sectionOrder.indexOf(b);
    if (indexA === -1 && indexB === -1) return a.localeCompare(b);
    if (indexA === -1) return 1;
    if (indexB === -1) return -1;
    return indexA - indexB;
}).filter(k => k !== 'titulo');

// Remove duplicates if any (though keys are unique)
// Handle special rendering removal if needed but our sort handles it.
// We want 'personagens' (raw) and 'personagens_chave' (npc) to be handled.
// 'personagens' might be the player chars. 
// Let's filter out internal keys if necessary.


return (
    <div className="tabbed-view">
        <div className="tab-buttons">
            {sections.map(section => (
                <button
                    key={section}
                    className={activeTab === section ? 'active' : ''}
                    onClick={() => { setActiveTab(section); setEditingTab(null); }}
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
