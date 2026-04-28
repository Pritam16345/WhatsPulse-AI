import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { api } from '../api';

export default function AIAsk({ sessionId }) {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const askQuestion = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;
    setLoading(true);
    setError('');
    setAnswer('');
    try {
      const data = await api('ai/ask', {
        method: 'POST',
        body: { session_id: sessionId, question }
      });
      setAnswer(data.answer);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fade-in">
      <h2 className="section-title">❓ Ask Your Chat</h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: 20 }}>
        Ask Gemini anything about your conversations. Example: "What movies were discussed?" or "Who mentioned cricket?"
      </p>

      <form onSubmit={askQuestion} className="ai-input-wrap">
        <input
          type="text"
          className="ai-input"
          placeholder="Type your question here..."
          value={question}
          onChange={e => setQuestion(e.target.value)}
          disabled={loading}
        />
        <button type="submit" className="btn btn-primary" disabled={loading || !question.trim()}>
          {loading ? 'Asking...' : 'Ask'}
        </button>
      </form>

      {loading && <div className="spinner" />}
      {error && <div className="ai-result" style={{ color: 'var(--danger)', borderLeft: '4px solid var(--danger)' }}>{error}</div>}
      {answer && (
        <div className="ai-result">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{answer}</ReactMarkdown>
        </div>
      )}
      {!loading && !answer && !error && (
        <div className="empty-state">
          <div className="icon">🔍</div>
          <p>Go ahead, ask a question about your chat history.</p>
        </div>
      )}
    </div>
  );
}
