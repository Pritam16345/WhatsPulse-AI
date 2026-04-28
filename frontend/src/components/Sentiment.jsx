import { useState, useEffect, useRef } from 'react';
import { api } from '../api';
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

const COLORS = ['#25d366','#7c3aed','#f85149','#58a6ff','#d29922','#3fb950','#f778ba','#79c0ff'];

export default function Sentiment({ sessionId }) {
  const [loading, setLoading] = useState(true);
  const chartRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!sessionId) return;
    api('sentiment', { params: { session_id: sessionId } })
      .then(data => {
        if (data.error) return;
        if (chartRef.current) chartRef.current.destroy();
        const datasets = data.datasets.map((ds, i) => ({
          label: ds.user, data: ds.data,
          borderColor: COLORS[i % COLORS.length], backgroundColor: COLORS[i % COLORS.length] + '22',
          tension: 0.3, pointRadius: 0, fill: false,
        }));
        chartRef.current = new Chart(canvasRef.current, {
          type: 'line',
          data: { labels: data.labels, datasets },
          options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { labels: { color: '#8b949e' } } },
            scales: {
              x: { ticks: { color: '#8b949e', maxTicksLimit: 12 }, grid: { color: 'rgba(48,54,61,0.3)' } },
              y: { min: -1, max: 1, ticks: { color: '#8b949e' }, grid: { color: 'rgba(48,54,61,0.3)' }, title: { display: true, text: 'Sentiment', color: '#8b949e' } },
            },
          },
        });
      })
      .finally(() => setLoading(false));
    return () => { if (chartRef.current) chartRef.current.destroy(); };
  }, [sessionId]);

  if (loading) return <div className="spinner" />;

  return (
    <div className="fade-in">
      <h2 className="section-title">💖 Sentiment Analysis</h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: 16 }}>Weekly sentiment score per user (VADER). Range: -1 (negative) to +1 (positive)</p>
      <div className="card"><div className="chart-container"><canvas ref={canvasRef} /></div></div>
    </div>
  );
}
