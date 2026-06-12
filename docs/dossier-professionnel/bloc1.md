# Dossier Professionnel — Bloc 1
## Maintenir l'infrastructure et le système d'information en conditions opérationnelles

> Titre professionnel **Administrateur Systèmes DevOps** (TP-01893)
> Candidat : Yassine TAIFI BERNOUSSI
> Projet : **DevOps Monitoring Platform**
> Repository : https://github.com/YTA048/Devops-monitoring

---

## 1. Présentation du projet support

### 1.1 Contexte

Dans les environnements modernes (cloud, microservices), les applications sont distribuées et complexes. Les équipes DevOps ont besoin d'outils permettant de superviser les performances, détecter les incidents et analyser rapidement les problèmes en production. Sans observabilité, les systèmes deviennent difficiles à maintenir et le temps moyen de résolution (MTTR) explose lors des incidents.

### 1.2 Problématique

Comment surveiller efficacement une application distribuée afin de :

- Détecter rapidement les anomalies (latence, taux d'erreur, indisponibilité)
- Comprendre l'origine des incidents grâce au tracing distribué
- Centraliser les logs pour un debug rapide
- Garantir la disponibilité et la performance des services
- Alerter automatiquement les équipes en cas de dégradation

### 1.3 Solution mise en œuvre

J'ai conçu et implémenté une **plateforme de monitoring et d'observabilité** complète, basée sur les trois piliers de l'observabilité : **métriques** (Prometheus), **logs** (ELK Stack) et **traces** (Jaeger).

L'infrastructure est entièrement codifiée (Infrastructure as Code via Terraform), conteneurisée (Docker Compose) et automatisée (CI/CD GitHub Actions).

### 1.4 Stack technique

| Couche | Technologie | Rôle |
|---|---|---|
| Application | FastAPI 0.110 (Python 3.11) | API REST instrumentée |
| Frontend | React 18 + Vite + Chart.js | Dashboard utilisateur |
| Stockage | PostgreSQL 15 | Persistance applicative |
| Métriques | Prometheus + node-exporter + cAdvisor | Collecte et stockage TSDB |
| Dashboards | Grafana 10 | Visualisation et KPI métier |
| Tracing | Jaeger (OTLP gRPC) | Tracing distribué |
| Logs | Elasticsearch + Logstash + Kibana 8.13 | Centralisation et exploration |
| Alerting | AlertManager + Discord/Email | Notifications |
| IaC | Terraform >= 1.5 | Provisionnement AWS |
| CI/CD | GitHub Actions | Lint, tests, build, scan sécurité |

---

## 2. Réalisation n°1 — Provisionnement de l'infrastructure cloud par Infrastructure as Code

### 2.1 Compétences mobilisées

| Compétence | Couverture |
|---|---|
| **CP2 — Mettre en œuvre l'Infrastructure as Code** | Cœur de la réalisation |
| CP3 — Sécuriser l'infrastructure | Security Group restrictif, EBS chiffré |
| CP4 — Mettre en production l'application | User-data installant Docker + clone repo + `docker compose up` |
| CP1 — Scripts d'automatisation | Bash dans `user_data` Terraform |

### 2.2 Contexte et besoin

La plateforme de monitoring doit être déployable sur AWS de manière reproductible, sans intervention manuelle. Le déploiement doit pouvoir être détruit et recréé à l'identique à tout moment, pour des environnements éphémères (dev, demo, soutenance).

### 2.3 Objectifs

1. **Codifier l'infrastructure** dans des fichiers HCL versionnés
2. **Provisionner automatiquement** un VPC dédié, un subnet public, un Security Group, une instance EC2
3. **Bootstraper l'application** automatiquement via le mécanisme `user_data` (cloud-init)
4. **Sécuriser** l'instance : chiffrement du disque, ports restreints, AMI résolue dynamiquement
5. **Permettre la destruction propre** en une commande (`terraform destroy`)

### 2.4 Démarche

#### a) Choix technologiques

- **Terraform** plutôt qu'Ansible ou CloudFormation : indépendance vis-à-vis du cloud provider, syntaxe déclarative, plan/apply, écosystème riche.
- **AMI dynamique** (`data "aws_ami"`) plutôt qu'AMI hardcodée : la même configuration fonctionne quelle que soit la région et reste valide dans le temps.
- **EC2 t3.micro** : éligible au free tier, suffisant pour la démo (l'optimisation viendrait via Auto-Scaling Groups en production).

#### b) Architecture provisionnée

```
                    AWS Cloud
                       │
          ┌────────────┴────────────┐
          │   VPC 10.0.0.0/16       │
          │     │                   │
          │     ├── IGW             │
          │     │                   │
          │     ├── Route Table ────┼─→ 0.0.0.0/0 → IGW
          │     │                   │
          │     └── Subnet public   │
          │          10.0.1.0/24    │
          │             │           │
          │             ├── SG (SSH/8000/3000/3001/9090/16686/5601/9093)
          │             │           │
          │             └── EC2 t3.micro
          │                  │      │
          │                  └── EBS gp3 30GB chiffré
          │                  └── User-data : Docker + Compose + clone + up
          │                       │
          └───────────────────────┘
```

#### c) Extraits de code clés

**Provider et AMI dynamique** (`terraform/main.tf`) :

```hcl
provider "aws" {
  region = var.aws_region
}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}
```

> **Justification** : la résolution dynamique évite l'écueil d'une AMI hardcodée qui deviendrait obsolète ou inexistante dans une autre région.

**Security Group** (extrait) :

```hcl
resource "aws_security_group" "monitoring" {
  name        = "${var.project_name}-sg"
  description = "Allow SSH and observability stack ports"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_cidr]   # restreint en prod
  }

  ingress {
    description = "Grafana"
    from_port   = 3001
    to_port     = 3001
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  # ... 7 autres ingress (FastAPI, Prometheus, Jaeger, Kibana, etc.)
}
```

**EC2 + user-data** (bootstrap automatique) :

```hcl
resource "aws_instance" "monitoring" {
  ami                         = data.aws_ami.amazon_linux.id
  instance_type               = var.instance_type
  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.monitoring.id]
  associate_public_ip_address = true

  user_data = <<-EOF
    #!/bin/bash
    set -euxo pipefail

    dnf update -y
    dnf install -y docker git
    systemctl enable --now docker
    usermod -aG docker ec2-user

    # Docker Compose v2 plugin
    DOCKER_CONFIG=/usr/local/lib/docker
    mkdir -p $DOCKER_CONFIG/cli-plugins
    curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
      -o $DOCKER_CONFIG/cli-plugins/docker-compose
    chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose

    # vm.max_map_count requis par Elasticsearch
    echo "vm.max_map_count=262144" >> /etc/sysctl.conf
    sysctl -p

    cd /home/ec2-user
    sudo -u ec2-user git clone --branch ${var.git_branch} ${var.git_repo_url} devops-monitoring
    cd devops-monitoring
    docker compose up -d
  EOF

  root_block_device {
    volume_size           = 30
    volume_type           = "gp3"
    delete_on_termination = true
    encrypted             = true   # chiffrement disque obligatoire
  }
}
```

**Outputs utiles** (post-déploiement) :

```hcl
output "grafana_url" {
  value = "http://${aws_instance.monitoring.public_dns}:3001"
}

output "jaeger_url" {
  value = "http://${aws_instance.monitoring.public_dns}:16686"
}
```

#### d) Procédure de déploiement

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# ajuster les variables (region, ssh_cidr, key_name)

terraform init      # télécharge le provider AWS
terraform plan      # vérifie ce qui va être créé
terraform apply     # provisionne réellement (~3 min)

# Une fois l'instance UP, attendre ~5 min que user-data finisse
# Puis ouvrir l'URL Grafana retournée en output
```

> **CAPTURES À INSÉRER ICI :**
> - Capture 1 : sortie de `terraform plan` montrant les ~12 ressources à créer
> - Capture 2 : sortie de `terraform apply` complète (3 min)
> - Capture 3 : console AWS EC2 Instances montrant l'instance `devops-monitoring-ec2` running
> - Capture 4 : console AWS VPC montrant le VPC, subnet, IGW créés
> - Capture 5 : SSH sur l'instance avec `docker compose ps` montrant les 12 services up

### 2.5 Résultats

| Indicateur | Avant | Après |
|---|---|---|
| Temps de déploiement complet | ~30 min manuel | ~5 min automatisé |
| Reproductibilité | Aucune (clic-clic AWS console) | 100 % (code versionné Git) |
| Lignes de code Terraform | 0 (rien) | 311 lignes |
| Ressources provisionnées | 0 | VPC + IGW + Subnet + RT + SG + EC2 + EBS |
| Possibilité de tear-down | Manuelle | `terraform destroy` |

### 2.6 Difficultés rencontrées et solutions

| Difficulté | Solution |
|---|---|
| Première version utilisait `ami-12345678` (AMI inexistante hardcodée) | Migration vers `data "aws_ami"` dynamique avec filtres |
| `terraform validate` échouait sans credentials AWS dans le CI | Job CI tolérant : `continue-on-error` au niveau du job |
| Bootstrap EC2 timing-sensitive (Elasticsearch nécessite `vm.max_map_count`) | Écriture explicite dans `/etc/sysctl.conf` + `sysctl -p` dans user-data |
| Disque EBS par défaut non chiffré | Ajout `encrypted = true` dans `root_block_device` |

### 2.7 Bilan professionnel

Cette réalisation m'a permis d'industrialiser le provisionnement d'une stack complexe (12 services). En production, j'irais plus loin avec :

- **Backend Terraform distant** (S3 + DynamoDB lock) pour le travail en équipe
- **Modules** réutilisables (un module `vpc/`, un module `ec2-monitoring/`)
- **Auto Scaling Group** plutôt qu'une seule EC2
- **Application Load Balancer** + ACM pour HTTPS
- **IAM Roles** plutôt que credentials statiques

---

## 3. Réalisation n°2 — Conteneurisation et orchestration de la stack d'observabilité

### 3.1 Compétences mobilisées

| Compétence | Couverture |
|---|---|
| **CP3 — Sécuriser l'infrastructure** | Multi-stage builds, utilisateur non-root, scan Trivy |
| **CP4 — Mettre en production l'application** | Docker Compose, healthchecks, dépendances, profiles |
| CP1 — Scripts d'automatisation | Scripts shell, CI GitHub Actions |
| CP2 — Infrastructure as Code | `docker-compose.yml` versionné |

### 3.2 Contexte et besoin

La plateforme comprend **12 services hétérogènes** (FastAPI, React, PostgreSQL, Prometheus, Grafana, AlertManager, Jaeger, Elasticsearch, Logstash, Kibana, node-exporter, cAdvisor). Lancer chacun manuellement (téléchargement, configuration, démarrage dans le bon ordre) est :

- Long (15-30 min)
- Source d'erreurs humaines
- Non reproductible
- Incompatible avec un environnement CI

Il fallait un orchestrateur déclaratif simple pour le poste de dev et la démo.

### 3.3 Objectifs

1. Décrire les 12 services dans un fichier `docker-compose.yml` unique
2. Garantir l'**ordre de démarrage** (Elasticsearch avant Logstash, Postgres avant backend)
3. Sécuriser les images applicatives (**Dockerfile multi-stage**, utilisateur **non-root**, healthchecks)
4. Externaliser la configuration via variables d'environnement (`.env`)
5. **Persister** les données critiques (volumes nommés)
6. Permettre l'activation conditionnelle (profiles Docker Compose pour les services Linux-only)

### 3.4 Démarche

#### a) Architecture des conteneurs

```
                          ┌──────────────┐
                          │   Frontend   │  React + nginx :3000
                          └──────┬───────┘
                                 │ REST + JWT
                          ┌──────▼───────┐
                          │   Backend    │  FastAPI :8000
                          └─┬─────┬─────┬┘
            /metrics        │     │     │ traces OTLP
                            │     │     │
                  ┌─────────▼┐ ┌──▼───┐ ▼──────────┐
                  │ Prometheus│ │Logstash│ Jaeger    │
                  │   :9090   │ │ :5000  │ :16686    │
                  └─────┬─────┘ └────┬───┘ └─────────┘
                        │            │
                  ┌─────▼─────┐ ┌────▼─────────┐ ┌────────┐
                  │  Grafana  │ │Elasticsearch │ │ Kibana │
                  │   :3001   │ │    :9200     │ │ :5601  │
                  └─────┬─────┘ └──────────────┘ └────────┘
                        │
                  ┌─────▼────────┐
                  │ AlertManager │  → Discord webhook + email
                  │   :9093      │
                  └──────────────┘
```

#### b) Dockerfile multi-stage du backend (sécurité + taille minimale)

```dockerfile
# syntax=docker/dockerfile:1.6
###############################################################################
# Stage 1 — builder : installation des dépendances dans un venv isolé
###############################################################################
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

###############################################################################
# Stage 2 — runtime : image minimale, utilisateur non-root
###############################################################################
FROM python:3.11-slim AS runtime

ENV PATH="/opt/venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends libpq5 curl \
    && rm -rf /var/lib/apt/lists/*

# Utilisateur non-root (sécurité)
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

# Healthcheck pour Docker / Kubernetes
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Justification du multi-stage :**

- L'image finale ne contient pas `gcc`, `build-essential`, `libpq-dev` qui ne servent qu'au build → **surface d'attaque réduite**.
- Taille divisée par ~3 (pas mesuré exactement, observation visuelle).
- L'utilisateur `appuser` non-root limite l'impact d'une éventuelle RCE.

#### c) docker-compose.yml — services et dépendances

Extrait commenté :

```yaml
services:
  db:
    image: postgres:15-alpine
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER:-monitoring}"]
      interval: 10s
    networks: [monitoring]

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://monitoring:monitoring@db:5432/monitoring
      JAEGER_ENDPOINT: http://jaeger:4317
      LOGSTASH_HOST: logstash
    depends_on:
      db:
        condition: service_healthy   # attend que postgres soit prêt
    networks: [monitoring]

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.13.0
    environment:
      discovery.type: single-node
      xpack.security.enabled: "false"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - es_data:/usr/share/elasticsearch/data   # persistance logs
    healthcheck:
      test: ["CMD-SHELL", "curl -fs http://localhost:9200/_cluster/health || exit 1"]

  logstash:
    image: docker.elastic.co/logstash/logstash:8.13.0
    depends_on:
      elasticsearch:
        condition: service_healthy   # attend ES avant logstash

  node-exporter:
    image: prom/node-exporter:v1.7.0
    profiles: ["linux"]   # désactivé sur Windows/macOS (mounts incompatibles)

# 5 volumes nommés pour la persistance
volumes:
  db_data:
  prometheus_data:
  alertmanager_data:
  grafana_data:
  es_data:
```

> **CAPTURES À INSÉRER ICI :**
> - Capture 6 : sortie de `docker compose ps` avec les 10 services running/healthy
> - Capture 7 : sortie de `docker compose images` montrant les images builded (devops-monitoring-backend, devops-monitoring-frontend) et leurs tailles
> - Capture 8 : `docker exec backend whoami` retournant `appuser` (preuve du non-root)
> - Capture 9 : Grafana ouvert sur http://localhost:3001 avec le dashboard "Business Metrics"

#### d) Sécurité : scan automatisé Trivy dans le CI

```yaml
# .github/workflows/ci.yml
- name: Run Trivy on Docker image
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ env.IMAGE_NAME }}:${{ github.sha }}
    format: table
    severity: CRITICAL,HIGH

- name: Run Trivy on filesystem
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: fs
    scan-ref: .
    severity: CRITICAL,HIGH
```

Chaque push sur `main` déclenche un scan automatique des **vulnérabilités CRITICAL et HIGH** dans :
- L'image Docker du backend
- Les dépendances Python du repo (filesystem scan)

### 3.5 Résultats

| Indicateur | Mesure |
|---|---|
| Services orchestrés | 12 (10 par défaut + 2 en profile linux) |
| Volumes persistants | 5 |
| Temps de démarrage froid | ~5 min (premier build) puis ~30s |
| Image backend (multi-stage) | Réduction estimée 3× vs single-stage |
| Tests unitaires backend | 11 tests (pytest), 100 % passés |
| Lignes du `docker-compose.yml` | 217 |

### 3.6 Difficultés rencontrées et solutions

| Difficulté | Solution |
|---|---|
| `passlib 1.7.4` incompatible avec `bcrypt 4.x` (erreur `password cannot be longer than 72 bytes`) | Pin `bcrypt==3.2.2` dans `requirements.txt` |
| `node-exporter` plantait sur Docker Desktop Windows (mounts `rslave` Linux-only) | Mise sous **profile `linux`** dans Compose, activable via `--profile linux` |
| `httpx >= 0.28` casse `TestClient` de Starlette (paramètre `app=` deprecated) | Pin `httpx==0.27.2` |
| Elasticsearch refusait de démarrer (`vm.max_map_count` trop bas sur l'host Linux) | Documentation runbook + correction dans `user_data` Terraform |
| Synchronisation problématique entre l'éditeur Windows et le mount Linux du sandbox (NULL bytes en fin de fichier) | Script de nettoyage automatique des NULL bytes |

### 3.7 Bilan professionnel

L'orchestration via Docker Compose m'a permis de manipuler une stack distribuée comme une seule unité. En production j'évoluerais vers :

- **Kubernetes** + Helm Charts (déjà disponibles pour Prometheus, Grafana, ELK)
- **Service Mesh** (Istio / Linkerd) pour mTLS et observabilité réseau
- **HPA** (Horizontal Pod Autoscaler) basé sur les métriques Prometheus
- **Secrets management** (Vault, External Secrets Operator) plutôt que `.env` plain

---

## 4. Synthèse de couverture des compétences du Bloc 1

| CP | Intitulé | Couverture | Preuves dans le projet |
|---|---|---|---|
| **CP1** | Réaliser des scripts d'automatisation et d'industrialisation | ✅ | `scripts/clean-git-history.sh`, user-data Terraform, `.github/workflows/ci.yml` |
| **CP2** | Mettre en œuvre l'IaC | ✅ | `terraform/main.tf` (311 lignes : VPC + EC2 + SG + AMI dynamique) |
| **CP3** | Sécuriser l'infrastructure | ✅ | Dockerfile multi-stage non-root, EBS chiffré, SG restrictif, scan Trivy CI, JWT bcrypt |
| **CP4** | Mettre en production l'application | ✅ | Docker Compose 12 services avec healthchecks et dépendances, user-data EC2 auto-deploy |

---

## 5. Ressources et liens

- **Code source** : https://github.com/YTA048/Devops-monitoring
- **CDC** : `docs/CDC.md`
- **Architecture** : `docs/architecture.md`
- **Business Metrics (BC03-CP2)** : `docs/business-metrics.md`
- **Runbook tests end-to-end** : `docs/RUNBOOK.md`
- **Workflow CI** : `.github/workflows/ci.yml`
- **Terraform** : `terraform/main.tf`, `terraform/README.md`
- **Docker Compose** : `docker-compose.yml`, `docker-compose.test.yml`

---

## 6. Captures d'écran à intégrer

Pour rendre ce dossier conforme à l'attendu RNCP, **intégrer les 9 captures** mentionnées dans les sections 2.4 et 3.4.

Procédure de capture (sur poste de dev) :

| # | Capture | Commande / URL |
|---|---|---|
| 1 | `terraform plan` | `cd terraform && terraform plan` |
| 2 | `terraform apply` | `terraform apply` (à la fin du déploiement) |
| 3 | Console AWS EC2 | https://console.aws.amazon.com/ec2 |
| 4 | Console AWS VPC | https://console.aws.amazon.com/vpc |
| 5 | SSH + `docker compose ps` | `ssh -i key.pem ec2-user@<IP>` puis `docker compose ps` |
| 6 | `docker compose ps` local | `docker compose ps` |
| 7 | `docker compose images` | `docker compose images` |
| 8 | Preuve non-root | `docker exec backend whoami` → `appuser` |
| 9 | Grafana Business Metrics | http://localhost:3001 → dashboard "Business Metrics" |

Chaque capture doit être placée à l'endroit indiqué `[CAPTURE À INSÉRER ICI]`, légendée et numérotée.

---

*Document rédigé dans le cadre de la préparation au titre professionnel Administrateur Systèmes DevOps.*
