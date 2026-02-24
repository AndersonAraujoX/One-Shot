// src/services/api.js
import axios from 'axios';

const BASE_URL = process.env.REACT_APP_API_URL || '';

export const startChat = async (config) => {
  const response = await axios.post(`${BASE_URL}/api/start_chat`, config);
  return response.data;
};

export const generateAdventureStream = async (config, onChunk, onError, onComplete) => {

  try {
    const response = await fetch(`${BASE_URL}/api/generate_adventure`, {
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
  const response = await axios.get(`${BASE_URL}/api/adventures`);
  return response.data;
};

export const getAdventure = async (id) => {
  const response = await axios.get(`${BASE_URL}/api/adventures/${id}`);
  return response.data;
};

export const sendMessage = async (sessionId, prompt) => {
  const response = await axios.post(`${BASE_URL}/api/send_message`, { session_id: sessionId, prompt });
  return response.data;
};
