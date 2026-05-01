#!/usr/bin/env bash
###############################################################################
# Nettoyage de l'historique Git
#
# Supprime node_modules/, monitoring.db et .venv/ de l'ENSEMBLE de l'historique
# (pas juste du HEAD). Utilise git-filter-repo (recommandé par GitHub).
#
# ATTENTION : ce script réécrit l'historique. Tous les collaborateurs devront
# re-cloner le repo après le force-push.
###############################################################################
set -euo pipefail

# 0. Sécurité : on doit être à la racine du repo et sans changes en cours
if [ ! -d ".git" ]; then
  echo "ERREUR : à exécuter depuis la racine du repo Git." >&2
  exit 1
fi

if ! git diff-index --quiet HEAD --; then
  echo "ERREUR : il y a des changements non commités. Commit ou stash d'abord." >&2
  exit 1
fi

# 1. Vérifier que git-filter-repo est installé
if ! command -v git-filter-repo &>/dev/null; then
  echo "ERREUR : git-filter-repo n'est pas installé." >&2
  echo ""
  echo "Installation :"
  echo "  Windows (avec pip) : pip install git-filter-repo"
  echo "  macOS              : brew install git-filter-repo"
  echo "  Linux              : apt-get install git-filter-repo  (ou via pip)"
  exit 1
fi

# 2. Backup
BRANCH=$(git rev-parse --abbrev-ref HEAD)
BACKUP="backup-$(date +%Y%m%d-%H%M%S)"
echo "[*] Backup branch : $BACKUP"
git branch "$BACKUP"

# 3. Filter-repo : supprime les chemins indésirables
echo "[*] Suppression de node_modules/, monitoring.db, .venv/, *.db de l'historique..."
git filter-repo --invert-paths \
  --path node_modules/ \
  --path .venv/ \
  --path backend/monitoring.db \
  --path-glob "*.db" \
  --force

# 4. Garbage collect
echo "[*] git gc --aggressive..."
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 5. Re-ajouter le remote (filter-repo le supprime par sécurité)
echo ""
echo "[*] Filter-repo a supprimé le remote. Tu dois maintenant :"
echo "     git remote add origin <URL_DU_REPO>"
echo "     git push --force --all origin"
echo "     git push --force --tags origin"
echo ""
echo "Backup gardé sur la branche : $BACKUP"
echo "Pour vérifier la taille du repo : du -sh .git"
