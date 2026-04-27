## 📌 Contexte du projet

Ce projet consiste à développer une plateforme de monitoring DevOps permettant de superviser des applications web en temps réel.

L’objectif est de fournir une solution complète d’observabilité incluant :
- la collecte de métriques (Prometheus)
- la visualisation (Grafana)
- le tracing distribué (Jaeger)
- la gestion des logs (ELK Stack)

## 🎯 Objectifs

- Surveiller la performance d’une application FastAPI
- Détecter les anomalies (latence, erreurs)
- Centraliser les logs
- Fournir une interface de visualisation

## 👤 Utilisateurs cibles

- DevOps Engineers
- SRE (Site Reliability Engineers)
- Développeurs backend

## ⚙️ Contraintes

- Déploiement conteneurisé (Docker)
- Architecture microservices
- Monitoring temps réel
- Scalabilité possible

## 🧱 Architecture

Le système est composé de :
- Backend FastAPI (API + métriques)
- Frontend React (UI)
- Prometheus (metrics)
- Grafana (dashboard)
- Jaeger (tracing)
- ELK (logs)

## 🚀 Valeur ajoutée

Ce projet démontre la mise en place d’une stack d’observabilité complète utilisée en entreprise.
# DevOps Monitoring Platform

## ?? Stack
- FastAPI (Backend)
- React (Frontend)
- Docker Compose
- Prometheus + Grafana
- Jaeger (Tracing)
- ELK Stack (Logs)
- AlertManager

## ?? Features
- Metrics monitoring
- Logs analysis
- Distributed tracing
- Alerting system

## ?? Run
docker compose up --build

## ?? Access
- Frontend: http://localhost:3001
- Backend: http://localhost:8000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- Jaeger: http://localhost:16686
- Kibana: http://localhost:5601

