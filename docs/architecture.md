# Architecture — Kit de monitoring agence web

## Contexte

Une agence web héberge les sites de ses clients sur un serveur Linux.
Elle a besoin de savoir en temps réel :
- Si les sites des clients sont en ligne ou en panne
- Si les sites répondent rapidement
- Si le serveur qui les héberge est en bonne santé (CPU, RAM, disque)
- Recevoir une alerte immédiate quand quelque chose ne va pas

---

## Schéma d'architecture

```
Sites clients (internet)
  https://client-1.fr
  https://client-2.com          ← sondes HTTP toutes les 30s
  https://client-3.fr
         │
         ▼
┌─────────────────────────┐
│   blackbox-exporter     │  Port 9115
│   Sonde HTTP GET        │  → probe_success (0/1)
│   Mesure la latence     │  → probe_duration_seconds
└────────────┬────────────┘
             │ métriques
             ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│      prometheus         │◄────│     node-exporter       │
│      Port 9090          │     │     Port 9100           │
│  Collecte toutes les    │     │  CPU, RAM, Disque       │
│  métriques (30s)        │     │  du serveur Linux       │
│  Évalue les alertes     │     └─────────────────────────┘
└────────┬────────────────┘
         │              │ alertes
         ▼              ▼
┌──────────────┐  ┌──────────────────┐
│   grafana    │  │  alertmanager    │
│   Port 3001  │  │  Port 9093       │
│  Dashboards  │  │  → Email Outlook │
│  6 KPI       │  │  (111562@        │
│  visuels     │  │   ecole-it.com)  │
└──────────────┘  └──────────────────┘
```

---

## Les 5 services et leur rôle

| Service | Image Docker | Port | Rôle |
|---------|-------------|------|------|
| **blackbox-exporter** | prom/blackbox-exporter:v0.25.0 | 9115 | Sonde HTTP des sites clients |
| **node-exporter** | prom/node-exporter:v1.7.0 | 9100 | Métriques système du serveur |
| **prometheus** | prom/prometheus:v2.51.0 | 9090 | Collecte, stockage, alertes |
| **grafana** | grafana/grafana:10.4.0 | 3001 | Dashboards visuels |
| **alertmanager** | prom/alertmanager:v0.27.0 | 9093 | Envoi des notifications |

---

## Les 6 KPI surveillés

| KPI | Métrique Prometheus | Seuil d'alerte |
|-----|--------------------|-----------------|
| Sites UP / DOWN | `probe_success` | 0 = alerte immédiate |
| Latence des sites | `probe_duration_seconds` | > 2s → warning |
| Disponibilité 24h | `avg_over_time(probe_success[24h])` | < 99% → warning |
| CPU serveur | `node_cpu_seconds_total` | > 80% pendant 2 min |
| RAM serveur | `node_memory_MemAvailable_bytes` | > 85% pendant 2 min |
| Disque serveur | `node_filesystem_avail_bytes` | > 90% pendant 5 min |

---

## Flux d'une alerte

```
1. Prometheus détecte : probe_success == 0 depuis 1 minute
2. Prometheus envoie l'alerte à Alertmanager
3. Alertmanager groupe les alertes (30s d'attente)
4. Alertmanager envoie un email à 111562@ecole-it.com
5. Sujet : "[CRITIQUE] SiteDown — https://client.fr"
6. L'alerte se répète toutes les 30 min si le site reste DOWN
7. Un email "RÉSOLUE" est envoyé quand le site revient
```

---

## Sécurité

- **Aucun secret dans le code** : tous les mots de passe sont dans `.env` (exclu de Git)
- **`.gitignore`** inclut `.env`, `*.tfvars`, `.terraform/`, `*.tfstate`
- **Terraform** : Security Group AWS restreint (SSH uniquement depuis IP autorisée)
- **Volumes persistants** : données Prometheus et Grafana conservées entre redémarrages

---

## Déploiement production (Terraform AWS)

L'infrastructure est décrite dans `terraform/main.tf` :

- VPC dédié (10.0.0.0/16) avec Internet Gateway
- Subnet public
- Security Group : SSH restreint + ports monitoring
- EC2 t3.micro Amazon Linux 2023
- User-data : installe Docker + clone le repo + lance la stack automatiquement

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Renseigner les variables AWS
terraform init
terraform plan
terraform apply
```

---

## Environnements

| Environnement | Fichier | Ports | Usage |
|--------------|---------|-------|-------|
| **Production** | `docker-compose.yml` | 3001, 9090, 9093, 9100, 9115 | Surveillance réelle |
| **Test** | `docker-compose.test.yml` | 13001, 19090, 19093, 19100, 19115 | Validation + démo alertes |

L'environnement de test inclut un site fictif (`site-en-panne-test.xyz`) pour déclencher l'alerte `SiteDown` sans impacter la production.

---

## Provisionnement automatisé

Le script `scripts/provision/setup-serveur.sh` :
1. Met à jour le système (apt/yum)
2. Installe Docker et Docker Compose
3. Clone le repo depuis GitHub
4. Crée le fichier `.env`
5. Lance la stack avec `docker compose up -d`

Le script `scripts/verify/check-services.sh` vérifie que tous les services répondent après déploiement.
