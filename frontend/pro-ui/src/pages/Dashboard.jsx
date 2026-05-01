import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import client from '../api/client.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const REFRESH_INTERVAL = 15000; // 15s

export default function Dashboard() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [lastRefresh, setLastRefresh] = useState(null);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await client.get('/monitor');
      setResults(res.data.results || []);
      setLastRefresh(new Date());
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const id = setInterval(fetchData, REFRESH_INTERVAL);
    return () => clearInterval(id);
  }, [fetchData]);

  const stats = useMemo(() => {
    const up = results.filter((r) => r.status === 'UP').length;
    const down = results.filter((r) => r.status === 'DOWN').length;
    const degraded = results.filter((r) => r.status === 'DEGRADED').length;
    const avgLatency = results.length
      ? (results.reduce((s, r) => s + (r.latency_s || 0), 0) / results.length).toFixed(3)
      : 0;
    return { up, down, degraded, avgLatency, total: results.length };
  }, [results]);

  const chartData = useMemo(
    () => ({
      labels: results.map((r) => r.site.replace('https://', '')),
      datasets: [
        {
          label: 'Latence (s)',
          data: results.map((r) => r.latency_s),
          backgroundColor: results.map((r) =>
            r.status === 'UP' ? '#22c55e' : r.status === 'DEGRADED' ? '#f59e0b' : '#ef4444',
          ),
        },
      ],
    }),
    [results],
  );

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Statut des services surveillés</h2>
        <div className="actions">
          {lastRefresh && (
            <span className="muted">
              Dernier refresh : {lastRefresh.toLocaleTimeString()}
            </span>
          )}
          <button onClick={fetchData} disabled={loading} className="btn-primary">
            {loading ? 'Refresh...' : 'Refresh now'}
          </button>
        </div>
      </div>

      {error && <div className="error">Erreur : {error}</div>}

      <div className="stats-grid">
        <StatCard label="Total" value={stats.total} />
        <StatCard label="UP" value={stats.up} className="green" />
        <StatCard label="DEGRADED" value={stats.degraded} className="orange" />
        <StatCard label="DOWN" value={stats.down} className="red" />
        <StatCard label="Latence moy." value={`${stats.avgLatency} s`} />
      </div>

      <div className="card chart-card">
        <h3>Latence par site</h3>
        <Bar
          data={chartData}
          options={{
            responsive: true,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true } },
          }}
        />
      </div>

      <div className="card">
        <h3>Détails</h3>
        <table className="table">
          <thead>
            <tr>
              <th>Site</th>
              <th>Statut</th>
              <th>Latence</th>
              <th>Heure</th>
            </tr>
          </thead>
          <tbody>
            {results.map((r) => (
              <tr key={r.site}>
                <td>{r.site}</td>
                <td>
                  <span className={`badge ${r.status.toLowerCase()}`}>{r.status}</span>
                </td>
                <td>{r.latency_s} s</td>
                <td>{new Date(r.time).toLocaleTimeString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function StatCard({ label, value, className = '' }) {
  return (
    <div className={`stat-card ${className}`}>
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
    </div>
  );
}
