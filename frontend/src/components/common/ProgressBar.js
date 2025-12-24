
import React from 'react';
import './ProgressBar.css';

const ProgressBar = ({ progress, message }) => {
    return (
        <div className="progress-container">
            <div className="progress-info">
                <span className="progress-message">{message || "Carregando..."}</span>
                <span className="progress-percentage">{Math.round(progress)}%</span>
            </div>
            <div className="progress-track">
                <div
                    className="progress-fill"
                    style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
                ></div>
                <div className="progress-glow"></div>
            </div>
        </div>
    );
};

export default ProgressBar;
