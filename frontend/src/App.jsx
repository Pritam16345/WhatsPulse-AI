import { useState, useCallback } from 'react';
import './index.css';
import Upload from './components/Upload';
import Overview from './components/Overview';
import Users from './components/Users';
import Timeline from './components/Timeline';
import Heatmap from './components/Heatmap';
import Words from './components/Words';
import Emojis from './components/Emojis';
import ResponseTime from './components/ResponseTime';
import Sentiment from './components/Sentiment';
import Network from './components/Network';
import Links from './components/Links';
import MediaSection from './components/MediaSection';
import Deleted from './components/Deleted';
import NightOwl from './components/NightOwl';
import Polls from './components/Polls';
import AISummary from './components/AISummary';
import AIAsk from './components/AIAsk';
import AIPersonality from './components/AIPersonality';
import ExportSection from './components/ExportSection';

const NAV = [
  { id: 'upload', icon: '📤', label: 'Upload', always: true },
  { type: 'label', text: 'Analytics' },
  { id: 'overview', icon: '📊', label: 'Overview' },
  { id: 'users', icon: '👥', label: 'Users' },
  { id: 'timeline', icon: '📈', label: 'Timeline' },
  { id: 'heatmap', icon: '🔥', label: 'Heatmap' },
  { id: 'words', icon: '💬', label: 'Words' },
  { id: 'emojis', icon: '😀', label: 'Emojis' },
  { id: 'response', icon: '⏱️', label: 'Response' },
  { id: 'sentiment', icon: '💖', label: 'Sentiment' },
  { id: 'network', icon: '🕸️', label: 'Network' },
  { id: 'links', icon: '🔗', label: 'Links' },
  { id: 'media', icon: '🖼️', label: 'Media' },
  { id: 'deleted', icon: '🗑️', label: 'Deleted' },
  { id: 'nightowl', icon: '🌙', label: 'Night Owl' },
  { id: 'polls', icon: '📋', label: 'Polls' },
  { type: 'label', text: 'AI ✨' },
  { id: 'ai-summary', icon: '📝', label: 'Summary' },
  { id: 'ai-ask', icon: '❓', label: 'Ask Chat' },
  { id: 'ai-personality', icon: '🎭', label: 'Profiles' },
  { type: 'label', text: 'Export' },
  { id: 'export', icon: '💾', label: 'Export' },
];

const SECTIONS = {
  upload: Upload, overview: Overview, users: Users, timeline: Timeline,
  heatmap: Heatmap, words: Words, emojis: Emojis, response: ResponseTime,
  sentiment: Sentiment, network: Network, links: Links, media: MediaSection,
  deleted: Deleted, nightowl: NightOwl, polls: Polls,
  'ai-summary': AISummary, 'ai-ask': AIAsk, 'ai-personality': AIPersonality,
  export: ExportSection,
};

export default function App() {
  const [section, setSection] = useState('upload');
  const [sessionId, setSessionId] = useState(null);
  const [users, setUsers] = useState([]);
  const [uploadInfo, setUploadInfo] = useState(null);
  const [dark, setDark] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const onUploadDone = useCallback((data) => {
    setSessionId(data.session_id);
    setUsers(data.users);
    setUploadInfo(data);
    setSection('overview');
  }, []);

  const toggleTheme = () => {
    setDark(d => !d);
    document.documentElement.setAttribute('data-theme', dark ? 'light' : 'dark');
  };

  const navigate = (id) => {
    if (!sessionId && id !== 'upload') return;
    setSection(id);
    setSidebarOpen(false);
  };

  const SectionComponent = SECTIONS[section] || Upload;

  return (
    <>
      <header className="header">
        <div className="header-left">
          <button className="hamburger" onClick={() => setSidebarOpen(o => !o)} aria-label="Toggle sidebar">
            <span /><span /><span />
          </button>
          <div className="logo">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
            </svg>
            <h1>WhatsPulse AI</h1>
          </div>
        </div>
        <div className="header-right">
          {uploadInfo && <div className="upload-badge">{uploadInfo.total_messages} msgs • {uploadInfo.date_range}</div>}
          <button className="theme-toggle" onClick={toggleTheme} aria-label="Toggle theme">
            {dark ? '☀️' : '🌙'}
          </button>
        </div>
      </header>

      <aside className={`sidebar${sidebarOpen ? ' open' : ''}`}>
        <nav>
          {NAV.map((item, i) =>
            item.type === 'label' ? (
              <div className="nav-group-label" key={i}>{item.text}</div>
            ) : (
              <div
                key={item.id}
                className={`nav-item${section === item.id ? ' active' : ''}${!sessionId && !item.always ? ' disabled' : ''}`}
                onClick={() => navigate(item.id)}
              >
                <span className="nav-icon">{item.icon}</span>
                <span className="nav-label">{item.label}</span>
              </div>
            )
          )}
        </nav>
      </aside>

      {sidebarOpen && <div className="sidebar-overlay open" onClick={() => setSidebarOpen(false)} />}

      <main className="main">
        <div className="fade-in" key={section}>
          <SectionComponent sessionId={sessionId} users={users} onUploadDone={onUploadDone} />
        </div>
      </main>
    </>
  );
}
