"""
DevOps Monitoring Platform - Backend FastAPI

Expose une API REST instrumentee :
  - Metriques Prometheus sur /metrics
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

Instrumentator().instrument(app).expose(app, endpoint="/metrics", tags=["monitoring"])


@app.get("/", tags=["root"])
def root():
    """Page racine de l'API."""
    return {
        "service": SERVICE_NAME,
        "version": "1.0.0",
        "endpoints": ["/health", "/ready", "/metrics", "/monitor", "/sites"],
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
    """Verifie le statut HTTP de chacun des sites surveilles."""
    results = []
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

        results.append({
            "time": datetime.now(timezone.utc).isoformat(),
            "site": site,
            "status": status,
            "latency_s": latency,
        })
    return {"results": results, "checked": len(results)}


@app.get("/error-test", tags=["monitoring"])
def error_test():
    """Endpoint pour tester les alertes d'erreur (renvoie une 500)."""
    logger.error("error_test_endpoint_called")
    raise HTTPException(status_code=500, detail="Erreur simulee pour tester les alertes")
