# Cahier des Charges — DevOps Monitoring Platform

## 1. Contexte

Dans les environnements modernes (cloud et microservices), les applications sont distribuées et complexes. Les équipes DevOps ont besoin d'outils permettant de superviser les performances, détecter les incidents et analyser rapidement les problèmes en production.

Sans observabilité, les systèmes deviennent difficiles à maintenir et à optimiser, et le temps moyen de résolution (MTTR) explose lors des incidents.

---

## 2. Problématique

Comment surveiller efficacement une application distribuée afin de :

- Détecter rapidement les anomalies (latence, taux d'erreur, indisponibilité)
- Comprendre l'origine des incidents grâce au tracing distribué
- Centraliser les logs pour un debug rapide
- Garantir la disponibilité et la performance des services
- Alerter automatiquement les équipes en cas de dégradation

---

## 3. Solution proposée

Ce projet consiste à développer une plateforme de monitoring et d'observabilité basée sur une stack DevOps moderne, conteneurisée et orchestrée via Docker Compose.

Elle permet de :

- Collecter des métriques applicatives et système (Prometheus + node-exporter)
- Visualiser les données dans des dashboards (Grafana)
- Tracer les requêtes de bout en bout (Jaeger + OpenTelemetry)
- Centraliser les logs (ELK Stack : Elasticsearch + Logstash + Kibana)
- Générer des alertes automatiques (AlertManager)
- Provisionner l'infrastructure cloud (Terraform sur AWS)
- Automatiser l'intégration continue (GitHub Actions : lint, tests, build, scan sécurité)

---

## 4. Architecture technique

Le système est basé sur une architecture microservices conteneurisée.

**Application :**

- Backend : FastAPI (Python 3.11) — API REST instrumentée + endpoint `/metrics` Prometheus
- Frontend : React 18 + Vite — dashboard utilisateur avec graphiques Chart.js
- Base de données : PostgreSQL 15
- Orchestration : Docker Compose (dev) / Terraform + EC2 (prod)

**Stack d'observabilité :**

| Composant | Rôle | Port |
|-----------|------|------|
| Prometheus | Collecte des métriques | 9090 |
| Grafana | Dashboards de visualisation | 3001 |
| Jaeger | Tracing distribué (OTLP) | 16686 |
| Elasticsearch | Stockage des logs | 9200 |
| Logstash | Pipeline de logs (TCP→ES) | 5000 |
| Kibana | Exploration des logs | 5601 |
| AlertManager | Gestion des alertes | 9093 |
| node-exporter | Métriques système hôte | 9100 |

**Infrastructure as Code :**

- Terraform : provisionnement AWS (VPC, Subnet, Security Group, EC2 t3.micro, user_data Docker)
- AMI dynamique via `data "aws_ami"` (Amazon Linux 2023)

**CI/CD :**

- GitHub Actions : lint Python (pylint), tests unitaires (pytest), build Docker, scan vulnérabilités (Trivy)

---

## 5. Cas d'usage

- Monitoring temps réel des performances d'une API (latence p50/p95/p99, RPS, taux d'erreur)
- Détection automatique des services indisponibles (alertes < 1 min)
- Analyse des temps de réponse par endpoint
- Debugging via tracing distribué (root cause analysis)
- Visualisation des logs en temps réel et corrélation logs/métriques/traces
- Notification automatique en cas de saturation CPU/mémoire ou taux d'erreur élevé

---

## 6. Utilisateurs cibles

- DevOps Engineers
- Site Reliability Engineers (SRE)
- Développeurs backend
- Équipes de support production

---

## 7. Valeur ajoutée

- Vision complète du système (les 3 piliers de l'observabilité : metrics + logs + traces)
- Détection proactive des incidents avant impact utilisateur
- Amélioration de la fiabilité et des performances
- Réduction du temps de diagnostic (MTTR)
- Stack 100% open source, pas de vendor lock-in

---

## 8. Contraintes techniques

- Déploiement conteneurisé (Docker / Docker Compose)
- Architecture microservices
- Monitoring temps réel (scrape interval ≤ 15s)
- Scalabilité horizontale possible
- Sécurité : utilisateur non-root dans les containers, secrets via variables d'environnement, scan d'images

---

## 9. Évolutions possibles

- Déploiement cloud automatisé via Terraform (AWS)
- CI/CD avancé avec déploiement continu (GitOps)
- Intégration d'IA pour la détection d'anomalies (Prophet, LSTM)
- Auto-scaling basé sur les métriques Prometheus
- Migration vers Kubernetes (Helm charts)
- Service mesh (Istio / Linkerd) pour observabilité avancée
