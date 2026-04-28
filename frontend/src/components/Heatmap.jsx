import { useState, useEffect } from 'react';
import { api } from '../api';

export default function Heatmap({ sessionId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!sessionId) return;
    api('heatmap', { params: { session_id: sessionId } }).then(setData).finally(() => setLoading(false));
  }, [sessionId]);

  if (loading) return <div className="spinner" />;
  if (!data) return null;

  const maxVal = Math.max(...data.data.flat(), 1);
  const getColor = (val) => {
    const intensity = val / maxVal;
    if (intensity === 0) return 'rgba(48,54,61,0.3)';
    const r = Math.round(37 + (0 - 37) * intensity);
    const g = Math.round(211 * intensity);
    const b = Math.round(102 * intensity);
    return `rgba(${r},${g},${b},${0.2 + intensity * 0.8})`;
  };

  return (
    <div className="fade-in">
      <h2 className="section-title">🔥 Activity Heatmap</h2>
      <div className="card" style={{ overflowX: 'auto' }}>
        <div className="heatmap-grid">
          <div />
          {data.hours.map(h => <div className="heatmap-hour" key={h}>{h}</div>)}
          {data.days.map((day, di) => (
            <>
              <div className="heatmap-label" key={`l-${day}`}>{day.slice(0, 3)}</div>
              {data.data[di].map((val, hi) => (
                <div
                  className="heatmap-cell"
                  key={`${di}-${hi}`}
                  style={{ background: getColor(val) }}
                >
                  <span className="heatmap-tooltip">{day} {hi}:00 — {val} msgs</span>
                </div>
              ))}
            </>
          ))}
        </div>
      </div>
    </div>
  );
}
