import { useState, useEffect, useRef } from 'react';
import { api } from '../api';
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

const COLORS = ['#25d366','#7c3aed','#f85149','#58a6ff','#d29922','#3fb950','#f778ba','#79c0ff','#ffa657','#a5d6ff'];

export default function Timeline({ sessionId, users }) {
  const [gran, setGran] = useState('daily');
  const [user, setUser] = useState(null);
  const chartRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!sessionId) return;
    api('timeline', { params: { session_id: sessionId, granularity: gran, user } })
      .then(data => {
        if (chartRef.current) chartRef.current.destroy();
        const datasets = data.datasets.map((ds, i) => ({
          label: ds.user,
          data: ds.data,
          borderColor: COLORS[i % COLORS.length],
          backgroundColor: COLORS[i % COLORS.length] + '22',
          fill: data.datasets.length === 1,
          tension: 0.3,
          pointRadius: data.labels.length > 60 ? 0 : 3,
        }));
        chartRef.current = new Chart(canvasRef.current, {
          type: 'line',
          data: { labels: data.labels, datasets },
          options: {
            responsive: true, maintainAspectRatio: false,
            animation: { duration: 600 },
            plugins: { legend: { labels: { color: 'var(--text-primary)' } } },
            scales: {
              x: { ticks: { color: '#8b949e', maxTicksLimit: 15 }, grid: { color: 'rgba(48,54,61,0.3)' } },
              y: { ticks: { color: '#8b949e' }, grid: { color: 'rgba(48,54,61,0.3)' } },
            },
          },
        });
      });
    return () => { if (chartRef.current) chartRef.current.destroy(); };
  }, [sessionId, gran, user]);

  return (
    <div className="fade-in">
      <h2 className="section-title">📈 Timeline</h2>
      <div className="filter-bar">
        {['daily', 'weekly', 'monthly'].map(g => (
          <button key={g} className={`btn btn-secondary${gran === g ? ' active' : ''}`} onClick={() => setGran(g)}>
            {g.charAt(0).toUpperCase() + g.slice(1)}
          </button>
        ))}
        <select value={user || ''} onChange={e => setUser(e.target.value || null)}>
          <option value="">All Users</option>
          {users?.map(u => <option key={u} value={u}>{u}</option>)}
        </select>
      </div>
      <div className="card">
        <div className="chart-container"><canvas ref={canvasRef} /></div>
      </div>
    </div>
  );
}
