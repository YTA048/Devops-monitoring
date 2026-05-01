# Scripts de maintenance

## clean-git-history.sh

Nettoie l'historique Git en supprimant `node_modules/`, `.venv/` et `monitoring.db` de **tous les commits**.

### Prérequis

Installer `git-filter-repo` (l'outil officiel recommandé par GitHub) :

```bash
# Windows / Linux (via pip)
pip install git-filter-repo

# macOS
brew install git-filter-repo
```

### Exécution

```bash
cd devops-monitoring
bash scripts/clean-git-history.sh
```

Le script :

1. Crée une branche de backup `backup-YYYYMMDD-HHMMSS`
2. Lance `git filter-repo` pour réécrire tous les commits
3. Garbage collect

### Après exécution

`filter-repo` supprime le remote par sécurité. Tu dois le ré-ajouter et force-pusher :

```bash
git remote add origin git@github.com:<user>/devops-monitoring.git
git push --force --all origin
git push --force --tags origin
```

### Notes importantes

- Le force-push réécrit l'historique distant. Tous les collaborateurs devront **re-cloner** le repo.
- La branche backup locale te permet de revenir en arrière si problème : `git reset --hard backup-YYYYMMDD-HHMMSS`.
- Vérifier la taille du repo après : `du -sh .git/`.
