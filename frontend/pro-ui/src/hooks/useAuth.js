import { useState } from 'react';

const STORAGE_KEY = 'monitoring_token';

export function useAuth() {
  const [token, setToken] = useState(() => localStorage.getItem(STORAGE_KEY));

  const login = (newToken) => {
    localStorage.setItem(STORAGE_KEY, newToken);
    setToken(newToken);
  };

  const logout = () => {
    localStorage.removeItem(STORAGE_KEY);
    setToken(null);
  };

  return { token, login, logout };
}
