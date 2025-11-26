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

export const generateAdventure = async (config) => {
  if (isDemoMode) {
    // In demo mode, we simulate a network delay and fetch a local mock file.
    await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate loading
    const response = await axios.get('/mock-adventure.json');
    return response.data;
  }
  const response = await axios.post('/api/generate_adventure', config);
  return response.data;
};
