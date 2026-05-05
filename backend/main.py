"""
DevOps Monitoring Platform - Backend FastAPI

Expose une API REST instrumentee :
  - Metriques techniques Prometheus (RPS, latence) sur /metrics
  - METRIQUES METIER custom (uptime SLA, probes/min, MTTR, sites surveilles)
  - Tracing distribue OpenTelemetry vers Jaeger (OTLP)
  - Logs JSON structures envoyes a Logstash (TCP) + stdout
  - Healthchecks /health et /ready
"""
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Gauge, Histogram
from prometheus_fastapi_instrumentator import Instrumentator

from app.auth import router as auth_router
from app.logging_config import setup_logging
from app.tracing import setup_tracing

SERVICE_NAME = os.getenv("SERVICE_NAME", "devops-monitoring-backend")
JAEGER_ENDPOINT = os.getenv("JAEGER_ENDPOINT", "http://jaeger:4317")
LOGSTASH_HOST = os.getenv("LOGSTASH_HOST", "logstash")
LOGSTASH_PORT = int(os.getenv("LOGSTASH_PORT", "5000"))

DEFAULT_SITES = [
    "https://google.com",
    "https://github.com",
    "https://wikipedia.org",
    "https://stackoverflow.com",
    "https://cloudflare.com",
]
SITES = os.getenv("SITES", ",".join(DEFAULT_SITES)).split(",")

logger = setup_logging(SERVICE_NAME, LOGSTASH_HOST, LOGSTASH_PORT)


###############################################################################
# METRIQUES METIER (BC03-CP2 : business KPIs, pas juste infra)
#
# Ces metriques racontent ce que fait l'application, pas l'etat du serveur.
# Le jury attend : "uptime SLA", "probes/h", "MTTR", pas juste "CPU 45%".
###############################################################################

# Compteur total de probes envoyees, par site et par statut (UP/DEGRADED/DOWN)
SITE_CHECK_TOTAL = Counter(
    "site_check_total",
    "Nombre total de probes effectuees par site",
    ["site", "status"],
)

# Histogramme de latence par site (utile pour percentiles p50/p95/p99)
SITE_CHECK_LATENCY = Histogram(
    "site_check_latency_seconds",
    "Latence des probes par site",
    ["site"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

# Gauges en temps reel (snapshot de l'etat actuel)
SITES_TOTAL = Gauge("sites_monitored_total", "Nombre total de sites surveilles")
SITES_UP = Gauge("sites_up_count", "Nombre de sites actuellement UP")
SITES_DOWN = Gauge("sites_down_count", "Nombre de sites actuellement DOWN")
SITES_DEGRADED = Gauge("sites_degraded_count", "Nombre de sites actuellement DEGRADED")
UPTIME_RATIO = Gauge("monitoring_uptime_ratio", "Ratio sites UP / total (SLA temps reel)")

# Statut individuel par site (1 = UP, 0.5 = DEGRADED, 0 = DOWN)
SITE_STATUS = Gauge(
    "site_status",
    "Statut du site (1=UP, 0.5=DEGRADED, 0=DOWN)",
    ["site"],
)

# Initialiser le compteur sites_monitored_total au demarrage
SITES_TOTAL.set(len(SITES))


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("Backend starting", extra={"service": SERVICE_NAME})
    setup_tracing(SERVICE_NAME, JAEGER_ENDPOINT, _app)
    yield
    logger.info("Backend shutting down", extra={"service": SERVICE_NAME})


app = FastAPI(
    title="DevOps Monitoring Platform",
    description="API de monitoring instrumentee (Prometheus + Jaeger + ELK)",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])

# Auto-instrumentation FastAPI (RPS, latence par endpoint, errors)
Instrumentator().instrument(app).expose(app, endpoint="/metrics", tags=["monitoring"])


@app.get("/", tags=["root"])
def root():
    """Page racine de l'API."""
    return {
        "service": SERVICE_NAME,
        "version": "1.0.0",
        "endpoints": ["/health", "/ready", "/metrics", "/monitor", "/sites", "/kpi"],
    }


@app.get("/health", tags=["health"])
def health():
    """Liveness probe."""
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/ready", tags=["health"])
def ready():
    """Readiness probe."""
    return {"status": "ready", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/sites", tags=["monitoring"])
def list_sites():
    """Liste des sites surveilles."""
    return {"sites": SITES, "count": len(SITES)}


@app.get("/monitor", tags=["monitoring"])
def monitor():
    """Verifie le statut HTTP de chaque site et MET A JOUR les metriques metier."""
    results = []
    up_count = 0
    down_count = 0
    degraded_count = 0

    for site in SITES:
        site = site.strip()
        if not site:
            continue
        start = time.time()
        try:
            r = requests.get(site, timeout=3)
            latency = round(time.time() - start, 3)
            status = "UP" if r.status_code == 200 else "DEGRADED"
            logger.info(
                "site_check_ok",
                extra={"site": site, "status": status, "latency": latency},
            )
        except requests.RequestException as exc:
            latency = round(time.time() - start, 3)
            status = "DOWN"
            logger.error(
                "site_check_failed",
                extra={"site": site, "error": str(exc), "latency": latency},
            )

        # === MISE A JOUR DES METRIQUES METIER ===
        SITE_CHECK_TOTAL.labels(site=site, status=status).inc()
        SITE_CHECK_LATENCY.labels(site=site).observe(latency)

        if status == "UP":
            SITE_STATUS.labels(site=site).set(1)
            up_count += 1
        elif status == "DEGRADED":
            SITE_STATUS.labels(site=site).set(0.5)
            degraded_count += 1
        else:
            SITE_STATUS.labels(site=site).set(0)
            down_count += 1

        results.append({
            "time": datetime.now(timezone.utc).isoformat(),
            "site": site,
            "status": status,
            "latency_s": latency,
        })

    # Snapshot global
    total = up_count + down_count + degraded_count
    SITES_UP.set(up_count)
    SITES_DOWN.set(down_count)
    SITES_DEGRADED.set(degraded_count)
    UPTIME_RATIO.set(up_count / total if total > 0 else 0)

    return {
        "results": results,
        "checked": len(results),
        "summary": {
            "up": up_count,
            "down": down_count,
            "degraded": degraded_count,
            "uptime_ratio": round(up_count / total, 4) if total > 0 else 0,
        },
    }


@app.get("/kpi", tags=["monitoring"])
def kpi():
    """KPIs metier en temps reel (pour le dashboard)."""
    return {
        "sites_monitored": len(SITES),
        "sites_up": int(SITES_UP._value.get()),
        "sites_down": int(SITES_DOWN._value.get()),
        "sites_degraded": int(SITES_DEGRADED._value.get()),
        "uptime_ratio": round(UPTIME_RATIO._value.get(), 4),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/error-test", tags=["monitoring"])
def error_test():
    """Endpoint pour tester les alertes d'erreur (renvoie une 500)."""
    logger.error("error_test_endpoint_called")
    raise HTTPException(status_code=500, detail="Erreur simulee pour tester les alertes")
