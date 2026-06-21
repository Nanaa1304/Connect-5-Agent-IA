# Connect 5 — Agent IA (Negamax + PVS + Zobrist)


## Description

Ce projet implémente un agent autonome (`IntelligentPlayer`) capable de jouer au
**Connect 5**, une variante du Puissance 4 jouée sur une grille 16×16 où l'objectif
est d'aligner 5 pions consécutifs (horizontalement, verticalement ou en diagonale).

L'agent doit choisir un coup valide en respectant une contrainte de temps stricte
d'environ **1 seconde par tour**.

## Algorithme

L'agent repose sur une recherche **Negamax + Alpha-Beta Pruning** enrichie de
plusieurs optimisations :

- **PVS (Principal Variation Search)** pour accélérer l'élagage Alpha-Beta
- **Zobrist Hashing** + table de transposition pour éviter de réévaluer des positions déjà vues
- **Évaluation incrémentale O(1)** basée sur un pré-calcul de toutes les fenêtres de 5 cases du plateau
- **Move ordering avancé** : coup de la table de transposition, *killer moves*, *history heuristic*, priorité au centre
- **Détection de victoire locale O(K)** autour du dernier coup joué (plutôt qu'un scan complet du plateau)
- **Iterative Deepening (IDDFS)** avec seuil de temps adaptatif (~0.85s) pour rester sous la limite d'1s
- **Recherche tactique immédiate** : détection des coups gagnants et des coups bloquant une victoire adverse avant la recherche en profondeur

### Résultats

- 10/10 victoires contre `RandomPlayer`
- Temps de calcul maximal observé : ~0.80s (sous la limite d'1s imposée)
- Profondeur de recherche atteinte : 6 à 8 plis selon la position

## Structure du dépôt

```
.
├── agent.py          # Implémentation de IntelligentPlayer (l'agent IA)
├── board.py           # Représentation du plateau de jeu (Board, Move)
├── game.py            # Interface graphique (pygame) + boucle de jeu
├── randomplayer.py     # Agent de référence jouant aléatoirement
├── player.py           # (à fournir) classe de base BasePlayer + HumanPlayer
└── README.md
```


## Prérequis

```bash
pip install pygame
```

## Lancer une partie

Agent IA contre joueur humain :

```bash
python game.py --p1 player.HumanPlayer --p2 agent.IntelligentPlayer
```

Agent IA contre l'agent aléatoire de référence :

```bash
python game.py --p1 agent.IntelligentPlayer --p2 randomplayer.RandomPlayer
```

Deux instances de l'agent IA l'une contre l'autre :

```bash
python game.py --p1 agent.IntelligentPlayer --p2 agent.IntelligentPlayer
```

## Contraintes du projet

- Plateau : grille 16×16, alignement de 5 pions
- Temps maximal par coup : 1 seconde (sous peine de disqualification)
- La classe doit hériter de `BasePlayer` et implémenter `choose_move(board)`
