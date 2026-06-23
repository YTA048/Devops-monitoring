#!/bin/bash
###############################################################################
# Script de provisionnement — Kit monitoring agence web
#
# Ce script installe et configure automatiquement Docker + Docker Compose
# sur un serveur Linux (Ubuntu 22.04 / Amazon Linux 2023).
#
# Usage :
#   chmod +x setup-serveur.sh
#   sudo ./setup-serveur.sh
#
# Idempotent : peut être relancé plusieurs fois sans effet de bord.
###############################################################################

set -euo pipefail

LOG_FILE="/var/log/provision-monitoring.log"
REPO_URL="https://github.com/YTA048/Devops-monitoring.git"
INSTALL_DIR="/opt/monitoring"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "=== Début du provisionnement ==="

###############################################################################
# 1. Mise à jour du système
###############################################################################
log "1. Mise à jour des paquets..."
if command -v apt-get &>/dev/null; then
    apt-get update -y
    apt-get upgrade -y
elif command -v yum &>/dev/null; then
    yum update -y
fi
log "   Système à jour."

###############################################################################
# 2. Installation de Docker
###############################################################################
log "2. Installation de Docker..."

if command -v docker &>/dev/null; then
    log "   Docker déjà installé : $(docker --version)"
else
    if command -v apt-get &>/dev/null; then
        # Ubuntu / Debian
        apt-get install -y ca-certificates curl gnupg
        install -m 0755 -d /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        chmod a+r /etc/apt/keyrings/docker.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
            https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
            > /etc/apt/sources.list.d/docker.list
        apt-get update -y
        apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    elif command -v yum &>/dev/null; then
        # Amazon Linux / CentOS / RHEL
        yum install -y docker
        systemctl enable docker
        systemctl start docker
        # Docker Compose plugin
        mkdir -p /usr/local/lib/docker/cli-plugins
        curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64" \
            -o /usr/local/lib/docker/cli-plugins/docker-compose
        chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
    fi
    log "   Docker installé : $(docker --version)"
fi

###############################################################################
# 3. Démarrage de Docker
###############################################################################
log "3. Démarrage du service Docker..."
systemctl enable docker
systemctl start docker
log "   Docker actif."

###############################################################################
# 4. Clonage du projet
###############################################################################
log "4. Clonage du projet dans $INSTALL_DIR..."

if [ -d "$INSTALL_DIR/.git" ]; then
    log "   Projet déjà cloné — mise à jour..."
    git -C "$INSTALL_DIR" pull
else
    git clone "$REPO_URL" "$INSTALL_DIR"
fi
log "   Projet prêt."

###############################################################################
# 5. Configuration de l'environnement
###############################################################################
log "5. Configuration des variables d'environnement..."

if [ ! -f "$INSTALL_DIR/.env" ]; then
    cp "$INSTALL_DIR/.env.example" "$INSTALL_DIR/.env"
    log "   Fichier .env créé depuis .env.example"
    log "   IMPORTANT : éditer $INSTALL_DIR/.env pour renseigner les vraies valeurs"
else
    log "   Fichier .env déjà présent."
fi

###############################################################################
# 6. Lancement de la stack
###############################################################################
log "6. Lancement de la stack Docker..."
cd "$INSTALL_DIR"
docker compose up -d
log "   Stack lancée."

###############################################################################
# 7. Vérification
###############################################################################
log "7. Vérification des conteneurs..."
sleep 5
docker compose ps

log ""
log "=== Provisionnement terminé avec succès ==="
log ""
log "URLs disponibles :"
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "IP_SERVEUR")
log "  Grafana      : http://$SERVER_IP:3001  (admin/admin)"
log "  Prometheus   : http://$SERVER_IP:9090"
log "  Alertmanager : http://$SERVER_IP:9093"
log ""
log "Logs complets : $LOG_FILE"
