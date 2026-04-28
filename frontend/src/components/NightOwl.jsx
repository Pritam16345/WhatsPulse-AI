import { useState, useEffect } from 'react';
import { api } from '../api';

export default function NightOwl({ sessionId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!sessionId) return;
    api('night_owl', { params: { session_id: sessionId } }).then(setData).finally(() => setLoading(false));
  }, [sessionId]);

  if (loading) return <div className="spinner" />;
  if (!data?.per_user?.length) return <div className="empty-state"><div className="icon">🌙</div><p>No night owl data</p></div>;

  return (
    <div className="fade-in">
      <h2 className="section-title">🌙 Night Owl Analysis</h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: 16 }}>Messages sent between 12 AM – 4 AM</p>
      <div className="callout callout-purple"><div>🌙</div><div><div style={{ fontWeight: 700 }}>{data.total_night_messages} Late Night Messages</div></div></div>
      <div className="users-grid">
        {data.per_user.filter(u => u.night_messages > 0).map((u, i) => (
          <div className="user-card" key={i}>
            <div className="user-card-header">
              <div className="user-avatar" style={{ background: i === 0 ? '#7c3aed' : '#25d366' }}>🌙</div>
              <div>
                <div className="user-name">{u.user} {i === 0 && '👑'}</div>
                <div style={{ fontSize: '.8rem', color: 'var(--text-muted)' }}>Night Owl Score: {u.night_pct}%</div>
              </div>
            </div>
            <div className="user-stats-grid">
              <div className="user-stat"><div className="user-stat-val">{u.night_messages}</div><div className="user-stat-label">Night Msgs</div></div>
              <div className="user-stat"><div className="user-stat-val">{u.night_pct}%</div><div className="user-stat-label">Of Their Total</div></div>
              <div className="user-stat"><div className="user-stat-val">{u.total_messages}</div><div className="user-stat-label">Total Msgs</div></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
