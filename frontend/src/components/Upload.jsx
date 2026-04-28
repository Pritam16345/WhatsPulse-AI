import { useState, useRef } from 'react';
import { uploadFile } from '../api';

export default function Upload({ onUploadDone }) {
  const [dragging, setDragging] = useState(false);
  const [progress, setProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const inputRef = useRef();

  const handleFile = async (file) => {
    if (!file) return;
    const name = file.name.toLowerCase();
    if (!name.endsWith('.txt') && !name.endsWith('.zip')) {
      setError('Please upload a .txt or .zip file');
      return;
    }
    setError('');
    setUploading(true);
    setProgress(0);
    try {
      const data = await uploadFile(file, setProgress);
      setProgress(100);
      setTimeout(() => onUploadDone(data), 500);
    } catch (e) {
      setError(e.message);
      setUploading(false);
    }
  };

  const onDrop = (e) => { e.preventDefault(); setDragging(false); handleFile(e.dataTransfer.files[0]); };
  const onDragOver = (e) => { e.preventDefault(); setDragging(true); };
  const onDragLeave = () => setDragging(false);

  return (
    <div
      className={`upload-zone${dragging ? ' dragover' : ''}`}
      onDrop={onDrop} onDragOver={onDragOver} onDragLeave={onDragLeave}
      onClick={() => !uploading && inputRef.current.click()}
    >
      <div className="icon">💬</div>
      <h2>Upload WhatsApp Chat</h2>
      <p>Drag & drop your .txt or .zip export file here, or click to browse</p>
      <input type="file" ref={inputRef} accept=".txt,.zip" onChange={e => handleFile(e.target.files[0])} style={{ display: 'none' }} />
      {!uploading && <button className="upload-btn">Choose File</button>}
      {uploading && (
        <div className="progress-bar-wrap">
          <div className="progress-bar-fill" style={{ width: `${progress}%` }} />
        </div>
      )}
      {error && <p style={{ color: 'var(--danger)', marginTop: 12 }}>{error}</p>}
      <p style={{ marginTop: 20, fontSize: '.8rem', color: 'var(--text-muted)' }}>
        WhatsApp → Chat → ⋮ → More → Export Chat → Without Media
      </p>
    </div>
  );
}
