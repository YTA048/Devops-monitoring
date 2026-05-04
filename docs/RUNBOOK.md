# Runbook - Tests end-to-end

Ce document explique comment **prouver** que la plateforme fonctionne reellement (pas juste que les containers tournent). C'est le test qu'il faut faire avant la soutenance.

---

## 0. Pre-requis

```bash
# Copier les variables d'environnement
cp .env.example .env

# Editer .env et au minimum mettre :
# - DISCORD_WEBHOOK_URL : votre vrai webhook Discord
# - JWT_SECRET          : une chaine aleatoire 32 chars+
# - GRAFANA_PASSWORD    : mot de passe Grafana fort
```

### Creer un webhook Discord (5 min)

1. Sur Discord, click droit sur un channel > **Edit Channel** > **Integrations** > **Webhooks** > **New Webhook**
2. Donner un nom (ex: "DevOps Alerts"), copier l'URL du webhook
3. Coller dans `.env` : `DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...`

### Lancer la stack

```bash
docker compose up -d

# Verifier que tous les services sont healthy (peut prendre 2-3 min pour Elasticsearch)
docker compose ps
```

Tous les services doivent etre `running` ou `healthy`.

---

## 1. Test des metriques Prometheus

```bash
# 1. Voir les metriques exposees par le backend
curl http://localhost:8000/metrics | head -20

# 2. Generer du trafic
for i in {1..20}; do curl -s http://localhost:8000/monitor > /dev/null; done

# 3. Verifier dans Prometheus
# Aller sur http://localhost:9090
# Query : http_requests_total{job="backend"}
# On doit voir le compteur augmenter
```

**OK si :** la query renvoie une valeur > 0 et augmente apres chaque appel.

---

## 2. Test du tracing Jaeger

```bash
# 1. Generer du trafic instrumente
for i in {1..10}; do curl -s http://localhost:8000/monitor > /dev/null; done

# 2. Ouvrir Jaeger UI
# http://localhost:16686
# - Service : devops-monitoring-backend
# - Click "Find Traces"
```

**OK si :** on voit des traces avec :
- L'endpoint `GET /monitor` au top
- Des spans enfants pour chaque appel `requests.get(site)` (un par site)
- Les durations en ms

**Capture d'ecran a faire pour la soutenance.**

---

## 3. Test des logs ELK

```bash
# 1. Generer un evenement d'erreur
curl http://localhost:8000/error-test

# 2. Voir les logs dans le backend (stdout, format JSON)
docker compose logs backend | tail -5

# 3. Ouvrir Kibana
# http://localhost:5601
# Premier passage : creer un Data View
#  - Stack Management > Data Views > Create
#  - Name: "logs-*", Index pattern: "logs-*", Timestamp: "@timestamp"
# Aller dans Discover, choisir le data view, voir les logs.
```

**OK si :** Kibana montre les logs JSON avec les champs `service`, `level`, `message`.

**Capture d'ecran a faire.**

---

## 4. Test des alertes (LE PLUS IMPORTANT)

### 4.a. Test alerte InstanceDown -> Discord

```bash
# 1. Tuer node-exporter (simule une defaillance)
docker compose stop node-exporter

# 2. Attendre 1 minute (la regle "for: 1m" doit declencher)
sleep 70

# 3. Verifier dans Prometheus
# http://localhost:9090/alerts
# L'alerte InstanceDown doit etre en "FIRING" (rouge)

# 4. Verifier dans AlertManager
# http://localhost:9093
# L'alerte doit apparaitre dans la liste

# 5. VERIFIER DISCORD
# Le message doit arriver sur le channel Discord configure
```

**OK si :** Discord recoit un message avec :
- 🚨 ALERT - InstanceDown
- Severity: critical
- Instance: node-exporter:9100

### 4.b. Resolution -> Discord

```bash
# Redemarrer node-exporter
docker compose start node-exporter

# Attendre 1-2 min, Discord doit recevoir :
# ✅ RESOLVED - InstanceDown
```

### 4.c. Test alerte BackendHighErrorRate

```bash
# Generer 20 erreurs (taux > 5% requis)
for i in {1..20}; do curl -s http://localhost:8000/error-test > /dev/null; done

# Attendre 2 min (regle "for: 2m")
# Discord doit recevoir l'alerte BackendHighErrorRate
```

**Capture d'ecran de Discord recevant l'alerte = preuve definitive pour BC03-CP2.**

---

## 5. Test du frontend React

```bash
# Ouvrir http://localhost:3000
# Login : admin / admin123
# Le dashboard doit montrer :
# - 5 sites surveilles
# - Le statut UP/DOWN/DEGRADED
# - Le graphique en bar de la latence
# - Le tableau des resultats
# - Refresh automatique toutes les 15s
```

---

## 6. Test du CI/CD

```bash
# Pousser un commit - GitHub Actions doit tourner :
git commit --allow-empty -m "test: trigger CI"
git push origin main

# Verifier https://github.com/<user>/Devops-monitoring/actions
# Tous les jobs doivent etre verts :
#  - Lint
#  - Tests (11 passed)
#  - Build Docker image
#  - Security scan (Trivy)
#  - Terraform validate + fmt
```

---

## 7. Test du deploiement Terraform (optionnel)

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Editer terraform.tfvars

terraform init
terraform plan    # Verifier ce qui va etre cree
# terraform apply   # ATTENTION : coute de l'argent AWS

# Apres apply, recuperer l'IP publique :
terraform output ec2_public_ip

# Attendre 3-5 min que le user_data finisse (clone + docker compose up)
# SSH et verifier :
# ssh -i ~/.ssh/your-key.pem ec2-user@<IP>
# docker compose ps

# Detruire pour ne pas laisser de cout
terraform destroy
```

---

## Checklist avant soutenance

- [ ] `.env` cree avec vrais Discord webhook + SMTP credentials
- [ ] Stack lancee : `docker compose up -d`
- [ ] Tous les services UP : `docker compose ps`
- [ ] Test 1 : metriques Prometheus generent du trafic, query OK
- [ ] Test 2 : Jaeger UI montre des traces (screenshot)
- [ ] Test 3 : Kibana montre les logs (screenshot)
- [ ] Test 4 : alerte InstanceDown declenche message Discord (screenshot)
- [ ] Test 4 : alerte BackendHighErrorRate fonctionne (screenshot)
- [ ] Test 5 : frontend React loginable + dashboard charge
- [ ] Test 6 : GitHub Actions tous verts
- [ ] (optionnel) Test 7 : Terraform plan reussi
