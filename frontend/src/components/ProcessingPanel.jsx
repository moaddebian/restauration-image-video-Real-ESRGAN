import React from 'react';

export function ProcessingPanel({ media, progress, onStart, isProcessing, model, setModel, scale, setScale, error }) {
  const models = [
    { value: 'RealESRGAN_x4plus', label: 'RealESRGAN x4+ (Général)' },
    { value: 'RealESRGAN_x4plus_anime_6B', label: 'RealESRGAN x4+ Anime' },
    { value: 'RealESRNet_x4plus', label: 'RealESRNet x4+' },
    { value: 'RealESRGAN_x2plus', label: 'RealESRGAN x2+ (Rapide)' },
  ];

  return (
    <section className="panel panel-processing">
      <h2 className="panel-title">AI Restoration</h2>
      <p className="panel-subtitle">
        Real-ESRGAN pipeline. Configurez le modèle et le facteur d'agrandissement.
      </p>

      {error && (
        <div className="error-message" style={{ 
          padding: '12px', 
          background: 'rgba(239, 68, 68, 0.1)', 
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '8px',
          marginBottom: '16px',
          color: '#ef4444'
        }}>
          ⚠️ {error}
        </div>
      )}

      <div className="control-row">
        <label className="field-group">
          <span className="field-label">Modèle</span>
          <select 
            className="form-control"
            value={model}
            onChange={(e) => setModel(e.target.value)}
            disabled={isProcessing}
          >
            {models.map(m => (
              <option key={m.value} value={m.value}>{m.label}</option>
            ))}
          </select>
        </label>
      </div>

      <div className="control-row">
        <div className="field-group">
          <span className="field-label">Facteur d'agrandissement</span>
          <div className="chip-row">
            {[2, 4].map(s => (
              <button 
                key={s} 
                type="button" 
                className={`chip ${scale === s ? 'chip-active' : ''}`}
                onClick={() => setScale(s)}
                disabled={isProcessing}
              >
                ×{s}
              </button>
            ))}
          </div>
        </div>
      </div>

      <button
        type="button"
        className="primary-button"
        disabled={!media?.file || isProcessing}
        onClick={onStart}
      >
        {isProcessing ? (
          <>
            <span className="spinner" />
            Processing ({progress}%)
          </>
        ) : (
          'Run AI Restoration'
        )}
      </button>

      <div className="progress-track" aria-hidden={!isProcessing}>
        <div className="progress-bar" style={{ width: `${progress}%` }} />
      </div>
    </section>
  );
}

