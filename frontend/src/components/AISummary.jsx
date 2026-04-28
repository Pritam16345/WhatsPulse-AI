import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { api } from '../api';

export default function AISummary({ sessionId, users }) {
  const [period, setPeriod] = useState('all');
  const [user, setUser] = useState('');
  const [summary, setSummary] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const generateSummary = async () => {
    setLoading(true);
    setError('');
    setSummary('');
    try {
      const data = await api('ai/summarize', {
        method: 'POST',
        body: { session_id: sessionId, period, user: user || null }
      });
      setSummary(data.summary);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fade-in">
      <h2 className="section-title">📝 AI Conversation Summary</h2>
      <div className="filter-bar">
        <select value={period} onChange={e => setPeriod(e.target.value)}>
          <option value="all">All Time</option>
          <option value="month">Last Month</option>
          <option value="week">Last Week</option>
        </select>
        <select value={user} onChange={e => setUser(e.target.value)}>
          <option value="">All Users</option>
          {users.map(u => <option key={u} value={u}>{u}</option>)}
        </select>
        <button className="btn btn-primary" onClick={generateSummary} disabled={loading}>
          {loading ? 'Generating...' : 'Generate Summary'}
        </button>
      </div>

      {loading && <div className="spinner" />}
      {error && <div className="ai-result" style={{ color: 'var(--danger)', borderLeft: '4px solid var(--danger)' }}>{error}</div>}
      {summary && (
        <div className="ai-result">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{summary}</ReactMarkdown>
        </div>
      )}
      {!loading && !summary && !error && (
        <div className="empty-state">
          <div className="icon">✨</div>
          <p>Click "Generate Summary" to get AI-powered insights into your chat.</p>
        </div>
      )}
    </div>
  );
}
