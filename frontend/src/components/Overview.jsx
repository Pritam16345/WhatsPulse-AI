import { useState, useEffect } from 'react';
import { api } from '../api';

function StatCard({ icon, value, label }) {
  return (
    <div className="stat-card">
      <div className="stat-icon">{icon}</div>
      <div className="stat-value">{typeof value === 'number' ? value.toLocaleString() : value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

export default function Overview({ sessionId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!sessionId) return;
    setLoading(true);
    api('overview', { params: { session_id: sessionId } })
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [sessionId]);

  if (loading) return <div className="spinner" />;
  if (!data) return <div className="empty-state"><div className="icon">📊</div><p>No data available</p></div>;

  return (
    <div className="fade-in">
      <h2 className="section-title">📊 Overview</h2>
      <div className="stats-grid">
        <StatCard icon="💬" value={data.total_messages} label="Messages" />
        <StatCard icon="📝" value={data.total_words} label="Words" />
        <StatCard icon="🖼️" value={data.total_media} label="Media" />
        <StatCard icon="🔗" value={data.total_links} label="Links" />
        <StatCard icon="🗑️" value={data.total_deleted} label="Deleted" />
        <StatCard icon="📅" value={data.date_range_days} label="Days Active" />
      </div>
      <div className="stats-grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(220px,1fr))' }}>
        <div className="callout callout-accent">
          <div>🏆</div>
          <div>
            <div style={{ fontWeight: 700 }}>Most Active Day</div>
            <div style={{ fontSize: '.85rem', color: 'var(--text-secondary)' }}>{data.most_active_day} — {data.most_active_day_count} messages</div>
          </div>
        </div>
        <div className="callout callout-purple">
          <div>⚡</div>
          <div>
            <div style={{ fontWeight: 700 }}>Peak Velocity</div>
            <div style={{ fontSize: '.85rem', color: 'var(--text-secondary)' }}>{data.peak_velocity} msgs/hr on peak day</div>
          </div>
        </div>
        <div className="callout callout-accent">
          <div>👥</div>
          <div>
            <div style={{ fontWeight: 700 }}>{data.total_unique_users} Participants</div>
            <div style={{ fontSize: '.85rem', color: 'var(--text-secondary)' }}>{data.avg_messages_per_day} msgs/day avg</div>
          </div>
        </div>
        <div className="callout callout-purple">
          <div>😶</div>
          <div>
            <div style={{ fontWeight: 700 }}>{data.silent_days} Silent Days</div>
            <div style={{ fontSize: '.85rem', color: 'var(--text-secondary)' }}>{data.first_message_date} → {data.last_message_date}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
