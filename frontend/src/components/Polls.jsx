import { useState, useEffect } from 'react';
import { api } from '../api';

export default function Polls({ sessionId }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!sessionId) return;
    api('polls', { params: { session_id: sessionId } }).then(setData).finally(() => setLoading(false));
  }, [sessionId]);

  if (loading) return <div className="spinner" />;
  if (!data.length) return <div className="empty-state"><div className="icon">📋</div><p>No polls found in this chat</p></div>;

  return (
    <div className="fade-in">
      <h2 className="section-title">📋 Polls</h2>
      {data.map((poll, i) => (
        <div className="poll-card" key={i}>
          <div className="poll-title">📊 {poll.title}</div>
          <div style={{ fontSize: '.8rem', color: 'var(--text-muted)', marginBottom: 12 }}>by {poll.user} • {poll.date} • {poll.total_votes} votes</div>
          {poll.options.map((opt, j) => {
            const pct = poll.total_votes > 0 ? (opt.votes / poll.total_votes * 100) : 0;
            return (
              <div className="poll-option" key={j}>
                <div className="poll-bar-bg">
                  <div className="poll-bar-fill" style={{ width: `${pct}%`, background: `linear-gradient(90deg, #25d366, #1db954)` }}>
                    {opt.option}
                  </div>
                </div>
                <div className="poll-votes">{opt.votes} votes</div>
              </div>
            );
          })}
        </div>
      ))}
    </div>
  );
}
