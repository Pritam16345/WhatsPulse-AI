import { useState, useEffect, useRef } from 'react';
import { api } from '../api';
import { Chart, registerables } from 'chart.js';
import WordCloud from 'wordcloud';
Chart.register(...registerables);

export default function Words({ sessionId, users }) {
  const [data, setData] = useState([]);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const chartRef = useRef(null);
  const canvasRef = useRef(null);
  const cloudRef = useRef(null);

  useEffect(() => {
    if (!sessionId) return;
    setLoading(true);
    api('words', { params: { session_id: sessionId, user } })
      .then(d => {
        setData(d);
        if (chartRef.current) chartRef.current.destroy();
        chartRef.current = new Chart(canvasRef.current, {
          type: 'bar',
          data: {
            labels: d.map(w => w.word),
            datasets: [{ label: 'Count', data: d.map(w => w.count), backgroundColor: '#25d366aa', borderColor: '#25d366', borderWidth: 1, borderRadius: 4 }],
          },
          options: {
            indexAxis: 'y', responsive: true, maintainAspectRatio: false,
            animation: { duration: 600 },
            plugins: { legend: { display: false } },
            scales: {
              x: { ticks: { color: '#8b949e' }, grid: { color: 'rgba(48,54,61,0.3)' } },
              y: { ticks: { color: '#8b949e', font: { size: 11 } }, grid: { display: false } },
            },
          },
        });

        // Word Cloud
        if (d.length > 0) {
          const list = d.map(w => [w.word, w.count]);
          WordCloud(cloudRef.current, {
            list,
            fontFamily: 'Inter, sans-serif',
            color: () => ['#25d366', '#7c3aed', '#58a6ff', '#d29922'][Math.floor(Math.random() * 4)],
            rotateRatio: 0.5,
            rotationSteps: 2,
            backgroundColor: 'transparent',
            gridSize: 8,
            weightFactor: (size) => (size * 50) / d[0].count,
            shrinkToFit: true,
          });
        }
      })
      .finally(() => setLoading(false));
    return () => { if (chartRef.current) chartRef.current.destroy(); };
  }, [sessionId, user]);

  if (loading && !data.length) return <div className="spinner" />;

  return (
    <div className="fade-in">
      <h2 className="section-title">💬 Word Frequency</h2>
      <div className="filter-bar">
        <select value={user || ''} onChange={e => setUser(e.target.value || null)}>
          <option value="">All Users</option>
          {users?.map(u => <option key={u} value={u}>{u}</option>)}
        </select>
      </div>
      <div className="two-col">
        <div className="card">
          <h3 style={{ marginBottom: 12 }}>Top Words</h3>
          <div className="chart-container" style={{ minHeight: Math.max(400, data.length * 20) }}>
            <canvas ref={canvasRef} />
          </div>
        </div>
        <div className="card">
          <h3 style={{ marginBottom: 12 }}>Word Cloud</h3>
          <div style={{ width: '100%', height: '400px' }} ref={cloudRef}></div>
        </div>
      </div>
    </div>
  );
}
