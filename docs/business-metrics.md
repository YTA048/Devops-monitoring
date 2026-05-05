# BC03-CP2 — Business metrics, capacity planning et forecast

> Le jury n'évalue pas BC03-CP2 sur "vous avez Prometheus".
> Il évalue sur **"vous comprenez votre métier à travers les chiffres"**.

Ce document explique la logique de monitoring **métier** mise en place dans le projet, distincte du monitoring d'infrastructure.

---

## Le métier de la plateforme

Le métier ici n'est **pas** "exposer une API REST". L'API est juste l'interface.

Le **vrai métier** : **superviser la disponibilité de sites web tiers et alerter en cas de panne.**

Les questions auxquelles l'utilisateur de la plateforme veut répondre :

- Mes 5 sites surveillés sont-ils tous UP en ce moment ?
- Lequel de mes sites est le moins fiable sur 7 jours ?
- Combien de probes échouent en moyenne ?
- Quelle est ma latence p95 sur chaque site ?
- Suis-je en train de tenir mon SLA de 99.7 % ?

Le dashboard `Business Metrics — Monitoring Platform` répond exactement à ces questions.

---

## Les 4 niveaux du dashboard

Conformément aux best practices de supervision avancée, le dashboard est structuré en 4 lignes de granularité croissante :

### Ligne 1 — BUSINESS METRICS (le métier)

| KPI | Formule Prometheus | Décision déclenchée |
|---|---|---|
| Sites surveillés | `sites_monitored_total` | Visibilité de la couverture |
| Probe Uptime SLA | `monitoring_uptime_ratio` | Si < 99.7 %, breach SLA → ticket |
| Probes / heure | `sum(rate(site_check_total[1h])) * 3600` | Cadence de surveillance |
| Sites DOWN (24h) | `sum(increase(site_check_total{status="DOWN"}[24h]))` | Si > 5, anomalie réseau récurrente |
| Alertes firing | `sum(ALERTS{alertstate="firing"})` | Charge de travail des SRE |

### Ligne 2 — APPLICATION METRICS (mes utilisateurs voient-ils des problèmes ?)

| KPI | Formule | Décision |
|---|---|---|
| Backend error rate (5m) | `rate(http_requests_total{status=~"5.."}) / rate(http_requests_total)` | Si > 1 %, debug |
| Latence p95 | `histogram_quantile(0.95, ...)` | Si > 1s, optimiser |
| Requests / sec | `sum(rate(http_requests_total[1m]))` | Capacity planning |
| Backend uptime | `up{job="backend"}` | Dispatch immédiat si DOWN |

### Ligne 3 — INFRASTRUCTURE (nécessaire mais pas suffisant)

CPU / RAM / Disk via `node-exporter` (activable en prod Linux avec `--profile linux`).

### Ligne 4 — TRENDS & FORECAST (anticiper avant que ça casse)

- **Statut des sites par site** (timeseries) : on voit *quel* site est le moins fiable
- **Latence p95 par site** : si une courbe monte, le site se dégrade → debug **avant** que les utilisateurs se plaignent
- **Probes/min par statut** : stack chart UP / DEGRADED / DOWN
- **Uptime ratio SLA trend** avec moyenne 1h : permet de **forecaster** un breach SLA

---

## Métriques custom exposées par le backend

Le backend expose ces métriques sur `/metrics`, additionnellement aux `http_requests_total` auto-instrumentées :

```
# Counter par site et statut
site_check_total{site="https://google.com",status="UP"} 142
site_check_total{site="https://google.com",status="DEGRADED"} 0
site_check_total{site="https://google.com",status="DOWN"} 1

# Histogram pour percentiles de latence par site
site_check_latency_seconds_bucket{site="https://google.com",le="0.05"} 12
site_check_latency_seconds_bucket{site="https://google.com",le="0.1"} 87
...

# Gauges en temps reel
sites_monitored_total 5
sites_up_count 4
sites_degraded_count 1
sites_down_count 0
monitoring_uptime_ratio 0.8
site_status{site="https://google.com"} 1
```

---

## Capacity planning : prévoir avant que ça casse

### Exemple appliqué

Imaginons que sur 7 jours on observe :

```
Jour 1 : 5 sites surveillés, ratio UP = 100%
Jour 4 : 5 sites, ratio UP = 95%
Jour 7 : 5 sites, ratio UP = 90%
Forecast : ratio < 80% à J11 → breach SLA imminent
```

### Décision préventive

À J7 (quand ratio = 90%), le SRE :

1. Identifie le site fautif via le panel "Statut des sites"
2. Vérifie sa latence : si elle a doublé, problème réseau ou CPU côté cible
3. Soit retire le site du monitoring (s'il est définitivement down), soit ouvre un ticket auprès du provider

**C'est exactement ce que le jury veut entendre :**

> "Mon dashboard m'a dit que mon SLA va breach à J11. À J7 j'ai pris l'action préventive X."

---

## Alertes métier (vs alertes infra)

5 alertes business définies dans `monitoring/alerts/alerts.yml` :

| Alerte | Seuil | Catégorie |
|---|---|---|
| `ProbeUptimeSLABreach` | uptime < 95 % pendant 5 min | critical / business |
| `SiteDownPersistent` | site_status == 0 pendant 3 min | critical / business |
| `SiteHighLatency` | p95 > 2s par site pendant 5 min | warning / business |
| `ProbeFailureRateHigh` | > 10 % de probes DOWN sur 10 min | warning / business |
| `NoMonitoringDataReceived` | aucune probe pendant 5 min | critical / business |

Chaque alerte a 3 annotations :

- `summary` : ce qui se passe
- `description` : les détails techniques
- `decision` : **l'action à prendre** (ce que le jury attend)

Exemple :

```yaml
- alert: SiteHighLatency
  annotations:
    summary: "Site {{ $labels.site }} - latence p95 > 2s"
    description: "..."
    decision: "Forecast: si la latence double dans les 5 prochains jours,
                le site sera marque DEGRADED. Investiguer maintenant."
```

---

## Le narrative pour la soutenance

Au lieu de :

> "Voici mon dashboard. CPU à 45 %, RAM à 62 %."

Dis :

> "Voici les 5 sites que je supervise. Mon SLA temps réel est à 99.8 % sur les 30 dernières minutes (panel 'Probe Uptime SLA'). Le site `stackoverflow.com` a vu sa latence p95 monter de 280 ms à 450 ms en 24 h (panel 'Latence par site'). Si la tendance continue, j'aurai un breach SLA dans ~3 jours. J'ai donc déjà préparé la commande pour augmenter le timeout de probe de 3s à 5s, ou retirer ce site si la dégradation persiste. Mon AlertManager m'envoie sur Discord toute alerte critical."

C'est ça qui convainc le jury BC03-CP2.

---

## Checklist soutenance BC03-CP2

- [x] Dashboard avec **données métier** (pas juste CPU)
- [x] Alertes qui **concernent l'app** (sites, SLA, probes)
- [x] **Tendances** visibles (timeseries 30m, par site)
- [x] **Forecast** documenté (capacity planning sur uptime ratio)
- [x] Décision justifiée pour chaque alerte (champ `decision`)
- [x] Métriques **custom** exposées par le backend (5 séries metier)
- [x] Endpoint `/kpi` qui résume les KPIs en JSON pour le frontend

---

## Liens utiles

- Dashboard JSON : `grafana/dashboards/business-metrics.json`
- Backend metrics : `backend/main.py` (section `METRIQUES METIER`)
- Alertes business : `monitoring/alerts/alerts.yml` (groupe `business_alerts`)
- Endpoint KPI : http://localhost:8000/kpi
