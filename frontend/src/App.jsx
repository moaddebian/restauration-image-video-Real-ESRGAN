import React, { useMemo, useState } from 'react';
import './index.css';
import { Layout } from './components/Layout.jsx';
import { UploadPanel } from './components/UploadPanel.jsx';
import { PreviewPanel } from './components/PreviewPanel.jsx';
import { ProcessingPanel } from './components/ProcessingPanel.jsx';
import { ComparisonPanel } from './components/ComparisonPanel.jsx';

// URL de l'API : utilise le proxy Vite en développement ou l'URL configurée
const API_BASE = import.meta.env.VITE_API_URL || '/api';

function App() {
  const [media, setMedia] = useState(null);
  const [model, setModel] = useState('RealESRGAN_x4plus');
  const [scale, setScale] = useState(4);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [restoredUrl, setRestoredUrl] = useState(null);
  const [downloadAnchor] = useState(() => document.createElement('a'));
  const [activeView, setActiveView] = useState('studio'); // 'studio' | 'about'
  const [error, setError] = useState(null);

  const originalUrl = useMemo(() => {
    if (!media?.file) return null;
    return URL.createObjectURL(media.file);
  }, [media]);

  const handleStartProcessing = async () => {
    if (!media?.file) return;

    setIsProcessing(true);
    setProgress(0);
    setError(null);
    setRestoredUrl(null);

    try {
      // Simuler une progression pendant l'upload et le traitement
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 5;
        });
      }, 200);

      // Préparer FormData
      const formData = new FormData();
      formData.append('image', media.file);
      formData.append('model', model);
      formData.append('outscale', scale.toString());

      // Appel API Flask
      const response = await fetch(`${API_BASE}/restore`, {
        method: 'POST',
        body: formData,
      });

      clearInterval(progressInterval);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Erreur lors de la restauration');
      }

      const result = await response.json();

      if (result.success) {
        // Utiliser le proxy Vite pour les URLs (fonctionne en dev et prod)
        // Les URLs retournées par Flask sont relatives (/api/preview/...)
        // Le proxy Vite les redirige automatiquement vers Flask
        setRestoredUrl(result.preview_url);
        setProgress(100);
        
        // Stocker l'URL de téléchargement pour le bouton download
        downloadAnchor.href = result.download_url;
        const ext = media.file.name.split('.').pop() || 'jpg';
        const safeName = media.file.name.replace(/\.[^/.]+$/, '');
        downloadAnchor.download = `${safeName}_restored.${ext}`;
      } else {
        throw new Error(result.error || 'Échec de la restauration');
      }
    } catch (err) {
      setError(err.message || 'Une erreur est survenue');
      setProgress(0);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDownload = () => {
    if (!downloadAnchor.href || !media?.file) return;
    downloadAnchor.click();
  };

  const content =
    activeView === 'studio' ? (
      <>
        <section className="hero">
        <div className="hero-copy">
          <h1>
            Restore<span className="hero-emphasis"> lost detail</span> with{' '}
            <span className="hero-gradient">neural upscaling</span>
          </h1>
          <p>
            Nostalix AI enhances old, noisy, and compressed media with an AI pipeline inspired by Real-ESRGAN.
            Drop your degraded footage and preview crystal-clear results in seconds.
          </p>
          <div className="hero-tags">
            <span className="pill">Images</span>
            <span className="pill">Videos</span>
            
          </div>
        </div>
        <div className="hero-logo">
          <img 
            src="/logo-nostalix-transparent.png" 
            alt="Nostalix AI Logo" 
            className="hero-logo-img"
          />
        </div>
        </section>

        <section className="studio-grid">
        <div className="studio-column">
          <UploadPanel onFileSelected={setMedia} />
          <ProcessingPanel
            media={media}
            progress={progress}
            onStart={handleStartProcessing}
            isProcessing={isProcessing}
            model={model}
            setModel={setModel}
            scale={scale}
            setScale={setScale}
            error={error}
          />
        </div>
        <div className="studio-column">
          <PreviewPanel media={media} processing={isProcessing} />
          <ComparisonPanel
            original={originalUrl}
            restored={restoredUrl}
            mediaKind={media?.kind}
            onDownload={handleDownload}
          />
        </div>
      </section>
      </>
    ) : (
      <section className="panel panel-about">
        <h2 className="panel-title">About the lab</h2>
        <p className="panel-subtitle">
          Nostalix AI is designed to plug directly into Real-ESRGAN or any modern super-resolution backend. The UI you
          see is fully API-ready and separates upload, processing orchestration, and visualization.
        </p>
        <ul className="about-list">
          <li>
            <strong>Image restoration</strong> — upscale low-res assets, recover edges, and reduce JPEG artifacts while
            preserving content.
          </li>
          <li>
            <strong>Video enhancement</strong> — process frames in batches, then stream them back into the comparison
            surface for instant QA.
          </li>
          <li>
            <strong>Backend ready</strong> — replace the simulated progress with a REST or WebSocket call to your
            Real-ESRGAN microservice.
          </li>
        </ul>
        <p className="panel-subtitle" style={{ marginTop: 12 }}>
          Hook suggestions:
        </p>
        <ul className="about-list">
          <li>
            Replace the simulated timer in <code>handleStartProcessing</code> with a call to your API.
          </li>
          <li>
            Stream progress updates via WebSockets to drive the animated progress bar.
          </li>
          <li>
            Store signed URLs for restored assets and feed them into the comparison panel as <code>restoredUrl</code>.
          </li>
        </ul>
      </section>
    );

  return (
    <Layout activeView={activeView} onNavChange={setActiveView}>
      {content}
    </Layout>
  );
}

export default App;
