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

    const renderContent = () => {
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
                            <div className="cover-image-container" style={{ marginBottom: '20px', textAlign: 'center' }}>
                                <img 
                                    src={`https://image.pollinations.ai/prompt/${encodeURIComponent(adventure.prompt_imagem_capa)}?width=800&height=400&nologo=true`} 
                                    alt="Capa da Aventura" 
                                    style={{ width: '100%', maxWidth: '800px', borderRadius: '8px', boxShadow: '0 4px 12px rgba(0,0,0,0.3)' }}
                                />
                                <div className="prompt-box" style={{ background: 'rgba(255,255,255,0.05)', padding: '10px', borderRadius: '5px', marginTop: '10px', fontSize: '0.8rem', color: '#aaa', textAlign: 'left', borderLeft: '4px solid #e91e63' }}>
                                    <strong>🎨 Prompt da Capa:</strong> {adventure.prompt_imagem_capa}
                                </div>
                            </div>
                        )}
                        <ReactMarkdown>{content}</ReactMarkdown>
                    </div>
                </div>
            );
        }

        // Special handling for complex objects
        // Incluindo cenario e desafios que também são arrays de objetos
        const complexTabs = ['personagens', 'personagens_chave', 'locais', 'locais_importantes', 'cenario', 'desafios'];

        if (complexTabs.includes(activeTab) && !isEditing) {
            return (
                <div className="adventure-section">
                    <div className="section-header">
                        <h2>{title}</h2>
                        <button onClick={() => handleCopy(JSON.stringify(content, null, 2))} className="copy-button">Copiar JSON</button>
                    </div>
                    <div className="section-content cards-container">
                        {Array.isArray(content) ? (
                            content.map((item, idx) => (
                                <div key={idx} className="card-wrapper">
                                    <div className="card">
                                        {/* Tenta identificar campos comuns automaticamente */}
                                        <h3>{item.nome || item.titulo || `Item ${idx + 1}`}</h3>

                                        {item.aparencia && <p><strong>Aparência:</strong> {item.aparencia}</p>}
                                        {item.atmosfera && <p><strong>Atmosfera:</strong> {item.atmosfera}</p>}
                                        {item.descricao && <p><strong>Descrição:</strong> {item.descricao}</p>}
                                        {item.efeito && <p><strong>Efeito:</strong> {item.efeito}</p>}
                                        {item.tipo && <p><strong>Tipo:</strong> {item.tipo}</p>}

                                        {/* Imagem Visual Renderizada pelo Prompt */}
                                        {item.prompt_imagem && (
                                            <div className="generated-image" style={{ marginTop: '15px' }}>
                                                <img 
                                                    src={`https://image.pollinations.ai/prompt/${encodeURIComponent(item.prompt_imagem)}?width=400&height=400&nologo=true&seed=${idx}`} 
                                                    alt={item.nome || 'Imagem Gerada'} 
                                                    style={{ width: '100%', borderRadius: '4px', boxShadow: '0 2px 4px rgba(0,0,0,0.2)' }}
                                                    loading="lazy"
                                                />
                                                <div className="mini-prompt" style={{ marginTop: '5px', fontSize: '0.7rem', color: '#666' }}>
                                                    <strong>🎨 Prompt:</strong> {item.prompt_imagem}
                                                </div>
                                            </div>
                                        )}

                                        {/* Fallback para mostrar chaves extras se não achou as principais */}
                                        {!item.nome && !item.aparencia && !item.atmosfera && !item.descricao && (
                                            <pre style={{ fontSize: '0.7rem' }}>{JSON.stringify(item, null, 2)}</pre>
                                        )}
                                    </div>
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

        // Se for um Objeto (como Ato 1, Ato 2...), vamos tentar formatar bonito em vez de JSON
        if (typeof content === 'object' && content !== null && !Array.isArray(content)) {
            // O "target" é o objeto que contem os dados do ato.
            // As vezes o objeto vem como { "ato1": { ... } } ou direto { "titulo": ... }
            // Vamos achar onde estão os dados reais.
            let target = content;

            // Tenta desenvelopar se a chave for igual a tab ou algo tipo/ato/
            if (content[activeTab]) target = content[activeTab];
            else if (content.ato1 && activeTab === 'ato1') target = content.ato1;
            else if (content.ato2 && activeTab === 'ato2') target = content.ato2;
            else if (content.ato3 && activeTab === 'ato3') target = content.ato3;
            else if (content.ato4 && activeTab === 'ato4') target = content.ato4;
            else if (content.ato5 && activeTab === 'ato5') target = content.ato5;

            // Verifica se tem sinais de ser um Ato/Cena
            if (target.titulo || target.sinopse || target.cenas) {
                return (
                    <div className="adventure-section">
                        <div className="section-header"><h2>{title}</h2></div>
                        <div className="section-content" style={{ textAlign: 'left' }}>
                            {target.titulo && <h3>{target.titulo}</h3>}
                            {target.sinopse && <p><strong>Sinopse:</strong> {target.sinopse}</p>}

                            {target.cenas && Array.isArray(target.cenas) && (
                                <div className="cenas-list">
                                    <h4>Cenas:</h4>
                                    {target.cenas.map((cena, i) => (
                                        <div key={i} className="cena-item" style={{ background: 'rgba(255,255,255,0.05)', padding: '15px', margin: '15px 0', borderRadius: '8px', borderLeft: '3px solid #6200ea' }}>
                                            <h5 style={{ marginTop: 0, color: '#bb86fc' }}>{cena.nome}</h5>
                                            <p>{cena.descricao}</p>

                                            <div style={{ fontSize: '0.9rem', color: '#ccc', marginTop: '10px' }}>
                                                {cena.locais && <p><strong>📍 Local:</strong> {Array.isArray(cena.locais) ? cena.locais.join(", ") : cena.locais}</p>}
                                                {cena.personagens && <p><strong>👤 NPCs:</strong> {Array.isArray(cena.personagens) ? cena.personagens.join(", ") : cena.personagens}</p>}
                                                {cena.desafios_associados && <p><strong>⚔️ Desafios:</strong> {Array.isArray(cena.desafios_associados) ? cena.desafios_associados.join(", ") : cena.desafios_associados}</p>}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                );
            }

            // Se falhar a detecção bonita, converte pra JSON string formatted
            displayContent = JSON.stringify(target, null, 2); // Usa target desenvelopado
        }

        if (Array.isArray(content)) {
            // Smart Array to String: Se os items forem objetos, tenta pegar o nome ou stringify
            displayContent = content.map(item => {
                if (typeof item === 'object') {
                    return `- ${item.nome || item.descricao || JSON.stringify(item)}`;
                }
                return `- ${item}`;
            }).join('\n');
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
