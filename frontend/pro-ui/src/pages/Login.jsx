import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import client from '../api/client.js';
import { useAuth } from '../hooks/useAuth.js';

export default function Login() {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await client.post('/auth/login', { username, password });
      login(res.data.access_token);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Erreur de connexion');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <form className="login-card" onSubmit={handleSubmit}>
        <h1>DevOps Monitoring</h1>
        <p className="subtitle">Connexion à la plateforme</p>

        <label>
          Utilisateur
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </label>

        <label>
          Mot de passe
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>

        {error && <div className="error">{error}</div>}

        <button type="submit" disabled={loading} className="btn-primary">
          {loading ? 'Connexion...' : 'Se connecter'}
        </button>

        <div className="hint">Démo : admin / admin123</div>
      </form>
    </div>
  );
}
