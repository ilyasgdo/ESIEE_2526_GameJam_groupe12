# ESIEE_2526_GameJame_groupe12
## PRD — « Tu n’es pas le héros » (Python)

Version: 0.1 (brouillon)
Date: 2025-09-16
Auteur: Équipe GameJam Groupe 12

### 1) Contexte & Objectifs

- **Pitch**: Le héros est contrôlé par une IA qui traverse des niveaux. Le joueur, en périphérie, influence l’environnement (pièges, ennemis, aides), sans contrôler directement le protagoniste. À chaque mort, l’IA apprend et s’adapte.
- **Objectif produit**: Créer un prototype jouable (MVP) en Python mettant en avant la boucle « Préparation → Run → Résultat/Shop », l’adaptation IA niveau 1 (danger map), et une économie simple.
- **Plateformes cibles (MVP)**: Desktop (Windows, Linux, macOS). Export exécutable via PyInstaller.
- **Public**: Joueurs PC aimant la stratégie légère, l’IA et les expériences méta-narratives.

### 2) Vision & Expérience

- **Expérience recherchée**: ressentir que l’action principale vous échappe. Vous êtes un artisan de l’ombre qui influence subtilement; l’IA progresse visiblement entre les runs.
- **Tonalité**: narration environnementale (affiches, radios, PNJ). Résultats locaux, pas cosmiques.

### 3) Périmètre (par jalons)

- **Jalon A — Prototype vertical (MVP)**
  1. 1 niveau (tilemap) top-down ou side-scroller grid.
  2. Héros IA avec A* et points de vie.
  3. 1 type de piège (mine): coût 10, single-use, dégâts létaux.
  4. Économie: +10 pièces si mort du héros; cap de gains par run.
  5. Adaptation IA (Tier 1): danger_map pénalisant les cellules meurtrières au prochain run.
  6. UI minimale: pièces, bouton Start/Run, HP du héros.
  7. Debug overlay: chemin A* et heatmap danger.

- **Jalon B — Core loop & polish**
  1. Shop UI et 3 pièges (mine, spike trap, noise maker).
  2. Enemy spawner (distractor/ennemis simples).
  3. Behaviour tree simple pour l’IA (sélection éviter/avancer).
  4. Écran de résultats + heatmap.

- **Jalon C-F (optionnels)**: narration, 5 niveaux, replay/analytics, multijoueur/leaderboards, localisation, optimisation et packaging.

### 4) Boucle de jeu (Core Loop)

1. **Préparation**: le joueur place des pièges sur la grille (prévisualisation, coût, validation).
2. **Run**: l’IA héro se déplace vers l’objectif en suivant A*. Les pièges se déclenchent, le héros peut mourir ou réussir.
3. **Résultat**: affichage résumé (morts, pièces, pièges déclenchés), mise à jour de la danger_map et du solde.
4. **Shop**: achat de pièges/consommables pour la prochaine préparation.

### 5) Mécaniques clés

- **Pièges (MVP)**: Mine cachée; coût=10; dégâts élevés; usage unique; déclenchement à contact.
- **Pièges (B)**: Spike Trap (ralentit + dégâts), Noise Maker (événement son, attire ennemis/distrait).
- **Ennemis (B)**: distractor (n’attaque pas, détourne l’IA), basic melee (simple poursuite).
- **Économie**:
  - Gain sur mort du héros: +10 pièces (configurable) ; réussite rapporte une fraction.
  - Caps: `max_coins_per_run` et éventuellement cap journalier.
  - ROI: équilibre coût/efficacité via cooldowns ou rareté.
- **Adaptation IA (Tier 1)**:
  - `danger_map[cell] += weight` à chaque mort causée par la cellule/piège.
  - Coût A*: `cell_cost = base_cost + danger_map[cell] * penalty_factor`.
  - Si chemin bloqué: choix d’un chemin alternatif; sinon demande d’assistance (placeholder).

### 6) Niveaux & Monde

- **Tilemap** via Tiled Editor (.tmx). Chargement avec `pytmx`, scrolling avec `pyscroll` si nécessaire.
- **Métadonnées**: spawn points, goal, navGraph/noeuds. Tags de zone (crowded/stealth/noisy) pour extensions futures.
- **MVP**: 1 carte compacte, lisible, avec quelques chemins alternatifs.

### 7) UI/UX

- **HUD**: pièces, cooldowns (si B), nombre de pièges actifs, état du run.
- **Minimap (optionnel)**: position du héros, objectif, fog partiel.
- **Placement**: grille, preview d’effet (portée), coût, confirmation rapide.
- **Run**: bouton pause, interventions limitées (B).
- **Écran Résultats**: résumé (morts, pièces, pièges déclenchés), heatmap danger.

### 8) Télémétrie & Replays

- **Événements**: `trap_placed`, `trap_triggered`, `hero_death(cause)`, `coins_change`, `a_star_path_hash`, `hero_action`.
- **Replays**: seed + état initial + liste compacte d’événements → rejouabilité locale.
- **KPIs de playtest**: `mean_time_to_goal`, `deaths_per_run`, `trap_activation_rate`, `coin_flow`, popularité des pièges, densité de placement.

### 9) Stack technique (Python)

- **Langage**: Python 3.11+
- **Rendu/Input**: `pygame-ce`
- **Tilemaps**: `pytmx` (+ `pyscroll` si maps grandes)
- **Pathfinding**: `networkx` (graphe + A*) ou `pathfinding`
- **Behaviour Trees (B)**: `py_trees`
- **RL (optionnel)**: `gymnasium`, `stable-baselines3`, `torch`
- **Persistance**: JSON (MVP), `sqlite3` si besoin
- **Tests**: `pytest`
- **Profiling**: `cProfile`
- **Packaging**: `pyinstaller`

Exemple `requirements.txt` (indicatif):

```
pygame-ce>=2.4
pytmx>=3.32
pyscroll>=2.29
networkx>=3.2
pathfinding>=1.0
py_trees>=2.2      # optionnel jalon B
gymnasium>=0.29    # optionnel RL
stable-baselines3>=2.3  # optionnel RL
torch              # optionnel RL
pytest>=8.0
```

### 10) Architecture technique (modules)

Arborescence proposée:

```
project/
├─ main.py
├─ game_manager.py
├─ ui_manager.py
├─ level_manager.py
├─ hero_ai/
│  ├─ pathfinding.py
│  ├─ behaviour_tree.py
│  └─ memory.py
├─ traps/
│  ├─ trap_manager.py
│  └─ trap_types.json
├─ enemies/
│  └─ enemy_manager.py
├─ shop/
│  └─ shop_manager.py
├─ analytics/
│  └─ logger.py
├─ assets/
│  ├─ sprites/
│  ├─ maps/
│  └─ sounds/
└─ saves/
   └─ progress.json
```

Responsabilités principales:

- `GameManager`: états (LOBBY → PREPARATION → RUNNING → RESULT), règle monnaie globale, sauvegarde.
- `LevelManager`: carte, collisions, triggers, waypoints, pièges/ennemis présents.
- `HeroAI`: perception, A*, mémoire (danger_map), décision (FSM/BT simple).
- `TrapManager`: définition/placement/activation/cooldowns; événements.
- `EnemyManager`: spawns/IA basique; interaction avec HeroAI.
- `ShopManager`: catalogue JSON, achats, vérifs coûts/inventaire.
- `AnalyticsLogger`: enregistre événements, export JSON (replay/analytique).

### 11) Spécifications data (exemples)

- `TrapType` (trap_types.json):

```
[
  {
    "id": "mine",
    "name": "Mine",
    "cost": 10,
    "cooldown": 0,
    "active_duration": 0,
    "trigger_condition": "on_enter",
    "effect": { "damage": 999, "stun": 0 },
    "visibility": "hidden"
  }
]
```

- `HeroState` (runtime):

```
{
  "pos": [x, y],
  "health": 100,
  "inventory": [ { "itemId": "potion", "count": 1 } ],
  "memory": { "danger_map": { "cellKey": 3 } },
  "learned_counters": { "mine": 1 }
}
```

- `LevelMeta` (chargée via TMX + meta JSON):

```
{
  "id": "level_01",
  "tileset": "assets/maps/level_01.tmx",
  "spawnPoints": [[1,1]],
  "goal": [20,12],
  "navGraph": "grid"
}
```

- `TelemetryEvent`:

```
{ "ts": 123456789, "runId": 1, "eventType": "trap_triggered", "payload": { "trapId": "mine", "pos": [5,6] } }
```

### 12) Exigences fonctionnelles (MVP)

1. Le joueur peut placer une mine sur des cellules valides pendant la phase Préparation.
2. Le bouton Start lance la phase Run; l’IA planifie un chemin A* vers l’objectif.
3. La mine inflige des dégâts létaux au héros quand il entre sur la cellule.
4. Si le héros meurt: +10 pièces; `danger_map` mise à jour; affichage Résultat.
5. Si réussite: gains réduits; affichage Résultat.
6. L’écran Résultat récapitule morts/coins/chemin (overlay heatmap).
7. Le Shop permet d’acheter au moins une mine supplémentaire pour la prochaine run.
8. Sauvegarde/chargement du solde de pièces et de la `danger_map` en JSON.

### 13) Exigences non-fonctionnelles

- **Performance**: 60 FPS visé sur PC standard; recalcul A* amorti (pas chaque frame).
- **Déterminisme**: seed initial loggé pour rejouabilité; mêmes entrées → même run.
- **Qualité**: tests unitaires (pathfinding, économie, lifecycle pièges). Mode debug overlay.
- **Accessibilité**: options volume, tailles police UI, daltonisme (plus tard).
- **Localisation**: FR en priorité; structure JSON prête pour EN.

### 14) Règles d’équilibrage initiales

- Mine: coût 10; létale; visibilité faible; stock limité; pas de cooldown.
- Cap par run: `max_coins_per_run = 20` (exemple). Ajustable via config.
- Penalty danger_map: `penalty_factor = 2` (exemple).

### 15) KPIs & Suivi

- **KPIs**: temps moyen jusqu’à l’objectif; morts/run; taux d’activation des pièges; flux de pièces; % réussite par run.
- **Objectifs MVP**: 3–6 minutes par session; 1–3 morts/run; activation mine 30–60%.
- **Collecte**: via `AnalyticsLogger` export JSON; dashboards simples (CSV → notebook externe).

### 16) Risques & Mitigations

- IA trop forte/faible → itération sur `penalty_factor`/coûts; A/B configs.
- Pathfinding coûteux → cache partiel, grille hiérarchique (plus tard), Numba/Cython si besoin.
- UX placement peu clair → preview visuel + tooltips + validation.
- Scope dérive → verrouiller MVP (1 niveau, 1 piège), feature flags pour le reste.

### 17) Roadmap & DoD

- **Semaine 1 (Jalon A)**: base projet, rendu, input, tilemap, IA A*, mine, économie, sauvegarde JSON, UI minimale, overlay debug.
  - DoD: run complet jouable; mort donne pièces; danger_map modifie le chemin suivant.
- **Semaine 2 (B partiel)**: shop UI, 2 pièges additionnels, écran résultats+heatmap, premiers ennemis.
  - DoD: achat et utilisation de 3 pièges; heatmap visible; un type d’ennemi fonctionnel.

### 18) Ouvertures (questions à trancher)

1. Top-down vs side-scroller pour le MVP ?
2. Visibilité des mines (complètement cachées vs indiquées discrètement) ?
3. Gains sur réussite: pourcentage exact vs palier fixe ?
4. Doit-on afficher la danger_map au joueur (transparence vs mystère) ?
5. Extent de la minimap au MVP ?

### 19) Checklist d’acceptation (MVP)

- Lancement → Préparation → Run → Résultat → Shop → Retour Préparation fonctionne sans crash.
- Le héros atteint parfois l’objectif (chemins alternatifs) et meurt parfois sur la mine.
- Les gains/épuisements de pièces s’affichent correctement et sont persistés.
- La `danger_map` affecte les runs suivants de manière observable.
- Les événements clés sont loggés et exportables.

### 20) Annexes

- Inspirations mécaniques: tower defense inversé, gestion d’IA adaptative.
- Outils auteurs: Tiled Editor pour créer des cartes rapidement.


