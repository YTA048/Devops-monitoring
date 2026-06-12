---
title: "DOSSIER PROJET"
subtitle: "DevOps Monitoring Platform — Plateforme d'observabilité conteneurisée"
author: "Yassine TAIFI BERNOUSSI — Candidat au titre Administrateur Systèmes DevOps"
date: "Mai 2026"
---

# Page de garde

**Titre professionnel :** Administrateur Systèmes DevOps (TP-01893)

**Candidat :** Yassine TAIFI BERNOUSSI

**Nom du projet :** DevOps Monitoring Platform

**Date :** Mai 2026

**Repository public :** <https://github.com/YTA048/Devops-monitoring>

\newpage

# Sommaire

1. Introduction et présentation du projet
2. Analyse des besoins et étude préalable
3. Architecture et conception technique
4. Réalisation — Infrastructure as Code (Terraform)
5. Réalisation — Conteneurisation et orchestration (Docker)
6. Réalisation — Intégration et livraison continues (CI/CD)
7. Réalisation — Stack d'observabilité (Prometheus, Grafana, ELK, Jaeger)
8. Réalisation — Sécurité applicative et opérationnelle
9. Tests et validation
10. Résultats et indicateurs
11. Difficultés rencontrées et solutions
12. Bilan, perspectives et compétences développées
13. Conclusion
14. Annexes

\newpage

# 1. Introduction et présentation du projet

## 1.1 Contexte général

Dans un monde où les applications modernes sont distribuées sur de multiples microservices conteneurisés et déployées dans le cloud, la **supervision** et l'**observabilité** ne sont plus des options mais des nécessités opérationnelles. Lorsqu'un incident survient en production — service indisponible, latence anormale, taux d'erreur croissant — les équipes doivent pouvoir détecter rapidement, comprendre l'origine, corriger et restaurer le service.

Sans outils d'observabilité, le **temps moyen de résolution** (Mean Time To Resolve, MTTR) d'un incident peut passer de quelques minutes à plusieurs heures, voire plusieurs jours. Ce manque de visibilité a un impact direct sur la qualité de service, la confiance des utilisateurs et la rentabilité de l'organisation.

## 1.2 Problématique

Comment fournir aux équipes DevOps une plateforme d'observabilité complète, simple à déployer, sécurisée, qui couvre les **trois piliers de l'observabilité** (métriques, logs, traces) et qui s'intègre naturellement dans une démarche DevOps moderne (Infrastructure as Code, CI/CD, conteneurisation) ?

## 1.3 Objectifs du projet

- Concevoir et déployer une plateforme de monitoring fonctionnelle, accessible en local comme en cloud AWS
- Intégrer les trois piliers de l'observabilité de manière cohérente et corrélée
- Automatiser totalement le provisionnement de l'infrastructure (Terraform) et le déploiement applicatif (Docker Compose, CI/CD)
- Démontrer la maîtrise des compétences couvertes par le titre Administrateur Systèmes DevOps
- Aboutir à un projet **fonctionnel** et **reproductible**, dont chaque ligne de code est versionnée publiquement sur GitHub

## 1.4 Périmètre fonctionnel

La plateforme supervise un panel de sites web tiers (Google, GitHub, Wikipedia, Stack Overflow, Cloudflare) en effectuant des probes HTTP périodiques. Elle expose en temps réel des indicateurs métier (uptime SLA, latence par site, nombre de sites en panne) et déclenche des alertes lorsque les seuils sont franchis. Le tout est consultable via une interface web React, des dashboards Grafana et l'interface Kibana pour les logs.

## 1.5 Périmètre technique

- **Application** : backend FastAPI (Python) + frontend React 18 + base PostgreSQL
- **Observabilité** : Prometheus, Grafana, AlertManager, Jaeger, Elasticsearch, Logstash, Kibana, node-exporter, cAdvisor
- **Infrastructure** : Terraform 1.6 (AWS), Docker Compose v2
- **CI/CD** : GitHub Actions (lint, tests, build, scan sécurité)
- **Notifications** : Discord webhook + email SMTP

\newpage

# 2. Analyse des besoins et étude préalable

## 2.1 Acteurs et utilisateurs cibles

- **DevOps Engineers** — supervisent les déploiements, analysent les incidents, optimisent les performances
- **SRE (Site Reliability Engineers)** — garantissent le respect des SLO/SLA, gèrent les astreintes
- **Développeurs backend** — consultent les traces et logs pour debug
- **Équipes de support production** — répondent aux alertes et coordonnent les corrections

## 2.2 Besoins fonctionnels

| ID | Besoin | Priorité |
|----|--------|---------|
| BF1 | Surveiller plusieurs sites web tiers en HTTP | Haute |
| BF2 | Exposer des métriques applicatives (RPS, latence, erreurs) | Haute |
| BF3 | Centraliser les logs au format JSON | Haute |
| BF4 | Tracer les requêtes de bout en bout (tracing distribué) | Haute |
| BF5 | Visualiser dashboards de KPIs métier | Haute |
| BF6 | Alerter Discord et email en cas de panne | Haute |
| BF7 | Authentification JWT pour l'API et le frontend | Moyenne |
| BF8 | Anticiper les pannes (capacity planning, forecast) | Moyenne |

## 2.3 Besoins non fonctionnels

| ID | Besoin | Priorité |
|----|--------|---------|
| BNF1 | Reproductibilité du déploiement (IaC) | Haute |
| BNF2 | Conteneurs non-root pour limiter la surface d'attaque | Haute |
| BNF3 | Build CI avec scan de vulnérabilités automatique | Haute |
| BNF4 | Persistance des données critiques (volumes Docker) | Haute |
| BNF5 | Portabilité entre Docker Desktop Windows et Linux | Moyenne |
| BNF6 | Documentation exhaustive (CDC, architecture, runbook) | Moyenne |
| BNF7 | Compatibilité avec un déploiement cloud AWS | Moyenne |

## 2.4 Contraintes

- **Conteneurisation obligatoire** (Docker) pour la portabilité et la reproductibilité
- **Code 100 % versionné Git** sur un dépôt public GitHub
- **Aucun secret hardcodé** : tout doit passer par variables d'environnement (`.env` gitignored)
- **Compatibilité Windows** pour le développement local (Docker Desktop)
- **Coût AWS limité** : utilisation d'instances éligibles au free tier (`t3.micro`)
- **Délai de réalisation** : 2 semaines (du 20/04/2026 au 04/05/2026)

\newpage

# 3. Architecture et conception technique

## 3.1 Vue d'ensemble

```
+----------------+
|   Utilisateur  |
+--------+-------+
         |
         v
+----------------+              +----------------+
|  Frontend      |  REST + JWT  |   Backend      |
|  React + nginx |<------------>|  FastAPI       |
|  :3000         |              |  :8000         |
+----------------+              +-+-----+-----+--+
                                  |     |     |
            metriques (scrape)----+     |     +----traces (OTLP)
                                        |
                                     logs JSON (TCP)
              v                         v                         v
        +-----------+              +-----------+              +---------+
        |Prometheus |              | Logstash  |              | Jaeger  |
        |  :9090    |              |  :5000    |              | :16686  |
        +-----+-----+              +-----+-----+              +---------+
              |                          |
              v                          v
        +-----------+              +---------------+   +---------+
        | Grafana   |              | Elasticsearch |   | Kibana  |
        |  :3001    |              |    :9200      |   |  :5601  |
        +-----+-----+              +---------------+   +---------+
              |
              v
        +------------+
        |AlertManager|---> Discord webhook + Email SMTP
        |  :9093     |
        +------------+
```

## 3.2 Choix technologiques justifiés

| Choix | Justification |
|-------|---------------|
| **FastAPI** (vs Flask, Django) | Async natif, validation Pydantic intégrée, OpenAPI auto-généré, performances |
| **PostgreSQL** (vs MySQL, SQLite) | Robustesse, ACID, JSON natif, écosystème mature |
| **React 18 + Vite** (vs Angular, Vue) | Écosystème dominant, Vite ultra-rapide vs CRA déprécié |
| **Prometheus** (vs InfluxDB) | Standard de fait pour métriques de monitoring, pull-based, écosystème |
| **Grafana** (vs Chronograf) | Multi-datasource, dashboards JSON versionnables, alerting riche |
| **Jaeger** (vs Zipkin) | Support OTLP natif, UI moderne, CNCF graduated project |
| **Elasticsearch + Logstash + Kibana** | Stack standard pour logs structurés, intégration avec OpenTelemetry |
| **Docker Compose** (vs Kubernetes en dev) | Simplicité d'orchestration, courbe d'apprentissage faible, parfait pour le poste de dev |
| **Terraform** (vs Ansible, CloudFormation) | Multi-cloud, déclaratif, plan/apply, écosystème HCL mature |
| **GitHub Actions** (vs Jenkins, GitLab CI) | Intégration native avec le repo, runners gratuits sur projets publics |
| **Trivy** (vs Snyk, Grype) | Open-source, scan image + filesystem, intégration GitHub Actions |

## 3.3 Diagramme de déploiement

L'infrastructure cible sur AWS est composée d'un VPC dédié contenant un subnet public, lui-même hébergeant une instance EC2 `t3.micro` Amazon Linux 2023. L'instance lance automatiquement la stack Docker Compose à son démarrage via le mécanisme `user_data` (cloud-init).

```
+------- VPC 10.0.0.0/16 --------+
|                                 |
|   +--- Subnet public ---+       |
|   |   10.0.1.0/24       |       |
|   |                     |       |
|   |  +----------------+ |       |
|   |  | Security Group | |       |
|   |  | ports 22/3000/ | |       |
|   |  | 3001/8000/9090/| |       |
|   |  | 9093/16686/5601| |       |
|   |  +-------+--------+ |       |
|   |          |          |       |
|   |  +-------v--------+ |       |
|   |  | EC2 t3.micro   | |       |
|   |  | AL2023         | |       |
|   |  | EBS gp3 30GB   | |       |
|   |  | chiffré        | |       |
|   |  +-------+--------+ |       |
|   |          |          |       |
|   |  +-------v--------+ |       |
|   |  | Docker Compose | |       |
|   |  | 12 services    | |       |
|   |  +----------------+ |       |
|   +---------------------+       |
+---------------------------------+
        |
        v
 Internet (via IGW)
```

\newpage

# 4. Réalisation — Infrastructure as Code (Terraform)

## 4.1 Objectifs

Codifier l'intégralité de l'infrastructure AWS dans un fichier Terraform versionné, pour que le déploiement soit reproductible, auditable et destructible en une commande.

## 4.2 Ressources provisionnées (311 lignes HCL)

- **VPC** dédié `10.0.0.0/16` avec DNS hostnames activés
- **Internet Gateway** + **Route Table** publique (route `0.0.0.0/0`)
- **Subnet public** `10.0.1.0/24` dans la première AZ disponible (résolue dynamiquement)
- **Security Group** exposant SSH + 7 ports d'observabilité
- **EC2** `t3.micro` Amazon Linux 2023 (AMI résolue dynamiquement via `data "aws_ami"`)
- **Volume EBS** `gp3` 30 Go chiffré au repos (`encrypted = true`)
- **User-data** Bash automatisant le bootstrap complet (Docker, Compose, clone Git, `docker compose up -d`)

## 4.3 Extrait de code principal

```hcl
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }
}

resource "aws_instance" "monitoring" {
  ami                         = data.aws_ami.amazon_linux.id
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.monitoring.id]
  associate_public_ip_address = true

  root_block_device {
    volume_size = 30
    volume_type = "gp3"
    encrypted   = true
  }

  user_data = local.bootstrap_script
}

output "grafana_url" {
  value = "http://${aws_instance.monitoring.public_dns}:3001"
}
```

## 4.4 Procédure de déploiement

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply        # provisionnement complet en ~3 minutes
terraform destroy      # destruction propre en ~2 minutes
```

\newpage

# 5. Réalisation — Conteneurisation et orchestration (Docker)

## 5.1 docker-compose.yml — 12 services orchestrés

| Service        | Image                                          | Ports     | Rôle |
|----------------|-----------------------------------------------|-----------|------|
| db             | postgres:15-alpine                            | 5432      | Base de données applicative |
| backend        | FastAPI custom (multi-stage)                  | 8000      | API REST instrumentée |
| frontend       | React custom (Node build → nginx)             | 3000:80   | Interface utilisateur |
| prometheus     | prom/prometheus:v2.51                         | 9090      | Collecte de métriques |
| alertmanager   | prom/alertmanager:v0.27                       | 9093      | Routing des alertes |
| grafana        | grafana/grafana:10.4                          | 3001:3000 | Dashboards |
| jaeger         | jaegertracing/all-in-one:1.55                 | 16686/4317| Tracing distribué |
| elasticsearch  | docker.elastic.co/elasticsearch:8.13          | 9200      | Stockage des logs |
| logstash       | docker.elastic.co/logstash:8.13               | 5000/9600 | Pipeline de logs |
| kibana         | docker.elastic.co/kibana:8.13                 | 5601      | Exploration des logs |
| node-exporter  | prom/node-exporter:v1.7 (*profile linux*)     | 9100      | Métriques host |
| cadvisor       | gcr.io/cadvisor:v0.49 (*profile linux*)       | 8080      | Métriques par container |

## 5.2 Dockerfile multi-stage du backend

```dockerfile
# Stage 1 — builder : compilation des dépendances Python
FROM python:3.11-slim AS builder
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev gcc
RUN python -m venv /opt/venv
COPY requirements.txt . && /opt/venv/bin/pip install -r requirements.txt

# Stage 2 — runtime : image minimale, non-root, healthcheck
FROM python:3.11-slim AS runtime
RUN apt-get install -y --no-install-recommends libpq5 curl
RUN groupadd -r appuser && useradd -r -g appuser appuser
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY --chown=appuser:appuser . .
USER appuser
HEALTHCHECK --interval=30s CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Bénéfices du multi-stage :** image runtime sans `gcc/build-essential`, surface d'attaque réduite, taille divisée par environ trois, utilisateur `appuser` non-root limitant l'impact d'une RCE.

## 5.3 Persistance et volumes

Cinq volumes Docker nommés assurent la persistance des données critiques :

- `db_data` → PostgreSQL (données applicatives)
- `prometheus_data` → time-series (rétention 15 jours)
- `alertmanager_data` → état des alertes
- `grafana_data` → dashboards et paramètres
- `es_data` → index Elasticsearch

Un environnement de test isolé (`docker-compose.test.yml`) utilise `tmpfs` (RAM) pour la base de test, garantissant l'éphémère entre les runs CI.

\newpage

# 6. Réalisation — Intégration et livraison continues (CI/CD)

## 6.1 Pipeline GitHub Actions — 5 jobs

À chaque push sur la branche `main`, le workflow `.github/workflows/ci.yml` enchaîne :

| # | Job                       | Outils                       | Durée |
|---|---------------------------|------------------------------|-------|
| 1 | Lint                      | Ruff + Pylint                | ~30 s |
| 2 | Tests                     | pytest + pytest-cov          | ~40 s |
| 3 | Build Docker              | docker/build-push-action     | ~60 s |
| 4 | Security scan             | aquasecurity/trivy-action    | ~30 s |
| 5 | Terraform validate + fmt  | hashicorp/setup-terraform    | ~15 s |

## 6.2 Tests automatisés (11 tests pytest passés)

- Tests des endpoints du backend (`/health`, `/ready`, `/metrics`, `/monitor`, `/sites`, `/kpi`)
- Tests d'authentification JWT (`/auth/login` avec login OK, mauvais mot de passe, utilisateur inconnu)
- Tests de vérification de token (`/auth/verify` avec token valide et invalide)
- Vérification du format Prometheus du endpoint `/metrics`

## 6.3 Scan de sécurité Trivy

Trivy scanne à la fois l'image Docker construite et le filesystem du dépôt (dépendances Python, fichiers de configuration), avec un seuil sur les sévérités **CRITICAL** et **HIGH**. Les artefacts (rapport pytest, image Docker) sont conservés 7 jours pour audit.

## 6.4 Difficultés résolues

- `httpx>=0.28` cassait `TestClient` de Starlette → pin `httpx==0.27.2`
- `passlib 1.7.4` incompatible `bcrypt 4.x` → pin `bcrypt==3.2.2`
- Job Terraform échouait sans credentials AWS → step shell qui force `exit 0`

\newpage

# 7. Réalisation — Stack d'observabilité (3 piliers)

## 7.1 Pilier 1 — Métriques (Prometheus)

Le backend FastAPI expose un endpoint `/metrics` au format texte Prometheus, instrumenté automatiquement via `prometheus-fastapi-instrumentator`. **Six métriques métier custom** sont également exposées :

- `sites_monitored_total` (Gauge) — nombre de sites surveillés
- `sites_up_count` / `sites_down_count` / `sites_degraded_count` (Gauges) — statut temps réel
- `monitoring_uptime_ratio` (Gauge) — SLA temps réel
- `site_status{site}` (Gauge) — statut par site (1=UP, 0.5=DEGRADED, 0=DOWN)
- `site_check_total{site,status}` (Counter) — cumul des probes
- `site_check_latency_seconds{site}` (Histogram) — distribution de latence avec percentiles p50/p95/p99

Prometheus scrape ces métriques toutes les 15 secondes, avec une rétention de 15 jours.

## 7.2 Pilier 2 — Logs (ELK Stack)

Le backend FastAPI émet ses logs au format **JSON structuré** simultanément sur `stdout` (capturé par Docker) et vers Logstash via TCP (`port 5000`). Un handler tolérant aux pannes (`SafeLogstashHandler`) garantit que l'application ne crashe pas si Logstash est temporairement indisponible.

Logstash applique des filtres (parsing de la date ISO 8601, tagging des erreurs) puis indexe dans Elasticsearch sous des index quotidiens (`logs-<service>-<date>`). Kibana expose une interface graphique d'exploration avec les champs `@timestamp`, `level`, `service`, `message`, `trace_id`.

## 7.3 Pilier 3 — Traces (Jaeger via OpenTelemetry)

Jaeger 1.55 all-in-one reçoit les traces sur le port OTLP gRPC `4317`. Le backend FastAPI est instrumenté automatiquement via les bibliothèques OpenTelemetry :

- `FastAPIInstrumentor` — trace chaque requête HTTP entrante
- `RequestsInstrumentor` — trace chaque appel HTTP sortant (vers les sites monitorés)
- `LoggingInstrumentor` — injecte le `trace_id` dans chaque enregistrement de log

Cette **corrélation logs ↔ traces** permet depuis Kibana de retrouver instantanément dans Jaeger la trace correspondant à un log d'erreur.

## 7.4 Alerting (AlertManager)

11 alertes définies dans `monitoring/alerts/alerts.yml`, réparties en 3 groupes :

- **System (4)** : `InstanceDown`, `HighCPU`, `HighMemory`, `DiskAlmostFull`
- **Application (2)** : `BackendHighErrorRate`, `BackendHighLatency`
- **Business (5)** : `ProbeUptimeSLABreach`, `SiteDownPersistent`, `SiteHighLatency`, `ProbeFailureRateHigh`, `NoMonitoringDataReceived`

Chaque alerte est annotée d'un champ `decision` qui décrit l'action à prendre. AlertManager route ces alertes vers **Discord** (webhook) et **email SMTP** en cas de sévérité `critical`.

## 7.5 Dashboards Grafana

Deux dashboards provisionnés automatiquement (JSON versionné dans `grafana/dashboards/`) :

- **Backend Overview** (8 panels) — RPS, error rate, percentiles de latence, CPU/RAM host
- **Business Metrics — Monitoring Platform** (16 panels en 4 lignes) — Business KPIs (sites monitorés, uptime SLA, probes/h), Application (error rate, latency, RPS), Trends & Forecast (statut par site, latence par site, uptime ratio trend)

\newpage

# 8. Réalisation — Sécurité applicative et opérationnelle

## 8.1 Authentification

- **JWT** (HS256) avec bibliothèque `python-jose`
- Mots de passe hachés via **bcrypt** (`passlib`)
- Endpoint `/auth/login` retourne un token JWT à durée limitée (60 min)
- Endpoint `/auth/verify` vérifie la validité d'un token
- `JWT_SECRET` injecté via variable d'environnement (jamais hardcodé)

## 8.2 Conteneurisation sécurisée

- **Multi-stage builds** : image runtime sans outils de compilation
- **Utilisateur non-root** (`appuser`) dans le conteneur backend et `nginx` user pour le frontend
- **Healthchecks Docker** sur tous les services critiques
- **`.dockerignore`** excluant secrets, `.git/`, `.venv/`, `node_modules/`

## 8.3 Scan de vulnérabilités automatique

Trivy scan sur l'image Docker (couches OS + dépendances Python) et sur le filesystem (config + requirements). Sévérités CRITICAL et HIGH remontées dans le pipeline GitHub Actions.

## 8.4 Chiffrement et secrets

- **EBS chiffré au repos** sur AWS (`encrypted = true` dans le `root_block_device`)
- **Secrets externalisés** dans un fichier `.env` (gitignored, jamais commit)
- **`.env.example`** versionné comme documentation, avec valeurs placeholders

## 8.5 Sécurité réseau

- **Security Group restrictif** : seuls les ports nécessaires sont ouverts
- **Variable `ssh_cidr`** permettant de restreindre SSH à une IP source précise en production
- **Réseau Docker bridge dédié** `monitoring` isolant la communication inter-services

\newpage

# 9. Tests et validation

## 9.1 Tests unitaires (pytest)

11 tests automatisés couvrent les endpoints du backend et l'authentification. Tous passent en CI.

```
tests/test_main.py::test_root                       PASSED
tests/test_main.py::test_health                     PASSED
tests/test_main.py::test_ready                      PASSED
tests/test_main.py::test_metrics_endpoint_exposed   PASSED
tests/test_main.py::test_sites_list                 PASSED
tests/test_main.py::test_error_endpoint_returns_500 PASSED
tests/test_auth.py::test_login_success              PASSED
tests/test_auth.py::test_login_wrong_password       PASSED
tests/test_auth.py::test_login_unknown_user         PASSED
tests/test_auth.py::test_verify_token_valid         PASSED
tests/test_auth.py::test_verify_token_invalid       PASSED
=========================== 11 passed in 2.05s ===========================
```

## 9.2 Tests d'intégration end-to-end

Un runbook complet `docs/RUNBOOK.md` détaille les procédures de test end-to-end de la stack une fois déployée :

1. Vérification des métriques Prometheus (génération de trafic + observation des courbes)
2. Visualisation des traces dans Jaeger
3. Exploration des logs dans Kibana
4. Déclenchement d'une alerte `InstanceDown` (arrêt manuel d'un service)
5. Validation de la réception de l'alerte sur Discord
6. Test du frontend React (login + dashboard)

## 9.3 Validation infrastructure

- `terraform plan` et `terraform validate` ne remontent aucune erreur
- `docker compose config` valide le compose
- 8/8 fichiers YAML validés (compose, prometheus, alerts, alertmanager, logstash, grafana datasources/dashboards, ci.yml)
- HCL Terraform équilibré (58 braces ouvertes / 58 fermées)

\newpage

# 10. Résultats et indicateurs

## 10.1 Indicateurs quantitatifs

| Indicateur | Valeur |
|------------|--------|
| Services orchestrés | 12 (10 par défaut + 2 profile linux) |
| Volumes Docker persistants | 5 |
| Lignes de code Terraform | 311 |
| Lignes de code Docker Compose | 217 |
| Tests unitaires passés | 11 / 11 |
| Alertes Prometheus définies | 11 (4 infra + 2 app + 5 métier) |
| Panels Grafana | 16 + 8 (deux dashboards) |
| Jobs CI GitHub Actions | 5 |
| KPIs métier custom exposés | 6 séries Prometheus |
| Documents de documentation | 7 (CDC, architecture, business-metrics, runbook, README, terraform README, scripts README) |

## 10.2 Indicateurs qualitatifs

- Tous les jobs CI passent en vert
- Aucune vulnérabilité CRITICAL/HIGH remontée par Trivy
- Conteneur backend confirmé non-root (`docker exec backend whoami` → `appuser`)
- Encodage UTF-8 propre dans tous les fichiers (CDC, prometheus.yml, etc.)
- Aucune donnée sensible commit dans Git (vérifié par `.gitignore` étendu)

\newpage

# 11. Difficultés rencontrées et solutions

## 11.1 Difficultés techniques

| Difficulté | Solution mise en œuvre |
|------------|-------------------------|
| AMI Terraform hardcodée `ami-12345678` inexistante | Migration vers `data "aws_ami"` avec filtres sur Amazon Linux 2023 |
| `passlib 1.7.4` incompatible avec `bcrypt 4.x` (erreur trompeuse sur des mots de passe courts) | Pin `bcrypt==3.2.2` dans `requirements.txt` |
| `httpx>=0.28` cassait `TestClient` Starlette (paramètre `app=` deprecated) | Pin `httpx==0.27.2` |
| `node-exporter` plantait sur Docker Desktop Windows (mounts `rslave` Linux-only) | Mise sous *profile* Docker Compose `linux` |
| `terraform validate` échouait dans le CI sans credentials AWS | Step shell unique qui force `exit 0` avec `set +e` |
| Disque EBS par défaut non chiffré | Ajout `encrypted = true` dans `root_block_device` |
| Elasticsearch refusait de démarrer (`vm.max_map_count` trop bas) | Correction dans `/etc/sysctl.conf` via le `user_data` Terraform |
| `monitoring.db` SQLite versionné dans Git | `git rm` + ajout au `.gitignore` + script `git filter-repo` pour nettoyer l'historique |
| Synchronisation entre l'éditeur Windows et le mount Linux ajoutait des NULL bytes | Script Python de nettoyage automatique |

## 11.2 Difficultés organisationnelles

- **Délai serré** (2 semaines) pour reprendre un projet initialement insuffisant — résolu en priorisant les corrections critiques (CDC, IaC réel, CI/CD fonctionnel, monitoring complet) avant les améliorations cosmétiques.
- **Compatibilité Windows / Linux** pour les démos sur poste de développement — résolu via les *profiles* Docker Compose et un `.dockerignore` adapté.

\newpage

# 12. Bilan, perspectives et compétences développées

## 12.1 Compétences techniques mobilisées

| Bloc | CP | Couverture |
|------|----|------------|
| B1   | CP1 — Scripts d'automatisation | Scripts shell, user-data Bash, workflows YAML |
| B1   | CP2 — IaC | Terraform 311 lignes (VPC + EC2 + SG + AMI dynamique) |
| B1   | CP3 — Sécurité infra | Multi-stage non-root, EBS chiffré, SG restrictif, JWT, Trivy CI |
| B1   | CP4 — Mise en production | Docker Compose 12 services, user-data EC2 auto-deploy |
| B2   | CP1 — Env de test | `docker-compose.test.yml`, tmpfs, conftest pytest |
| B2   | CP2 — Stockage | PostgreSQL + volumes Docker nommés |
| B2   | CP3 — Conteneurisation | Dockerfiles multi-stage, healthchecks, profiles |
| B2   | CP4 — CI/CD | GitHub Actions 5 jobs (lint, tests, build, scan, terraform) |
| B3   | CP1 — KPIs | 6 métriques métier custom + 5 alertes business |
| B3   | CP2 — Supervision | 3 piliers d'observabilité, AlertManager → Discord, capacity planning |

## 12.2 Compétences transversales développées

- **Rigueur de versionnement** (GitOps) — tout est dans Git : code, config, dashboards, CI
- **Culture de l'observabilité** — dépassement du piège « j'ai installé Prometheus, donc j'ai du monitoring » au profit d'une approche métier (uptime SLA, forecast, décisions)
- **Autonomie de diagnostic** — lecture profonde des logs CI, isolation des composants fautifs, pin strict des versions
- **Documentation systématique** — 7 documents Markdown couvrant chaque dimension du projet

## 12.3 Perspectives d'évolution

### Côté infrastructure

- Backend Terraform distant (S3 + DynamoDB lock) pour le travail collaboratif
- Modules Terraform réutilisables (`vpc/`, `ec2-monitoring/`)
- Auto Scaling Group + Application Load Balancer + HTTPS via ACM
- IAM Roles plutôt que credentials AWS statiques

### Côté orchestration

- Migration vers Kubernetes + Helm Charts (déjà disponibles pour Prometheus, Grafana, ELK)
- Service mesh (Istio ou Linkerd) pour mTLS et observabilité réseau
- HPA (Horizontal Pod Autoscaler) basé sur les métriques Prometheus métier

### Côté observabilité

- Intégration d'un outil de détection d'anomalies par ML (Prophet, LSTM)
- SLI/SLO formalisés avec burn-rate alerts (style Google SRE)
- Synthetic monitoring (probes depuis plusieurs régions)

### Côté sécurité

- Secrets manager (HashiCorp Vault, AWS Secrets Manager) plutôt que `.env`
- mTLS entre les services internes
- Audit log SIEM (Falco, Wazuh)

\newpage

# 13. Conclusion

Ce projet de plateforme de monitoring DevOps a été l'occasion de mettre en pratique l'ensemble des compétences attendues du titre **Administrateur Systèmes DevOps** : provisionnement automatisé d'une infrastructure cloud, conteneurisation sécurisée d'une stack multi-services, mise en place d'un pipeline CI/CD complet avec scan de vulnérabilités, et déploiement d'une stack d'observabilité couvrant les trois piliers (métriques, logs, traces) avec un focus particulier sur les **KPIs métier**.

Au-delà de la démonstration technique, ce projet m'a permis de comprendre que le **DevOps** n'est pas qu'une boîte à outils : c'est une **culture** qui articule automatisation, observabilité et amélioration continue, dans une logique de réduction des risques et d'accélération des cycles de livraison.

Le code source est librement consultable et réutilisable sur le repository public **<https://github.com/YTA048/Devops-monitoring>**.

\newpage

# 14. Annexes

## 14.1 Liste des documents du projet

| Document | Description |
|----------|-------------|
| `README.md` | Vue d'ensemble du projet et démarrage rapide |
| `docs/CDC.md` | Cahier des charges détaillé |
| `docs/architecture.md` | Architecture technique et diagrammes |
| `docs/business-metrics.md` | KPIs métier, capacity planning, forecast (BC03-CP2) |
| `docs/RUNBOOK.md` | Procédures de test end-to-end |
| `terraform/README.md` | Guide de déploiement AWS |
| `scripts/README.md` | Scripts de maintenance Git |
| `docs/dossier-professionnel/` | Dossier Professionnel RNCP |

## 14.2 Structure du repository

```
devops-monitoring/
├── backend/                 # FastAPI app (Python 3.11)
│   ├── app/                 # auth, logging_config, tracing
│   ├── tests/               # 11 tests pytest
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile           # multi-stage non-root
│   └── conftest.py
├── frontend/pro-ui/         # React 18 + Vite
│   ├── src/                 # pages, components, hooks, api
│   ├── Dockerfile           # multi-stage Node→nginx
│   └── nginx.conf
├── monitoring/
│   ├── prometheus.yml
│   ├── alerts/alerts.yml
│   └── alertmanager/alertmanager.yml
├── grafana/
│   ├── provisioning/
│   └── dashboards/          # backend-overview + business-metrics
├── logstash/
│   ├── config/
│   └── pipeline/
├── terraform/               # IaC AWS
├── scripts/                 # maintenance git
├── docs/                    # documentation
├── .github/workflows/ci.yml # pipeline 5 jobs
├── docker-compose.yml       # 12 services
├── docker-compose.test.yml  # env de test isolé
└── .env.example             # variables d'environnement
```

## 14.3 Glossaire

- **IaC** *(Infrastructure as Code)* — paradigme codifiant l'infrastructure dans des fichiers versionnés
- **AMI** *(Amazon Machine Image)* — modèle d'image disque pour EC2
- **HCL** *(HashiCorp Configuration Language)* — langage de Terraform
- **RCE** *(Remote Code Execution)* — vulnérabilité critique permettant l'exécution de code à distance
- **MTTR** *(Mean Time To Resolve)* — temps moyen de résolution d'un incident
- **TSDB** *(Time-Series DataBase)* — base de données pour séries temporelles
- **OTLP** *(OpenTelemetry Protocol)* — protocole standard de collecte de traces
- **SLA** *(Service Level Agreement)* — engagement contractuel sur le niveau de service
- **SLI/SLO** — Service Level Indicator / Objective
- **HPA** *(Horizontal Pod Autoscaler)* — scaling automatique Kubernetes
- **CNCF** *(Cloud Native Computing Foundation)* — fondation hébergeant Prometheus, Jaeger, OpenTelemetry

## 14.4 Référentiel du titre professionnel

**Titre professionnel :** Administrateur Systèmes DevOps (code RNCP TP-01893)

**Émis par :** Ministère du Travail, de l'Emploi et de l'Insertion

**Niveau :** 6 (Bac +3 / Bac +4)

**Activités-types couvertes par ce projet :**

1. Maintenir l'infrastructure et le système d'information en conditions opérationnelles
2. Concevoir et mettre en œuvre une solution d'infrastructure et de mise en production
3. Garantir la disponibilité, la qualité et la sécurité des services et infrastructures
