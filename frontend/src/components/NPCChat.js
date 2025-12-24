import React, { useState } from 'react';
import { sendMessage, startChat } from '../services/api';

function NPCChat({ adventure }) {
    const [selectedNPC, setSelectedNPC] = useState(null);
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [sessionId, setSessionId] = useState(null);
    const [loading, setLoading] = useState(false);

    const npcs = adventure.personagens_chave || [];

    const handleSelectNPC = async (npc) => {
        setSelectedNPC(npc);
        setMessages([]);
        setLoading(true);
        try {
            // Start a new chat session contextually for this NPC
            // Ideally we would have a specific endpoint or pass context, 
            // but for now we reuse startChat or just assume the backend handles it.
            // Actually, let's just start a generic chat and prime it.

            const config = {
                sistema: adventure.system || "Generic",
                genero_estilo: "Roleplay",
                num_jogadores: 1,
                nivel_tier: "1",
                tempo_estimado: "N/A"
            };

            const data = await startChat(config);
            setSessionId(data.session_id);

            // Prime the chat with NPC persona
            await sendMessage(data.session_id, `Você agora vai interpretar o seguinte NPC desta aventura: ${JSON.stringify(npc)}. Aja como ele, fale como ele. O usuário é um jogador ou o Mestre testando. Mantenha as respostas curtas e no personagem.`);

            setMessages([{ role: 'system', text: `Chat iniciado com ${npc.nome}` }]);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    const handleSend = async () => {
        if (!input.trim() || !sessionId) return;

        const userMsg = input;
        setInput('');
        setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
        setLoading(true);

        try {
            const data = await sendMessage(sessionId, userMsg);
            setMessages(prev => [...prev, { role: 'model', text: data.response }]);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="npc-chat-container">
            <div className="npc-list">
                <h3>Escolha um NPC</h3>
                {npcs.map((npc, idx) => (
                    <button key={idx} onClick={() => handleSelectNPC(npc)} className={selectedNPC === npc ? 'active' : ''}>
                        {npc.nome}
                    </button>
                ))}
            </div>
            <div className="chat-area">
                {selectedNPC ? (
                    <>
                        <div className="messages">
                            {messages.map((m, i) => (
                                <div key={i} className={`message ${m.role}`}>
                                    <strong>{m.role === 'user' ? 'Você' : selectedNPC.nome}: </strong>
                                    {m.text}
                                </div>
                            ))}
                        </div>
                        <div className="input-area">
                            <input
                                value={input}
                                onChange={e => setInput(e.target.value)}
                                onKeyPress={e => e.key === 'Enter' && handleSend()}
                                disabled={loading}
                                placeholder="Fale com o NPC..."
                            />
                            <button onClick={handleSend} disabled={loading}>Enviar</button>
                        </div>
                    </>
                ) : (
                    <p>Selecione um NPC para começar.</p>
                )}
            </div>
        </div>
    );
}

export default NPCChat;
