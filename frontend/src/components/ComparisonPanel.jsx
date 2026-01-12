import React, { useEffect, useRef, useState } from 'react';

export function ComparisonPanel({ original, restored, mediaKind, onDownload }) {
  const containerRef = useRef(null);
  const [sliderX, setSliderX] = useState(50);

  useEffect(() => {
    setSliderX(50);
  }, [restored]);

  if (!restored) {
    return (
      <section className="panel panel-comparison panel-empty">
        <h2 className="panel-title">Before / After</h2>
        <p className="panel-subtitle">Once processed, you&#39;ll be able to compare original vs restored here.</p>
      </section>
    );
  }

  const originalUrl = original;
  const restoredUrl = restored;

  const onPointerDown = e => {
    if (!containerRef.current) return;
    const container = containerRef.current;

    const updateFromEvent = evt => {
      const rect = container.getBoundingClientRect();
      const clientX = evt.touches ? evt.touches[0].clientX : evt.clientX;
      let x = ((clientX - rect.left) / rect.width) * 100;
      x = Math.min(100, Math.max(0, x));
      setSliderX(x);
    };

    const onMove = evt => {
      evt.preventDefault();
      updateFromEvent(evt);
    };

    const onUp = () => {
      window.removeEventListener('pointermove', onMove);
      window.removeEventListener('pointerup', onUp);
      window.removeEventListener('touchmove', onMove);
      window.removeEventListener('touchend', onUp);
    };

    window.addEventListener('pointermove', onMove);
    window.addEventListener('pointerup', onUp);
    window.addEventListener('touchmove', onMove);
    window.addEventListener('touchend', onUp);
  };

  return (
    <section className="panel panel-comparison">
      <div className="panel-header-row">
        <div>
          <h2 className="panel-title">Before / After</h2>
          <p className="panel-subtitle">Slide to reveal AI-restored details.</p>
        </div>
        {restored && (
          <button type="button" className="chip chip-download" onClick={onDownload}>
            ⬇ Download restored
          </button>
        )}
      </div>
      <div className="comparison-container" ref={containerRef}>
        {mediaKind === 'image' ? (
          <>
            <img src={originalUrl} alt="Original" className="comparison-media" />
            <div className="comparison-overlay" style={{ clipPath: `inset(0 0 0 ${sliderX}%)` }}>
              <img src={restoredUrl} alt="Restored" className="comparison-media" />
            </div>
          </>
        ) : (
          <>
            <video src={originalUrl} className="comparison-media" muted loop autoPlay />
            <div className="comparison-overlay" style={{ clipPath: `inset(0 0 0 ${sliderX}%)` }}>
              <video src={restoredUrl} className="comparison-media" muted loop autoPlay />
            </div>
          </>
        )}

        <div
          className="comparison-handle"
          style={{ left: `${sliderX}%` }}
          onMouseDown={onPointerDown}
          onTouchStart={onPointerDown}
        >
          <div className="comparison-handle-line" />
          <div className="comparison-handle-grip">
            <span>◀</span>
            <span>▶</span>
          </div>
        </div>
      </div>
    </section>
  );
}

