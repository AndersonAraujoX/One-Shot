// src/components/Chat.js
import React, { useState } from 'react';
import axios from 'axios';

const Chat = ({ sessionId, initialResponse, isDemo }) => {
    const [messages, setMessages] = useState([{ from: 'ai', text: initialResponse }]);
    const [input, setInput] = useState('');

    const sendMessage = async () => {
        if (!input.trim()) return;

        const newMessages = [...messages, { from: 'user', text: input }];
        setMessages(newMessages);
        setInput('');

        try {
            const response = await axios.post('/api/send_message', {
                session_id: sessionId,
                prompt: input
            });
            setMessages([...newMessages, { from: 'ai', text: response.data.response }]);
        } catch (error) {
            console.error('Error sending message:', error);
            setMessages([...newMessages, { from: 'ai', text: 'Desculpe, ocorreu um erro.' }]);
        }
    };

    return (
        <div className="chat">
            <div className="messages">
                {messages.map((msg, index) => (
                    <div key={index} className={`message ${msg.from}`}>
                        {msg.text.startsWith('/static') ? <img src={msg.text} alt="generated" /> : msg.text}
                    </div>
                ))}
            </div>
            <div className="input-area">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    disabled={isDemo}
                />
                <button onClick={sendMessage} disabled={isDemo}>Enviar</button>
            </div>
        </div>
    );
};

export default Chat;
