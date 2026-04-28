import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { api } from '../api';

export default function AIPersonality({ sessionId }) {
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const generateProfiles = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await api('ai/personality', { params: { session_id: sessionId } });
      setProfiles(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fade-in">
      <h2 className="section-title">🎭 User Personality Profiles</h2>
      <div className="filter-bar">
        <button className="btn btn-primary" onClick={generateProfiles} disabled={loading}>
          {loading ? 'Analyzing...' : 'Generate Personality Profiles'}
        </button>
      </div>

      {loading && <div className="spinner" />}
      {error && <div className="ai-result" style={{ color: 'var(--danger)' }}>{error}</div>}

      <div className="users-grid">
        {profiles.map((p, i) => (
          <div className="card" key={i} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div className="user-avatar" style={{ background: 'var(--accent2)' }}>
                {p.user.charAt(0).toUpperCase()}
              </div>
              <div className="user-name">{p.user}</div>
            </div>
            <div className="profile-text">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{p.profile_text}</ReactMarkdown>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {p.traits.map((t, j) => (
                <span key={j} className="trait-badge">{t}</span>
              ))}
            </div>
            <div className="user-stats-grid" style={{ marginTop: 10 }}>
              <div className="user-stat">
                <div className="user-stat-val">{p.stats.avg_words}</div>
                <div className="user-stat-label">Words/Msg</div>
              </div>
              <div className="user-stat">
                <div className="user-stat-val">{p.stats.emoji_rate}</div>
                <div className="user-stat-label">Emojis/Msg</div>
              </div>
              <div className="user-stat">
                <div className="user-stat-val">{p.stats.peak_hour}:00</div>
                <div className="user-stat-label">Peak Hour</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {!loading && !profiles.length && !error && (
        <div className="empty-state">
          <div className="icon">🎭</div>
          <p>Analyze user messaging patterns to generate fun personality profiles.</p>
        </div>
      )}
    </div>
  );
}
