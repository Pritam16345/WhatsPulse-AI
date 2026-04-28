export default function ExportSection({ sessionId }) {
  const exportUrl = (type) => `/api/export/${type}?session_id=${sessionId}`;

  return (
    <div className="fade-in">
      <h2 className="section-title">💾 Export Analysis</h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: 30 }}>
        Download your processed chat data and analysis results for offline use.
      </p>

      <div className="export-grid">
        <div className="card export-card">
          <div className="icon">📊</div>
          <h3 style={{ marginBottom: 10 }}>Full Analysis (JSON)</h3>
          <p>Export all statistics, word frequencies, emoji counts, and heatmap data in a structured JSON format.</p>
          <a href={exportUrl('json')} className="btn btn-primary" download>Download JSON</a>
        </div>

        <div className="card export-card">
          <div className="icon">📄</div>
          <h3 style={{ marginBottom: 10 }}>Parsed Messages (CSV)</h3>
          <p>Download the cleaned and parsed chat history as a CSV file, compatible with Excel or Google Sheets.</p>
          <a href={exportUrl('csv')} className="btn btn-primary" download>Download CSV</a>
        </div>
      </div>
    </div>
  );
}
