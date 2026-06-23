# Kit de monitoring — Agence web

Outil de surveillance pour une agence web qui héberge les sites de ses clients.

## Stack open source

| Conteneur | Image | Version | Licence | Rôle |
|-----------|-------|---------|---------|------|
| **blackbox-exporter** | [prom/blackbox-exporter](https://github.com/prometheus/blackbox_exporter) | v0.25.0 | Apache 2.0 | Sonde HTTP des sites clients |
| **node-exporter** | [prom/node-exporter](https://github.com/prometheus/node_exporter) | v1.7.0 | Apache 2.0 | Métriques système (CPU, RAM, disque) |
| **prometheus** | [prom/prometheus](https://github.com/prometheus/prometheus) | v2.51.0 | Apache 2.0 | Collecte et stockage des métriques |
| **grafana** | [grafana/grafana](https://github.com/grafana/grafana) | v10.4.0 | AGPL 3.0 | Dashboards et visualisation |
| **alertmanager** | [prom/alertmanager](https://github.com/prometheus/alertmanager) | v0.27.0 | Apache 2.0 | Envoi des alertes (email, Discord) |

> Tous les outils sont **open source** et maintenus par la communauté Prometheus / Grafana Labs.

---

## Ce que ça fait

| Besoin | Réponse technique |
|--------|-------------------|
| Est-ce que les sites des clients marchent ? | **Blackbox Exporter** sonde chaque URL toutes les 30 secondes |
| Est-ce qu'ils sont rapides ? | Prometheus mesure le **temps de réponse** de chaque site |
| Est-ce que le serveur va bien ? | **Node Exporter** expose le CPU, la RAM et le disque |
| Alerte quand un site tombe | **Alertmanager** envoie une notification Discord en moins de 2 minutes |

## Architecture

```
                   ┌─────────────────────────────┐
Sites clients ◄──  │  blackbox-exporter (port 9115) │  sonde HTTP toutes les 30s
                   └──────────────┬──────────────┘
                                  │ métriques
Serveur Linux ──►  node-exporter  │  (CPU, RAM, disque)
                                  │
                   ┌──────────────▼──────────────┐
                   │     prometheus (port 9090)   │  collecte + stockage
                   └──────┬───────────────┬───────┘
                          │               │ alertes
             ┌────────────▼───┐   ┌───────▼──────────┐
             │ grafana (:3000) │   │ alertmanager(:9093)│
             │  dashboards     │   │  → Discord/email  │
             └────────────────┘   └──────────────────┘
```

## Démarrage rapide

```bash
# 1. Copier le fichier de configuration
cp .env.example .env
# Éditer .env : renseigner le webhook Discord

# 2. Lancer la stack
docker compose up -d

# 3. Ouvrir Grafana
# http://localhost:3001   login: admin / admin
```

> **Note Linux :** `node-exporter` nécessite les montages `/proc` et `/sys` du système hôte.
> Sur Windows/macOS (Docker Desktop), les métriques serveur ne seront pas disponibles — c'est normal.

## Services et URLs

| Service | URL | Rôle |
|---------|-----|------|
| Grafana | http://localhost:3001 | Dashboards (admin/admin) |
| Prometheus | http://localhost:9090 | Données brutes + alertes |
| Alertmanager | http://localhost:9093 | Statut des notifications |
| Blackbox Exporter | http://localhost:9115 | Résultats des sondes HTTP |
| Node Exporter | http://localhost:9100/metrics | Métriques système brutes |

## Ajouter ou retirer un site à surveiller

Éditer `monitoring/prometheus.yml`, section `targets` :

```yaml
static_configs:
  - targets:
      - https://site-client-1.fr
      - https://site-client-2.com
      - https://nouveau-client.fr   # ← ajouter ici
```

Puis recharger Prometheus sans redémarrer :

```bash
curl -X POST http://localhost:9090/-/reload
```

## Simuler une panne (démo)

```bash
# Ajouter une URL qui ne répond pas dans prometheus.yml
# ex: - https://site-inexistant-demo.xyz

# Dans Prometheus http://localhost:9090/alerts
# → l'alerte "SiteDown" passe en FIRING après 1 minute

# Dans Discord → notification reçue
```

## Structure du projet

```
devops-monitoring/
├── monitoring/
│   ├── prometheus.yml     # configuration Prometheus (cibles à surveiller)
│   ├── alerts.yml         # règles d'alerte (site down, CPU élevé, etc.)
│   ├── alertmanager.yml   # envoi des notifications (Discord, email)
│   └── blackbox.yml       # configuration des sondes HTTP
├── grafana/
│   ├── provisioning/      # configuration automatique au démarrage
│   └── dashboards/        # dashboard JSON (agence-web.json)
├── docker-compose.yml     # déclaration des 5 services
└── .env.example           # variables à renseigner (webhook Discord, etc.)
```

## Comprendre chaque outil

**Prometheus** collecte les métriques en interrogeant les exporters toutes les 30 secondes. Il stocke les données localement et évalue les règles d'alerte.

**Blackbox Exporter** reçoit une URL, fait une requête HTTP GET, et expose deux métriques :
- `probe_success` : 1 si le site répond (code 2xx), 0 sinon
- `probe_duration_seconds` : temps de réponse en secondes

**Node Exporter** lit les fichiers système Linux (`/proc`, `/sys`) et expose des métriques sur le CPU, la RAM, le disque, le réseau.

**Grafana** se connecte à Prometheus comme source de données et affiche les métriques en graphiques. Les dashboards sont définis en JSON et chargés automatiquement au démarrage.

**Alertmanager** reçoit les alertes de Prometheus, les groupe pour éviter le spam, et les envoie sur Discord ou par email selon leur sévérité.
