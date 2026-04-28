import { useState, useEffect, useRef } from 'react';
import { api } from '../api';
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

export default function Links({ sessionId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const chartRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!sessionId) return;
    api('urls', { params: { session_id: sessionId } })
      .then(d => {
        setData(d);
        if (chartRef.current) chartRef.current.destroy();
        const plat = d.platform_breakdown || {};
        const labels = Object.keys(plat);
        const colors = ['#25d366','#7c3aed','#f85149','#58a6ff','#d29922','#3fb950','#f778ba','#79c0ff'];
        if (labels.length) {
          chartRef.current = new Chart(canvasRef.current, {
            type: 'doughnut',
            data: { labels, datasets: [{ data: Object.values(plat), backgroundColor: colors.slice(0, labels.length), borderWidth: 0 }] },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#8b949e' } } } },
          });
        }
      })
      .finally(() => setLoading(false));
    return () => { if (chartRef.current) chartRef.current.destroy(); };
  }, [sessionId]);

  if (loading) return <div className="spinner" />;
  if (!data || !data.total_urls) return <div className="empty-state"><div className="icon">🔗</div><p>No links shared</p></div>;

  return (
    <div className="fade-in">
      <h2 className="section-title">🔗 Link Analysis</h2>
      <div className="callout callout-accent"><div>🔗</div><div><div style={{ fontWeight: 700 }}>{data.total_urls} Total Links Shared</div></div></div>
      <div className="two-col">
        <div className="card"><h3 style={{ marginBottom: 12 }}>Platform Breakdown</h3><div className="chart-container" style={{ minHeight: 250 }}><canvas ref={canvasRef} /></div></div>
        <div className="card"><h3 style={{ marginBottom: 12 }}>Top Domains</h3>
          {data.top_domains.map((d, i) => (
            <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid var(--border)' }}>
              <span>{d.domain}</span><span style={{ color: 'var(--accent)', fontWeight: 700 }}>{d.count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
