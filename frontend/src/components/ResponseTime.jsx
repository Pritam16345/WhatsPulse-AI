import { useState, useEffect, useRef } from 'react';
import { api } from '../api';
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

export default function ResponseTime({ sessionId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const chartRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!sessionId) return;
    api('response_time', { params: { session_id: sessionId } })
      .then(d => {
        setData(d);
        if (chartRef.current) chartRef.current.destroy();
        const users = Object.keys(d.per_user || {});
        const avgs = users.map(u => d.per_user[u].avg_minutes);
        chartRef.current = new Chart(canvasRef.current, {
          type: 'bar',
          data: {
            labels: users,
            datasets: [{ label: 'Avg Response (min)', data: avgs, backgroundColor: '#7c3aedaa', borderColor: '#7c3aed', borderWidth: 1, borderRadius: 6 }],
          },
          options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
              x: { ticks: { color: '#8b949e' }, grid: { display: false } },
              y: { ticks: { color: '#8b949e' }, grid: { color: 'rgba(48,54,61,0.3)' }, title: { display: true, text: 'Minutes', color: '#8b949e' } },
            },
          },
        });
      })
      .finally(() => setLoading(false));
    return () => { if (chartRef.current) chartRef.current.destroy(); };
  }, [sessionId]);

  if (loading) return <div className="spinner" />;
  if (!data?.per_user || !Object.keys(data.per_user).length) return <div className="empty-state"><div className="icon">⏱️</div><p>Not enough data</p></div>;

  const sorted = Object.entries(data.per_user).sort((a, b) => a[1].avg_minutes - b[1].avg_minutes);
  const fastest = sorted[0];
  const slowest = sorted[sorted.length - 1];

  return (
    <div className="fade-in">
      <h2 className="section-title">⏱️ Response Time</h2>
      <div className="stats-grid" style={{ gridTemplateColumns: 'repeat(auto-fit,minmax(220px,1fr))' }}>
        <div className="callout callout-accent"><div>🏃</div><div><div style={{ fontWeight: 700 }}>Fastest: {fastest[0]}</div><div style={{ fontSize: '.85rem', color: 'var(--text-secondary)' }}>{fastest[1].avg_minutes} min avg</div></div></div>
        <div className="callout callout-purple"><div>🐌</div><div><div style={{ fontWeight: 700 }}>Slowest: {slowest[0]}</div><div style={{ fontSize: '.85rem', color: 'var(--text-secondary)' }}>{slowest[1].avg_minutes} min avg</div></div></div>
      </div>
      <div className="card"><div className="chart-container"><canvas ref={canvasRef} /></div></div>
    </div>
  );
}
