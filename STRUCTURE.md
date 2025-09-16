# Structure du Projet "Tu n'es pas le héros"

## Vue d'ensemble
Ce projet est un jeu 2D pygame où le joueur influence l'environnement pour aider ou nuire à un héros contrôlé par l'IA.

## Structure des dossiers

```
project/
├── main.py                    # Point d'entrée principal
├── game_manager.py           # Gestionnaire principal du jeu
├── requirements.txt          # Dépendances Python
├── .gitignore               # Fichiers à ignorer par Git
├── STRUCTURE.md             # Ce fichier
│
├── hero_bot/                # IA du héros principal
│   └── .gitkeep
│
├── AllierJoueur/            # Bot allié contrôlé par le joueur
│   └── .gitkeep
│
├── traps/                   # Système de pièges
│   └── .gitkeep
│
├── Allierbot/               # Bots alliés automatiques
│   └── .gitkeep
│
├── shop/                    # Système de magasin
│   └── .gitkeep
│
├── analytics/               # Logging et analytics
│   └── .gitkeep
│
├── assets/                  # Ressources du jeu
│   ├── sprites/            # Images et sprites
│   │   └── .gitkeep
│   ├── maps/               # Cartes et niveaux
│   │   └── .gitkeep
│   └── sounds/             # Sons et musique
│       └── .gitkeep
│
└── saves/                   # Sauvegardes
    └── .gitkeep
```

## Fonctionnalités actuelles

### main.py
- Initialisation de pygame
- Création de la fenêtre de jeu (1024x768)
- Boucle principale du jeu
- Gestion des événements (fermeture, échap)

### game_manager.py
- Gestion des états du jeu (LOBBY, PREPARATION, RUNNING, RESULT)
- Affichage d'un niveau basique avec grille
- IA simple du héros (mouvement vers l'objectif)
- Système de pièges basique
- Interface utilisateur minimale
- Économie simple (pièces)

## Contrôles actuels
- **ESPACE** : Démarrer un run
- **R** : Reset du jeu
- **S** : Entrer dans le shop
- **ÉCHAP** : Quitter le jeu

## Prochaines étapes
1. Implémenter le placement de pièges
2. Ajouter le système de magasin
3. Améliorer l'IA du héros avec pathfinding
4. Ajouter des ennemis
5. Implémenter la danger_map pour l'adaptation IA

## Installation et lancement

1. Installer les dépendances :
```bash
pip install -r requirements.txt
```

2. Lancer le jeu :
```bash
python main.py
```

## Architecture technique
- **Python 3.11+** avec pygame-ce
- **Pathfinding** : networkx + pathfinding
- **Tilemaps** : pytmx + pyscroll
- **IA** : py_trees pour les behaviour trees
- **Tests** : pytest
- **Packaging** : pyinstaller
