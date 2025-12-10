// src/components/common/LoadingSpinner.js
import React from 'react';
import './LoadingSpinner.css';

const LoadingSpinner = ({ message }) => (
  <div className="spinner-overlay">
    <div className="spinner-content">
      <div className="spinner-rune"></div>
      <p className="spinner-message">{message || "Conjurando a aventura..."}</p>
      <div className="progress-bar-container">
        <div className="progress-bar-fill"></div>
      </div>
    </div>
  </div>
);

export default LoadingSpinner;
