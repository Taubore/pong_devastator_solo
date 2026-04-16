# Pong Devastator Solo

Mini-projet d’apprentissage de Python avec `pygame-ce`.

L’objectif est de construire progressivement un Pong solo très simple, inspiré de
*Code the Classics* volume 1, en gardant un code lisible, pédagogique et facile à
tester.

## Fonctionnalités actuelles

- Ouverture d’une fenêtre Pygame.
- Fermeture propre avec la croix de la fenêtre ou la touche `Échap`.
- Affichage de deux raquettes, d’une balle, d’un score et d’une ligne centrale
  pointillée.
- Lancement de la balle avec la touche `Espace`.
- Déplacement de la raquette du joueur avec les flèches `Haut` et `Bas`.
- Détection simple des collisions avec les murs et les raquettes.
- Comptage du score quand la balle sort à gauche ou à droite.

## Prérequis

- Linux
- Python `3.12.3`
- `pygame-ce`
- VSCode avec le profil `Python_PyGame_CE` recommandé

## Installation

Créer puis activer l’environnement virtuel :

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Installer la dépendance principale :

```bash
python -m pip install pygame-ce
```

## Lancement

Depuis la racine du projet :

```bash
python main.py
```

## Contrôles

- `Espace` : lancer la balle.
- `Haut` : monter la raquette du joueur.
- `Bas` : descendre la raquette du joueur.
- `Échap` : quitter le jeu.

## Notes de développement

- Le projet est volontairement simple et travaille principalement dans `main.py`.
- Les changements doivent rester petits, progressifs et faciles à relire.
- L’environnement de référence est un workspace VSCode sous Linux avec
  l’environnement Python `.venv`.
- Éviter de modifier l’architecture ou les outils sans besoin concret observé.
- Les affichages de débogage doivent passer par `logging.debug()` plutôt que par
  des `print()` permanents dans la boucle du jeu.
- Les sons sont chargés dans `Jeu`, puis transmis aux objets qui en ont besoin,
  afin d’éviter que les classes de jeu connaissent directement les fichiers
  `.wav`.

## Pièges et solutions de contournement

- Utiliser `pygame-ce` plutôt que le paquet historique `pygame` pour rester
  cohérent avec l’environnement du projet.
- Lancer le jeu depuis l’environnement virtuel `.venv` afin d’éviter les écarts
  entre les dépendances globales et celles du projet.
- Lors d’un rebond sur une raquette, recaler la balle selon son sens d’arrivée
  horizontal plutôt que selon sa position après collision. La balle peut déjà
  être entrée dans le rectangle de la raquette au moment du test.
- Utiliser `IntEnum` pour les côtés du terrain quand la valeur doit aussi servir
  de direction numérique (`-1` ou `1`). Un `Enum` classique demande `.value`
  pour être utilisé dans un calcul.
