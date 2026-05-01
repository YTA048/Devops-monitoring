# Architecture détaillée

## Vue d'ensemble

La plateforme suit une architecture microservices conteneurisée, avec une séparation claire entre l'**application** (frontend + backend + base de données) et la **stack d'observabilité** (Prometheus + Grafana + ELK + Jaeger + AlertManager).

Tous les services communiquent via un réseau Docker dédié `monitoring`.

---

## Diagramme de flux

```
                     ┌──────────────────┐
                     │   Utilisateur    │
                     └────────┬─────────┘
                              │ HTTPS (en prod) / HTTP (dev)
                              ▼
                     ┌──────────────────┐
                     │ React (nginx :80)│
                     │  /login          │
                     │  /dashboard      │
                     └────────┬─────────┘
                              │ REST + JWT
                              ▼
              ┌────────────────────────────────┐
              │  FastAPI Backend (uvicorn:8000)│
              │  /auth/login, /monitor, /...   │
              │  /metrics  /health  /ready     │
              └─┬──────────┬───────────┬───────┘
                │          │           │
       métriques│          │ logs JSON │ traces OTLP gRPC
        (scrape)│          │ (TCP)     │ (port 4317)
                ▼          ▼           ▼
        ┌────────────┐ ┌─────────┐ ┌────────┐
        │ Prometheus │ │Logstash │ │ Jaeger │
        │  :9090     │ │ :5000   │ │ :16686 │
        └─────┬──────┘ └────┬────┘ └────────┘
              │             │
              ▼             ▼
        ┌──────────┐ ┌───────────────┐ ┌────────┐
        │ Grafana  │ │ Elasticsearch │ │ Kibana │
        │  :3001   │ │ :9200         │ │ :5601  │
        └──────────┘ └───────────────┘ └────────┘
              │
              ▼
        ┌──────────────┐
        │ AlertManager │
        │  :9093       │
        └──────┬───────┘
               │ webhook / slack / email
               ▼
        notifications
```

---

## Les 3 piliers de l'observabilité

### 1. Métriques (Prometheus)

- Le backend expose `/metrics` au format texte Prometheus, instrumenté automatiquement via `prometheus-fastapi-instrumentator`.
- Métriques exposées : `http_requests_total`, `http_request_duration_seconds_bucket`, `process_resident_memory_bytes`, `python_gc_objects_collected_total`...
- `node-exporter` fournit les métriques système (CPU, RAM, disque) de l'hôte.
- `cAdvisor` fournit les métriques par container.
- Prometheus scrape toutes les 15s, conserve 15 jours d'historique.

### 2. Logs (ELK Stack)

- Le backend envoie ses logs en **JSON structuré** sur deux sorties :
  - `stdout` (capturé par Docker)
  - TCP vers Logstash (port 5000) — best-effort, ne casse pas l'app si Logstash est down
- Logstash applique des filtres (parsing date, tag des erreurs) et indexe dans Elasticsearch (index `logs-<service>-<date>`).
- Kibana permet l'exploration et la création de dashboards de logs.
- Les logs incluent automatiquement le `trace_id` OpenTelemetry pour la corrélation logs ↔ traces.

### 3. Traces (Jaeger + OpenTelemetry)

- OpenTelemetry instrumente automatiquement FastAPI et `requests` (toutes les requêtes HTTP entrantes et sortantes sont tracées).
- Les spans sont exportés via OTLP gRPC (port 4317) vers Jaeger all-in-one.
- L'UI Jaeger permet de visualiser les traces, identifier les goulets d'étranglement, etc.

---

## Alerting

`AlertManager` reçoit les alertes de Prometheus définies dans `monitoring/alerts/alerts.yml`.

### Alertes système (`node-exporter`)

| Alerte | Condition | Sévérité |
|--------|-----------|----------|
| `InstanceDown` | `up == 0` pendant 1 min | critical |
| `HighCPU` | CPU > 80% pendant 2 min | warning |
| `HighMemory` | Mémoire > 85% pendant 2 min | warning |
| `DiskAlmostFull` | Disque > 90% pendant 5 min | critical |

### Alertes applicatives (`backend`)

| Alerte | Condition | Sévérité |
|--------|-----------|----------|
| `BackendHighErrorRate` | Taux d'erreur 5xx > 5% pendant 2 min | critical |
| `BackendHighLatency` | p95 latency > 1s pendant 5 min | warning |

### Routage

`AlertManager` envoie par défaut sur le webhook `http://backend:8000/alerts/webhook`. En production, configurer Slack / email / PagerDuty dans `monitoring/alertmanager/alertmanager.yml`.

---

## Sécurité

- **Authentification** : JWT (HS256), endpoint `/auth/login` avec bcrypt sur les mots de passe.
- **Containers** : utilisateur non-root pour le backend (`appuser`), nginx non-root pour le frontend.
- **Build** : Dockerfile multi-stage pour minimiser la surface d'attaque.
- **CI** : Trivy scanne les images Docker + le filesystem à chaque push (CRITICAL + HIGH).
- **Secrets** : variables d'environnement (`JWT_SECRET`, `POSTGRES_PASSWORD`), jamais commitées (`.gitignore`).

---

## Déploiement production (Terraform AWS)

L'infrastructure est entièrement décrite dans `terraform/main.tf` :

- VPC dédié (10.0.0.0/16) avec Internet Gateway
- Subnet public dans une AZ
- Security Group ouvrant SSH + ports d'observabilité
- EC2 t3.micro Amazon Linux 2023 (AMI résolue dynamiquement)
- User-data installant Docker + Docker Compose
- Volume EBS chiffré (gp3, 30 GB)

Outputs : URLs publiques de Grafana, Prometheus, Kibana, Jaeger.

---

## Évolutions futures

- Migration vers Kubernetes (Helm charts pour Prometheus, Grafana, ELK déjà disponibles)
- Service mesh (Istio / Linkerd) pour observabilité réseau
- ML pour la détection d'anomalies (Prophet, LSTM)
- Auto-scaling EC2 basé sur métriques Prometheus (custom CloudWatch metrics)
- HTTPS avec Let's Encrypt + reverse proxy Traefik
