import { useState, useEffect } from 'react';
import { api } from '../api';

const COLORS = ['#25d366','#7c3aed','#f85149','#58a6ff','#d29922','#3fb950','#f778ba','#79c0ff','#ffa657','#a5d6ff'];

export default function Users({ sessionId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!sessionId) return;
    api('users', { params: { session_id: sessionId } }).then(setData).finally(() => setLoading(false));
  }, [sessionId]);

  if (loading) return <div className="spinner" />;
  if (!data?.length) return <div className="empty-state"><div className="icon">👥</div><p>No user data</p></div>;

  return (
    <div className="fade-in">
      <h2 className="section-title">👥 User Statistics</h2>
      <div className="users-grid">
        {data.map((u, i) => (
          <div className="user-card" key={u.name}>
            <div className="user-card-header">
              <div className="user-avatar" style={{ background: COLORS[i % COLORS.length] }}>
                {u.name.charAt(0).toUpperCase()}
              </div>
              <div>
                <div className="user-name">{u.name}</div>
                <div style={{ fontSize: '.8rem', color: 'var(--text-muted)' }}>{u.message_pct}% of messages • Streak: {u.longest_streak}d</div>
              </div>
            </div>
            <div className="user-stats-grid">
              <div className="user-stat"><div className="user-stat-val">{u.message_count}</div><div className="user-stat-label">Messages</div></div>
              <div className="user-stat"><div className="user-stat-val">{u.word_count}</div><div className="user-stat-label">Words</div></div>
              <div className="user-stat"><div className="user-stat-val">{u.avg_words_per_msg}</div><div className="user-stat-label">Avg Words</div></div>
              <div className="user-stat"><div className="user-stat-val">{u.media_count}</div><div className="user-stat-label">Media</div></div>
              <div className="user-stat"><div className="user-stat-val">{u.emoji_count}</div><div className="user-stat-label">Emojis</div></div>
              <div className="user-stat"><div className="user-stat-val">{u.link_count}</div><div className="user-stat-label">Links</div></div>
              <div className="user-stat"><div className="user-stat-val">{u.deleted_count}</div><div className="user-stat-label">Deleted</div></div>
              <div className="user-stat"><div className="user-stat-val">{u.questions_asked}</div><div className="user-stat-label">Questions</div></div>
              <div className="user-stat"><div className="user-stat-val">{u.caps_messages}</div><div className="user-stat-label">CAPS</div></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
