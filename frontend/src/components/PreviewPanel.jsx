import React from 'react';

export function PreviewPanel({ media, processing }) {
  if (!media?.file) {
    return (
      <section className="panel panel-preview panel-empty">
        <h2 className="panel-title">Preview</h2>
        <p className="panel-subtitle">Your media preview will appear here once you upload a file.</p>
      </section>
    );
  }

  const url = URL.createObjectURL(media.file);

  return (
    <section className="panel panel-preview">
      <div className="panel-header-row">
        <div>
          <h2 className="panel-title">Original</h2>
          <p className="panel-subtitle">
            {media.file.name} · {(media.file.size / (1024 * 1024)).toFixed(2)} MB · {media.kind.toUpperCase()}
          </p>
        </div>
        {processing && <span className="pill pill-processing">Processing…</span>}
      </div>
      <div className="preview-media-container">
        {media.kind === 'image' ? (
          <img src={url} alt={media.file.name} className="preview-media" />
        ) : (
          <video src={url} controls className="preview-media" />
        )}
      </div>
    </section>
  );
}

