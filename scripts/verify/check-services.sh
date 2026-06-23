#!/bin/bash
###############################################################################
# Script de vérification post-déploiement
#
# Vérifie que tous les services répondent correctement après déploiement.
# Retourne 0 si tout est OK, 1 si au moins un service ne répond pas.
#
# Usage :
#   chmod +x check-services.sh
#   ./check-services.sh
###############################################################################

set -euo pipefail

HOST="${1:-localhost}"
ERRORS=0

check() {
    local name=$1
    local url=$2
    local expected=${3:-200}

    STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url" || echo "000")

    if [ "$STATUS" = "$expected" ]; then
        echo "  OK  $name ($url) → HTTP $STATUS"
    else
        echo "  KO  $name ($url) → HTTP $STATUS (attendu $expected)"
        ERRORS=$((ERRORS + 1))
    fi
}

echo "=== Vérification des services — $(date '+%Y-%m-%d %H:%M:%S') ==="
echo ""

check "Prometheus"         "http://$HOST:9090/-/healthy"
check "Alertmanager"       "http://$HOST:9093/-/healthy"
check "Blackbox Exporter"  "http://$HOST:9115/metrics"
check "Node Exporter"      "http://$HOST:9100/metrics"
check "Grafana"            "http://$HOST:3001/api/health"

echo ""
if [ "$ERRORS" -eq 0 ]; then
    echo "Résultat : tous les services sont opérationnels."
    exit 0
else
    echo "Résultat : $ERRORS service(s) ne répondent pas."
    exit 1
fi
