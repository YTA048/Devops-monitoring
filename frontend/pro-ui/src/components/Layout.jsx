import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth.js';

export default function Layout({ children }) {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="app">
      <header className="topbar">
        <h1 className="brand">DevOps Monitoring</h1>
        <nav className="links">
          <Link to="/">Dashboard</Link>
          <a href="http://localhost:9090" target="_blank" rel="noreferrer">Prometheus</a>
          <a href="http://localhost:3001" target="_blank" rel="noreferrer">Grafana</a>
          <a href="http://localhost:16686" target="_blank" rel="noreferrer">Jaeger</a>
          <a href="http://localhost:5601" target="_blank" rel="noreferrer">Kibana</a>
          <a href="http://localhost:9093" target="_blank" rel="noreferrer">AlertManager</a>
        </nav>
        <button onClick={handleLogout} className="btn-secondary">Logout</button>
      </header>
      <main className="main">{children}</main>
    </div>
  );
}
