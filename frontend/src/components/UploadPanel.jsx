import React, { useCallback, useRef, useState } from 'react';

const MEDIA_TYPES = {
  image: ['image/png', 'image/jpeg', 'image/jpg', 'image/webp'],
  video: ['video/mp4', 'video/webm', 'video/quicktime'],
};

function getMediaKind(file) {
  if (!file) return null;
  if (MEDIA_TYPES.image.includes(file.type)) return 'image';
  if (MEDIA_TYPES.video.includes(file.type)) return 'video';
  if (file.type.startsWith('image/')) return 'image';
  if (file.type.startsWith('video/')) return 'video';
  return null;
}

export function UploadPanel({ onFileSelected }) {
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const handleFiles = useCallback(
    files => {
      const file = files?.[0];
      if (!file) return;

      const kind = getMediaKind(file);
      if (!kind) {
        setError('Unsupported file type. Please upload an image (JPG, PNG, WEBP) or video (MP4, WEBM).');
        return;
      }

      setError('');
      onFileSelected?.({ file, kind });
    },
    [onFileSelected],
  );

  const onDrop = e => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    const dt = e.dataTransfer;
    if (dt?.files?.length) {
      handleFiles(dt.files);
    }
  };

  const onDragOver = e => {
    e.preventDefault();
    e.stopPropagation();
    if (!isDragging) setIsDragging(true);
  };

  const onDragLeave = e => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const onBrowseClick = () => {
    fileInputRef.current?.click();
  };

  const onInputChange = e => {
    if (e.target.files?.length) {
      handleFiles(e.target.files);
    }
  };

  return (
    <section className="panel panel-upload">
      <div
        className={`dropzone ${isDragging ? 'dropzone-active' : ''}`}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
      >
        <div className="dropzone-inner">
          <div className="dropzone-orbit">
            <div className="dropzone-orbit-inner" />
          </div>
          <div 
            className="dropzone-icon" 
            onClick={onBrowseClick}
            style={{ cursor: 'pointer' }}
            title="Cliquez pour sélectionner un fichier"
          >
            ⬆
          </div>
          <h2 className="panel-title">Drop your media</h2>
          <p className="panel-subtitle">
            Drag &amp; drop degraded images or videos, or{' '}
            <button type="button" className="link-button" onClick={onBrowseClick}>
              browse files
            </button>
          </p>
          <p className="panel-hint">JPG · PNG · WEBP · MP4 · WEBM · MOV · up to 200MB</p>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*,video/*"
          className="sr-only"
          onChange={onInputChange}
        />
      </div>
      {error && <p className="panel-error">{error}</p>}
    </section>
  );
}

