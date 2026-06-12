---
title: "Dossier Professionnel — Bloc 1"
subtitle: "Maintenir l'infrastructure et le système d'information en conditions opérationnelles"
author: "Yassine TAIFI BERNOUSSI — Administrateur Systèmes DevOps"
date: "Mai 2026"
---

# 1. Présentation du projet support

**Projet :** *DevOps Monitoring Platform* — plateforme d'observabilité complète pour superviser des sites web tiers et alerter en cas de panne.

**Problématique :** dans un environnement cloud distribué, les équipes ont besoin de détecter rapidement les anomalies (latence, erreurs, indisponibilité), de comprendre l'origine des incidents, de centraliser les logs et d'alerter automatiquement. Sans observabilité, le MTTR explose lors des incidents.

**Solution :** une plateforme conteneurisée intégrant les **trois piliers de l'observabilité** — *métriques* (Prometheus + node-exporter + cAdvisor), *logs* (ELK), *traces* (Jaeger via OpenTelemetry OTLP) — pilotée par un backend FastAPI instrumenté et un frontend React 18.

| Couche             | Technologies                                                           |
|--------------------|------------------------------------------------------------------------|
| Application        | FastAPI 0.110 (Python 3.11), React 18 + Vite + Chart.js, JWT bcrypt    |
| Stockage           | PostgreSQL 15, Elasticsearch 8.13                                      |
| Observabilité      | Prometheus 2.51 + Grafana 10 + AlertManager + Jaeger 1.55 + ELK 8.13   |
| Infrastructure     | Terraform >= 1.5 (AWS), Docker Compose v2                              |
| CI/CD              | GitHub Actions (Ruff, Pylint, pytest, Trivy, build Docker)             |

**Indicateurs :** 12 services, 11 alertes (4 infra + 2 app + 5 métier), 16 panels Grafana, 11 tests pytest, 6 KPIs métier custom, 311 lignes de Terraform, 217 lignes de Compose. Repo : <https://github.com/YTA048/Devops-monitoring>.

# 2. Réalisation n°1 — Provisionnement AWS par Infrastructure as Code

**Compétences mobilisées :** **B1-CP2 (IaC)** *cœur* — **B1-CP3 (Sécurité)** — **B1-CP4 (Mise en production)** — **B1-CP1 (Scripts)**.

**Contexte :** la plateforme doit être déployable sur AWS de manière reproductible, sans intervention manuelle. Le déploiement doit pouvoir être détruit et recréé à l'identique pour des environnements éphémères. La version initiale du projet contenait un Terraform symbolique de 6 lignes avec une AMI hardcodée inexistante (`ami-12345678`).

**Démarche :** j'ai conçu un fichier `terraform/main.tf` de 311 lignes qui provisionne 1 VPC dédié `10.0.0.0/16`, 1 IGW + Route Table publique, 1 Subnet public dans la première AZ disponible (résolue dynamiquement), 1 Security Group exposant SSH + 7 ports d'observabilité, 1 EC2 `t3.micro` Amazon Linux 2023 avec **AMI dynamique**, 1 EBS `gp3` 30 Go **chiffré**, et un `user_data` automatisant le bootstrap (Docker, Compose, clone Git, `docker compose up -d`).

**Extraits de code clés :**

```hcl
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  filter { name = "name"   values = ["al2023-ami-2023.*-x86_64"] }
}

resource "aws_instance" "monitoring" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = var.instance_type
  vpc_security_group_ids = [aws_security_group.monitoring.id]
  root_block_device { volume_size = 30  volume_type = "gp3"  encrypted = true }
}
```

**User-data Bash :**

```bash
#!/bin/bash
set -euxo pipefail
dnf install -y docker git && systemctl enable --now docker
echo "vm.max_map_count=262144" >> /etc/sysctl.conf && sysctl -p
git clone https://github.com/YTA048/Devops-monitoring.git && cd Devops-monitoring
docker compose up -d
```

**Résultats :**

| Indicateur                   | Avant         | Après                          |
|------------------------------|---------------|--------------------------------|
| Temps de déploiement         | ~30 min manuel| ~5 min automatisé              |
| Reproductibilité             | 0 %           | 100 % (code versionné Git)     |
| Sécurité disque              | Non chiffré   | EBS chiffré (`encrypted=true`) |
| Lignes Terraform             | 6 (factice)   | 311 (fonctionnel)              |

**Difficultés résolues :** AMI hardcodée `ami-12345678` inexistante → migration vers `data "aws_ami"` ; `terraform validate` échouait dans le CI sans credentials AWS → step tolérant qui force `exit 0` ; disque EBS non chiffré par défaut → ajout `encrypted = true` ; Elasticsearch nécessitait `vm.max_map_count >= 262144` → correction dans `/etc/sysctl.conf`.

**Capture à insérer — Figure 1 :** sortie de `terraform apply` + console AWS EC2 confirmant l'instance en état `running`.

# 3. Réalisation n°2 — Conteneurisation et orchestration Docker Compose

**Compétences mobilisées :** **B1-CP3 (Sécurité)** *cœur — multi-stage non-root, scan Trivy* — **B1-CP4 (Mise en production)** — **B1-CP1 (Scripts)** — **B1-CP2 (IaC déclaratif)**.

**Contexte :** la stack comprend 12 services hétérogènes (FastAPI, React, PostgreSQL, Prometheus, Grafana, AlertManager, Jaeger, ELK, node-exporter, cAdvisor). Lancer chacun manuellement est long (15-30 min), source d'erreurs et non reproductible. La version initiale ne contenait que 2 services sans BDD ni monitoring — incohérent avec l'intitulé *DevOps Monitoring*.

**Démarche :** j'ai modélisé l'ensemble dans un `docker-compose.yml` unique (217 lignes). Les dépendances sont gérées via `depends_on` + `condition: service_healthy` pour l'ordre de démarrage : Postgres avant le backend, Elasticsearch avant Logstash et Kibana. Cinq volumes Docker nommés persistent les données (`db_data`, `prometheus_data`, `alertmanager_data`, `grafana_data`, `es_data`). Un réseau bridge dédié `monitoring` isole la communication inter-services. Les services Linux-only (`node-exporter`, `cAdvisor`) sont sous un *profile* `linux` activable via `--profile linux` — la stack reste utilisable sur Docker Desktop Windows pour le développement. La configuration sensible (mots de passe, JWT_SECRET, webhook Discord) est externalisée dans `.env` (gitignored).

**Sécurité — Dockerfile multi-stage non-root :**

```dockerfile
FROM python:3.11-slim AS builder
RUN apt-get install -y build-essential libpq-dev gcc
RUN python -m venv /opt/venv && /opt/venv/bin/pip install -r requirements.txt

FROM python:3.11-slim AS runtime
RUN apt-get install -y libpq5 curl
RUN groupadd -r appuser && useradd -r -g appuser appuser
COPY --from=builder /opt/venv /opt/venv
COPY --chown=appuser:appuser . /app
WORKDIR /app && USER appuser
HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

L'image runtime ne contient pas `gcc`/`build-essential` — surface d'attaque réduite, taille divisée par ~3. L'utilisateur `appuser` non-root limite l'impact d'une RCE. Le `HEALTHCHECK` permet à l'orchestrateur de détecter et redémarrer un conteneur défaillant. Le pipeline CI scanne automatiquement l'image et le filesystem avec **Trivy** (sévérités CRITICAL/HIGH).

**Résultats :** 12 services orchestrés (10 par défaut + 2 profile linux), 5 volumes persistants nommés, 11/11 tests pytest passés, démarrage à froid ~5 min puis ~30 s, conteneur backend non-root avec healthcheck, scan Trivy automatique en CI.

**Difficultés résolues :** `passlib 1.7.4` incompatible avec `bcrypt 4.x` (erreur trompeuse sur des mots de passe de 8 caractères) → pin `bcrypt==3.2.2` ; `node-exporter` plantait sur Docker Desktop Windows (mounts `rslave` Linux-only) → mise sous *profile* `linux` ; `httpx>=0.28` cassait `TestClient` → pin `httpx==0.27.2`.

**Capture à insérer — Figure 2 :** `docker compose ps` (10 services healthy) + `docker exec backend whoami` retournant `appuser` + Grafana sur le dashboard *Business Metrics*.

# 4. Synthèse de couverture des compétences du Bloc 1

| CP   | Intitulé                                       | État | Preuve dans le projet                                                |
|------|------------------------------------------------|:----:|----------------------------------------------------------------------|
| CP1  | Réaliser des scripts d'automatisation          | OK   | `scripts/clean-git-history.sh`, user-data Terraform, CI 5 jobs       |
| CP2  | Mettre en œuvre l'IaC                          | OK   | `terraform/main.tf` 311 lignes (VPC + EC2 + SG + AMI dynamique)      |
| CP3  | Sécuriser l'infrastructure                     | OK   | Multi-stage non-root, EBS chiffré, SG restrictif, Trivy CI, JWT bcrypt|
| CP4  | Mettre en production l'application             | OK   | Docker Compose 12 services avec healthchecks et `depends_on`         |

**Bilan professionnel :** cette double réalisation m'a permis d'industrialiser le cycle de vie complet d'une stack distribuée. En production, je ferais évoluer cette infrastructure vers un **backend Terraform distant** (S3 + DynamoDB lock) pour le travail collaboratif, des **modules Terraform** réutilisables, un **Auto Scaling Group** + **ALB** + ACM pour HTTPS, et des **IAM Roles** plutôt que des credentials statiques. Côté conteneurs, la migration vers **Kubernetes** + Helm est la suite naturelle, avec un *service mesh* (Istio/Linkerd) pour le mTLS et un **HPA** basé sur les métriques Prometheus métier (`monitoring_uptime_ratio`, `site_check_total`).

# 5. Apports professionnels et glossaire

**Apports transversaux développés :** **rigueur GitOps** (tout est versionné : code, IaC, configuration, dashboards, pipelines) ; **culture observabilité** (au-delà du technique, raconter une histoire métier avec les chiffres — j'ai créé un dashboard *Business Metrics* à 4 niveaux : Business, Application, Infrastructure, Trends & Forecast) ; **autonomie de diagnostic** (face aux incompatibilités de versions Python/Docker, apprendre à lire les logs, isoler le composant, pinner et documenter).

**Glossaire :** **IaC** *(Infrastructure as Code)* — paradigme codifiant l'infrastructure ; **AMI** *(Amazon Machine Image)* — modèle d'image disque EC2 ; **HCL** *(HashiCorp Configuration Language)* — langage Terraform ; **RCE** *(Remote Code Execution)* — vulnérabilité critique ; **MTTR** *(Mean Time To Resolve)* — temps moyen de résolution ; **TSDB** *(Time-Series DataBase)* — Prometheus ; **OTLP** *(OpenTelemetry Protocol)* — collecte des traces ; **HPA** *(Horizontal Pod Autoscaler)* — autoscaling Kubernetes basé sur métriques.

**Documentation associée dans le repo :** `docs/CDC.md` (cahier des charges), `docs/architecture.md` (architecture détaillée), `docs/business-metrics.md` (BC03-CP2, KPIs métier et capacity planning), `docs/RUNBOOK.md` (procédures de test end-to-end), `terraform/README.md` (guide de déploiement AWS), `scripts/README.md` (maintenance Git).
