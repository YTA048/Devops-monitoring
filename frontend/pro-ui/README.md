# Frontend — DevOps Monitoring

App React 18 + Vite consommant l'API FastAPI du backend.

## Dev local

```bash
npm install
npm run dev
```

Ouvre http://localhost:3000.

## Build production

```bash
npm run build      # génère dist/
npm run preview    # sert dist/ sur :80
```

## Variables d'environnement

- `VITE_API_URL` : URL de l'API backend (défaut `http://localhost:8000`).

## Démo login

- Utilisateur : `admin`
- Mot de passe : `admin123`
