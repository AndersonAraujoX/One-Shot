// src/components/AdventureView.js
import React from 'react';
import axios from 'axios';

const AdventureView = ({ adventure }) => {

    const handleExportPDF = async () => {
        try {
            const response = await axios.post('/api/export_pdf', adventure, {
                responseType: 'blob',
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `${adventure.titulo.toLowerCase().replace(/ /g, '-')}.pdf`);
            document.body.appendChild(link);
            link.click();
        } catch (error) {
            console.error('Error exporting to PDF:', error);
        }
    };

    const handleExportVTT = async () => {
        try {
            const response = await axios.post('/api/export_vtt', adventure, {
                responseType: 'blob',
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `${adventure.titulo.toLowerCase().replace(/ /g, '-')}.zip`);
            document.body.appendChild(link);
            link.click();
        } catch (error) {
            console.error('Error exporting to VTT:', error);
        }
    };

    return (
        <div className="adventure-view">
            <button onClick={handleExportVTT}>Exportar para FoundryVTT</button>
            <button onClick={handleExportPDF}>Exportar para PDF</button>
            <h2>{adventure.titulo}</h2>
            <p>{adventure.sinopse}</p>

            <h3>Personagens Chave</h3>
            {adventure.personagens_chave.map((npc, index) => (
                <div key={index}>
                    <h4>{npc.nome}</h4>
                    <p>{npc.aparencia}</p>
                    {npc.url_imagem && <img src={npc.url_imagem} alt={npc.nome} />}
                </div>
            ))}

            <h3>Locais Importantes</h3>
            {adventure.locais_importantes.map((local, index) => (
                <div key={index}>
                    <h4>{local.nome}</h4>
                    <p>{local.atmosfera}</p>
                    {local.url_imagem && <img src={local.url_imagem} alt={local.nome} />}
                </div>
            ))}
        </div>
    );
};

export default AdventureView;