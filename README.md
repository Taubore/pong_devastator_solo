# Pong Devastator Solo

Mini-projet d’apprentissage de Python avec `pygame-ce`.

Le programme est un Pong solo simple : le joueur contrôle la raquette de gauche,
l’ordinateur contrôle celle de droite, et le premier à `3` points gagne.

## Lancement rapide

Depuis la racine du projet :

```bash
source .venv/bin/activate
python main.py
```

Si l’environnement virtuel n’existe pas encore :

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install pygame-ce
```

## Contrôles

- `Espace` : démarrer depuis l’écran titre, lancer la balle ou recommencer après
  une partie terminée.
- `Haut` : monter la raquette du joueur.
- `Bas` : descendre la raquette du joueur.
- `Échap` : quitter le jeu.

## Organisation du code

- `main.py` : boucle principale, états du jeu, affichage, événements, score et
  collisions.
- `configuration.py` : réglages principaux du jeu.
- `balle.py` : déplacement, rebonds, accélération et rendu de la balle.
- `raquette.py` : déplacement et rendu des raquettes.
- `commun.py` : énumérations partagées (`Cote`, `EtatJeu`).
- `assets/` : images et sons utilisés par le jeu.

## Points d’attention

- Utiliser `pygame-ce`, pas le vieux paquet `pygame`.
- Lancer le projet avec l’environnement `.venv` pour éviter les écarts de
  dépendances.
- `Cote` est un `IntEnum`, car ses valeurs servent aussi de directions
  numériques (`-1` et `1`).
- La balle stocke sa position en `float`, puis son rectangle est recalculé pour
  les collisions.
- Après un rebond sur une raquette, la direction de la balle est normalisée.
  L’angle vertical est borné avant cette normalisation pour éviter une balle trop
  verticale ou flottante.
- Le texte utilise une police monospace en gras avec anticrénelage, sans couleur
  de fond passée à `render()`, afin de limiter les contours gris en mode
  `pygame.SCALED`.

## Vérification rapide

```bash
.venv/bin/python -m py_compile main.py balle.py commun.py raquette.py configuration.py
```
