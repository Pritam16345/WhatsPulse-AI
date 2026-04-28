import { useState, useEffect, useRef } from 'react';
import { api } from '../api';
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

export default function Deleted({ sessionId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const chartRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!sessionId) return;
    api('deleted', { params: { session_id: sessionId } })
      .then(d => {
        setData(d);
        if (chartRef.current) chartRef.current.destroy();
        if (d.per_user?.length) {
          chartRef.current = new Chart(canvasRef.current, {
            type: 'bar',
            data: {
              labels: d.per_user.map(u => u.user),
              datasets: [{ label: 'Deleted', data: d.per_user.map(u => u.count), backgroundColor: '#f85149aa', borderColor: '#f85149', borderWidth: 1, borderRadius: 6 }],
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { ticks: { color: '#8b949e' } }, y: { ticks: { color: '#8b949e' }, grid: { color: 'rgba(48,54,61,0.3)' } } } },
          });
        }
      })
      .finally(() => setLoading(false));
    return () => { if (chartRef.current) chartRef.current.destroy(); };
  }, [sessionId]);

  if (loading) return <div className="spinner" />;
  if (!data?.total_deleted) return <div className="empty-state"><div className="icon">🗑️</div><p>No deleted messages</p></div>;

  return (
    <div className="fade-in">
      <h2 className="section-title">🗑️ Deleted Messages</h2>
      <div className="callout callout-accent"><div>🗑️</div><div><div style={{ fontWeight: 700 }}>{data.total_deleted} Deleted Messages</div></div></div>
      <div className="card"><div className="chart-container"><canvas ref={canvasRef} /></div></div>
    </div>
  );
}
