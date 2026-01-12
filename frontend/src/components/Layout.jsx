import React from 'react';

export function Layout({ children, activeView = 'studio', onNavChange }) {
  return (
    <div className="app-root">
      <div className="app-bg-glow" />
      <header className="app-header">
        <div className="app-logo">
          <div className="app-logo-mark">
            <img 
              src="/logo-nostalix-transparent.png" 
              alt="Nostalix AI Logo" 
              className="app-logo-img"
              onError={(e) => {
                // Fallback si l'image n'est pas trouvée
                e.target.style.display = 'none';
                const fallback = e.target.parentElement;
                if (fallback) {
                  fallback.classList.add('logo-fallback');
                }
              }}
            />
          </div>
          <span className="app-logo-text">
            <span className="app-logo-title">Nostalix AI</span>
            <span className="app-logo-subtitle">AI Image &amp; Video Restoration</span>
          </span>
        </div>
        <nav className="app-nav">
          <button
            className={`nav-link ${activeView === 'studio' ? 'nav-link-active' : ''}`}
            type="button"
            onClick={() => onNavChange?.('studio')}
          >
            Studio
          </button>
          <button
            className={`nav-link ${activeView === 'about' ? 'nav-link-active' : ''}`}
            type="button"
            onClick={() => onNavChange?.('about')}
          >
            About
          </button>
        </nav>
      </header>
      <main className="app-main">{children}</main>
      <footer className="app-footer">
        <span>© {new Date().getFullYear()} Nostalix AI</span>
        <span>Powered by Moad Dabyane For YOU</span>
      </footer>
    </div>
  );
}

