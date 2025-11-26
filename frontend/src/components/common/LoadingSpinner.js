// src/components/common/LoadingSpinner.js
import React from 'react';
import './LoadingSpinner.css';

const LoadingSpinner = () => (
  <div className="spinner-overlay">
    <div className="spinner-container"></div>
    <p>Gerando sua aventura...</p>
  </div>
);

export default LoadingSpinner;
