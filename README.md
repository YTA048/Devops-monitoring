# DevOps Monitoring Platform

Plateforme de monitoring et d'observabilité **clé en main**, basée sur une stack DevOps moderne et entièrement conteneurisée.

> Les 3 piliers de l'observabilité : **métriques** + **logs** + **traces**, dans une seule stack lancée en `docker compose up`.

---

## Stack technique

| Couche | Technologie |
|--------|-------------|
| Backend | FastAPI 0.110 (Python 3.11), instrumenté Prometheus + OpenTelemetry |
| Frontend | React 18 + Vite, Chart.js, React Router |
| Base de données | PostgreSQL 15 |
| Métriques | Prometheus + node-exporter + cAdvisor |
| Dashboards | Grafana 10 (datasources et dashboards provisionnés automatiquement) |
| Tracing | Jaeger all-in-one (OTLP gRPC) |
| Logs | Elasticsearch + Logstash + Kibana 8.13 |
| Alerting | AlertManager |
| IaC | Terraform >= 1.5 (AWS : VPC + EC2 t3.micro) |
| CI/CD | GitHub Actions (pylint + ruff + pytest + Docker build + Trivy) |

---

## Architecture

```
                      ┌──────────────┐
   utilisateur ────▶  │  Frontend    │  React + nginx (port 3000)
                      └──────┬───────┘
                             │ REST + JWT
                      ┌──────▼───────┐
                      │   Backend    │  FastAPI (port 8000)
                      └──┬─────┬─────┴──────┐
          /metrics        │     │ logs JSON │ traces OTLP
                          │     │           │
                ┌─────────▼─┐ ┌─▼────────┐ ┌▼─────────┐
                │Prometheus │ │ Logstash │ │  Jaeger  │
                └─────┬─────┘ └────┬─────┘ └──────────┘
                      │            │
                ┌─────▼─────┐ ┌────▼─────────┐ ┌────────┐
                │  Grafana  │ │Elasticsearch │ │ Kibana │
                └───────────┘ └──────────────┘ └────────┘
                      │
                ┌─────▼────────┐
                │ AlertManager │
                └──────────────┘
```

---

## Démarrage rapide

```bash
git clone <ce-repo>
cd devops-monitoring
docker compose up -d
```

Compter ~2 minutes au premier lancement (build images + warm-up Elasticsearch).

### URLs des services

| Service | URL | Login |
|---------|-----|-------|
| Frontend | http://localhost:3000 | `admin` / `admin123` |
| Backend (API + /metrics) | http://localhost:8000 | — |
| Prometheus | http://localhost:9090 | — |
| Grafana | http://localhost:3001 | `admin` / `admin` |
| AlertManager | http://localhost:9093 | — |
| Jaeger UI | http://localhost:16686 | — |
| Kibana | http://localhost:5601 | — |
| node-exporter | http://localhost:9100/metrics | — |
| cAdvisor | http://localhost:8080 | — |

### Tester la plateforme

```bash
# Vérifier l'API
curl http://localhost:8000/health

# Lancer une vague de checks (génère métriques + logs + traces)
for i in {1..20}; do curl -s http://localhost:8000/monitor > /dev/null; done

# Provoquer une erreur (déclenche une alerte si répétée)
curl http://localhost:8000/error-test
```

Puis ouvrir Grafana → dashboard "Backend Overview", Jaeger → service `devops-monitoring-backend`, Kibana → index pattern `logs-*`.

---

## Structure du projet

```
devops-monitoring/
├── backend/                  # FastAPI app
│   ├── app/                  # auth, logging, tracing modules
│   ├── tests/                # tests pytest
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile            # multi-stage, user non-root
│   ├── pytest.ini
│   └── .pylintrc
├── frontend/pro-ui/          # React 18 + Vite app
│   ├── src/                  # pages, components, hooks, api
│   ├── Dockerfile            # multi-stage build → nginx
│   ├── nginx.conf
│   └── package.json
├── monitoring/
│   ├── prometheus.yml
│   ├── alerts/alerts.yml
│   └── alertmanager/alertmanager.yml
├── grafana/
│   ├── provisioning/         # datasources + dashboards.yml
│   └── dashboards/           # JSON dashboards
├── logstash/
│   ├── config/logstash.yml
│   └── pipeline/logstash.conf
├── terraform/                # IaC AWS (VPC + EC2)
│   ├── main.tf
│   ├── terraform.tfvars.example
│   └── README.md
├── .github/workflows/ci.yml  # Pipeline CI/CD
├── scripts/                  # Maintenance Git
├── docs/
│   ├── CDC.md
│   └── architecture.md
└── docker-compose.yml
```

---

## CI/CD

Le pipeline GitHub Actions (`.github/workflows/ci.yml`) exécute à chaque push :

1. **Lint** — `ruff` + `pylint` sur le code Python
2. **Tests** — `pytest` avec couverture, upload du rapport
3. **Build** — image Docker du backend, cache GitHub Actions
4. **Security scan** — `Trivy` sur l'image Docker + le filesystem
5. **Terraform validate** — `terraform fmt` + `terraform validate`

---

## Déploiement AWS (Terraform)

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# éditer terraform.tfvars

terraform init
terraform plan
terraform apply
```

Voir [terraform/README.md](terraform/README.md) pour les détails.

---

## Tests

```bash
cd backend
pip install -r requirements.txt
pip install pytest pytest-cov httpx
pytest --cov=. --cov-report=term
```

---

## Maintenance

Pour nettoyer l'historique Git (supprimer `node_modules/` et `monitoring.db` de tous les commits passés), voir [scripts/README.md](scripts/README.md).

---

## Documentation

- [Cahier des charges (CDC)](docs/CDC.md)
- [Architecture détaillée](docs/architecture.md)

---

## Licence

Projet académique — usage pédagogique.
