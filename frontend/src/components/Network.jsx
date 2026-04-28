import { useState, useEffect, useRef } from 'react';
import { api } from '../api';

import { Network as VisNetwork, DataSet } from 'vis-network/standalone';

export default function Network({ sessionId }) {
  const [loading, setLoading] = useState(true);
  const containerRef = useRef(null);
  const networkRef = useRef(null);

  useEffect(() => {
    if (!sessionId) return;
    api('network', { params: { session_id: sessionId } })
      .then((data) => {
        if (!data.nodes.length) return;
        
        const nodes = new DataSet(data.nodes.map(n => ({
          id: n.id, label: n.label,
          size: 20 + (n.size / Math.max(...data.nodes.map(x => x.size), 1)) * 30,
          color: { background: '#25d366', border: '#1db954', highlight: { background: '#7c3aed', border: '#6d28d9' } },
          font: { color: '#e6edf3', size: 14, face: 'Inter' },
          shape: 'dot'
        })));

        const edges = new DataSet(data.edges.map(e => ({
          from: e.from, to: e.to,
          width: 1 + (e.weight / Math.max(...data.edges.map(x => x.weight), 1)) * 8,
          color: { color: 'rgba(139, 148, 158, 0.5)', highlight: '#25d366' },
          arrows: { to: { enabled: true, scaleFactor: 0.5 } },
          smooth: { type: 'curvedCW', roundness: 0.2 }
        })));

        if (networkRef.current) networkRef.current.destroy();
        networkRef.current = new VisNetwork(containerRef.current, { nodes, edges }, {
          physics: {
            enabled: true,
            barnesHut: { gravitationalConstant: -2000, centralGravity: 0.3, springLength: 150 },
            stabilization: { iterations: 150 }
          },
          interaction: { hover: true, tooltipDelay: 200, zoomView: true, dragView: true }
        });
      })
      .finally(() => setLoading(false));
    return () => { if (networkRef.current) networkRef.current.destroy(); };
  }, [sessionId]);

  if (loading) return <div className="spinner" />;

  return (
    <div className="fade-in">
      <h2 className="section-title">🕸️ Conversation Network</h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: 16 }}>Reply connections between users. Edge thickness = reply frequency.</p>
      <div className="network-container" ref={containerRef} />
    </div>
  );
}
