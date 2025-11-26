// src/components/common/ErrorDisplay.js
import React from 'react';
import './ErrorDisplay.css';

const ErrorDisplay = ({ message }) => {
  if (!message) return null;

  return (
    <div className="error-overlay">
      <div className="error-box">
        <h4>Ocorreu um Erro</h4>
        <p>{message}</p>
      </div>
    </div>
  );
};

export default ErrorDisplay;
