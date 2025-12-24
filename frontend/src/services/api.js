// src/services/api.js
import axios from 'axios';

const isDemoMode = process.env.NODE_ENV !== 'development';

export const startChat = async (config) => {
  if (isDemoMode) {
    return {
      session_id: 'demo-session',
      initial_response: 'Modo de demonstração: O chat real está desativado.',
    };
  }
  const response = await axios.post('/api/start_chat', config);
  return response.data;
};

export const generateAdventureStream = async (config, onChunk, onError, onComplete) => {
  if (isDemoMode) {
    // Mock streaming for demo
    setTimeout(() => onChunk({ type: 'progress', message: 'Iniciando demo...' }), 100);
    setTimeout(() => onChunk({ type: 'data', section: 'contexto', content: { titulo: 'Demo Adventure', sinopse: 'A demo synopsis.' } }), 1000);
    setTimeout(() => onComplete(), 2000);
    return;
  }

  try {
    const response = await fetch('/api/generate_adventure', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop(); // Keep the last partial line in the buffer

      for (const line of lines) {
        if (line.trim() === '') continue;
        try {
          const data = JSON.parse(line);
          onChunk(data);
        } catch (e) {
          console.error('Error parsing JSON chunk:', e);
        }
      }
    }
    
    if (onComplete) onComplete();

  } catch (err) {
    if (onError) onError(err);
  }
};

export const getAdventures = async () => {
    if (isDemoMode) return [];
    const response = await axios.get('/api/adventures');
    return response.data;
};

export const getAdventure = async (id) => {
    if (isDemoMode) return null;
    const response = await axios.get(`/api/adventures/${id}`);
    return response.data;
};

export const sendMessage = async (sessionId, prompt) => {
    if (isDemoMode) return { response: "Demo response" };
    const response = await axios.post('/api/send_message', { session_id: sessionId, prompt });
    return response.data;
};
