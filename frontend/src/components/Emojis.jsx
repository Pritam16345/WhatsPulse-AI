import { useState, useEffect } from 'react';
import { api } from '../api';

export default function Emojis({ sessionId, users }) {
  const [data, setData] = useState([]);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!sessionId) return;
    setLoading(true);
    api('emojis', { params: { session_id: sessionId, user } }).then(setData).finally(() => setLoading(false));
  }, [sessionId, user]);

  if (loading) return <div className="spinner" />;

  return (
    <div className="fade-in">
      <h2 className="section-title">😀 Emoji Analysis</h2>
      <div className="filter-bar">
        <select value={user || ''} onChange={e => setUser(e.target.value || null)}>
          <option value="">All Users</option>
          {users?.map(u => <option key={u} value={u}>{u}</option>)}
        </select>
      </div>
      {!data.length ? (
        <div className="empty-state"><div className="icon">😶</div><p>No emojis found</p></div>
      ) : (
        <div className="emoji-grid">
          {data.map((e, i) => (
            <div className="emoji-card" key={i}>
              <div className="emoji-big">{e.emoji}</div>
              <div className="emoji-count">{e.count}</div>
              <div className="emoji-name">{e.name}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
