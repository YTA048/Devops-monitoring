---
title: "Script Vidéo — Présentation DevOps Monitoring Platform"
subtitle: "Format pitch 3 minutes pour soutenance ou partage prof"
author: "Yassine TAIFI BERNOUSSI"
date: "Mai 2026"
---

# 🎬 Script Vidéo Globale — 3 minutes

> Vidéo de pitch synthétique pour présenter le projet *DevOps Monitoring Platform*.
> Format conseillé : vidéo de 1080p, voix-off + screencast.

---

## ⏱ Découpage temporel

| Section | Durée | Visuel à montrer |
|---|---|---|
| 1. Hook / accroche | 0:00 – 0:15 | Slide titre + ton visage |
| 2. Problématique | 0:15 – 0:35 | Animation MTTR qui explose |
| 3. Solution & stack | 0:35 – 1:00 | Schéma architecture 3 piliers |
| 4. Démo live | 1:00 – 2:00 | Écran de Grafana + Jaeger + Discord |
| 5. Couverture compétences | 2:00 – 2:30 | Matrice slide 13 |
| 6. Call to action | 2:30 – 3:00 | Repo GitHub + contact |

---

## 🎙 Script complet à lire (3 minutes / ~420 mots)

### 🎬 0:00 – 0:15 — Hook

*[Caméra sur toi, sourire confiant, fond clair]*

> **« Bonjour, je suis Yassine TAIFI BERNOUSSI. En trois minutes, je vais vous montrer comment j'ai conçu une plateforme d'observabilité conteneurisée qui détecte un incident en moins d'une minute et alerte les équipes en direct sur Discord. »**

---

### 📉 0:15 – 0:35 — Problématique

*[Transition vers une animation : graphique avec MTTR qui monte en flèche]*

> **« Le problème est simple. Dans un environnement cloud distribué, sans outils d'observabilité, les incidents sont détectés tardivement, leur origine reste floue, et le temps moyen de résolution explose. Ma plateforme attaque ce problème de front avec une cible claire : un uptime SLA de 99,8 % et une détection sous une minute. »**

---

### 🏗 0:35 – 1:00 — Solution & Stack

*[Montrer le schéma d'architecture, zoom sur les 3 piliers]*

> **« J'ai construit une solution qui repose sur les trois piliers reconnus de l'observabilité : les métriques avec Prometheus et Grafana, les logs avec la stack ELK, et les traces avec Jaeger et OpenTelemetry. Douze services orchestrés en un seul docker compose, 311 lignes de Terraform pour le déploiement AWS, et un pipeline CI/CD GitHub Actions tout vert. »**

---

### 🎥 1:00 – 2:00 — Démo live (60 sec)

*[Screencast plein écran — enchaîner ces 4 actions]*

> **Action 1** *(15 sec)* : terminal → `docker compose ps`
> **Voix off** : « D'abord, je vérifie que mes douze services sont tous *healthy*. »

> **Action 2** *(15 sec)* : navigateur → Grafana *Business Metrics*
> **Voix off** : « J'ouvre Grafana sur mon dashboard métier : seize panels, mes KPIs vivants, le SLA en temps réel à 99,8 %. »

> **Action 3** *(15 sec)* : Jaeger UI → recherche trace
> **Voix off** : « Côté traces, Jaeger me montre une requête de bout en bout, avec ses spans imbriqués. »

> **Action 4** *(15 sec)* : `docker compose stop logstash` → attente → Discord
> **Voix off** : « Et le clou : j'arrête un service, et soixante-dix secondes plus tard, l'alerte arrive sur Discord. C'est ça, l'observabilité en pratique. »

---

### 🎯 2:00 – 2:30 — Couverture compétences

*[Slide matrice à l'écran, encadrer chaque ligne pendant que tu parles]*

> **« Le projet n'est pas juste une démo : il valide les dix compétences techniques du titre Administrateur Systèmes DevOps. Bloc 1 : scripts, IaC, sécurité, mise en production. Bloc 2 : tests, stockage, conteneurisation, CI/CD. Bloc 3 : KPIs métier et supervision à trois piliers. Chaque compétence a sa preuve concrète, versionnée sur GitHub. »**

---

### 🔗 2:30 – 3:00 — Call to action

*[Retour caméra sur toi, écran avec QR code repo GitHub]*

> **« Le code est entièrement public, vous trouverez le lien en description : github.com/YTA048/Devops-monitoring. Documentation complète, dossier professionnel, dossier projet, rapports de tests : tout est livré. Je reste à votre disposition pour toute question. Merci pour votre attention. »**

---

## 🎬 Comment enregistrer la vidéo

### Matériel nécessaire

| Élément | Recommandation |
|---|---|
| Caméra | Webcam HD ou téléphone (1080p minimum) |
| Micro | Casque-micro ou micro USB (priorité son qualité) |
| Éclairage | Lumière naturelle face à toi, pas derrière |
| Fond | Mur clair uni ou bibliothèque rangée |

### Logiciel d'enregistrement

| Option | Quand l'utiliser |
|---|---|
| **OBS Studio** *(gratuit)* | Recommandé : combine webcam + screencast + audio |
| **Loom** *(gratuit jusqu'à 5 min)* | Plus simple, parfait pour ce pitch de 3 min |
| **PowerPoint Enregistrer la présentation** | Si tu veux juste les slides + voix off |
| **Zoom (s'enregistrer seul)** | Solution de secours |

### Workflow recommandé (OBS)

1. Crée deux **scènes OBS** :
   - *Scène 1* : webcam plein écran (intro, conclusion)
   - *Scène 2* : capture d'écran + webcam en mini-vignette (démo)
2. Lance ton enregistrement
3. Bascule entre les scènes avec un raccourci clavier
4. Exporte en MP4 1080p

### Workflow rapide (Loom)

1. Installe l'extension Chrome Loom
2. Choisis *Screen + Cam*
3. Clique *Start Recording*
4. Suis ton script
5. Loom génère le lien partageable

---

## 💡 Conseils de tournage

### Pendant l'enregistrement

- **Parle plus lentement** que d'habitude (le cerveau du jury a besoin de temps pour absorber)
- **Souris** au moins en intro et conclusion
- **Regarde la caméra**, pas l'écran (pose ton script juste à côté de l'objectif)
- **Pause de 1 seconde** entre chaque section, ça facilite le montage

### En cas d'erreur

- **Ne reprends pas tout depuis le début !**
- Tape dans tes mains, attends 3 secondes, recommence la phrase
- Au montage, tu coupes simplement aux applaudissements

### Post-production (15 min)

- **CapCut** ou **DaVinci Resolve** (gratuits) pour couper les ratés
- Ajoute un **sous-titrage automatique** (très important pour l'accessibilité)
- Mets une **musique de fond** très discrète (-30 dB max) optionnelle

---

## 📤 Diffusion

| Plateforme | Pour quoi |
|---|---|
| **YouTube** (non-listée) | Diffusion principale, lien à mettre dans le repo |
| **LinkedIn** | Mettre en avant ton profil DevOps |
| **Fichier MP4** | Partage direct au prof Max |
| **QR Code** | À mettre sur le slide 18 « Questions » du PowerPoint |

---

## ✅ Checklist avant publication

- [ ] Son clair, pas de souffle ni de saturations
- [ ] Image stable, pas de mouvements brusques
- [ ] Démo fluide (avoir testé le scénario 3 fois)
- [ ] Sous-titres générés (auto via YouTube ou CapCut)
- [ ] Vidéo en 1080p minimum
- [ ] Durée entre 2:50 et 3:10 (la concision est ta force)
- [ ] Lien GitHub vérifié dans la description
- [ ] Vidéo non-listée si publiée sur YouTube (jury seulement)

---

## 📋 Variante : version pour le prof Max

Si la vidéo est destinée à ton prof référent (Max), ajoute ce paragraphe en intro :

> **« Bonjour Monsieur, en complément du PowerPoint et des dossiers que je vous ai transmis, je vous propose cette présentation vidéo de trois minutes qui synthétise les points clés du projet. Elle me sert aussi d'entraînement à la prise de parole pour le jury. Je serais reconnaissant d'avoir votre avis. »**

Et termine par :

> **« Si vous repérez des points à améliorer dans la présentation orale ou des éléments techniques à mieux expliciter, je suis preneur de vos retours. Merci pour votre temps. »**
