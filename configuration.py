from dataclasses import dataclass


@dataclass
class ConfigurationJeu:
    """Regroupe les paramètres principaux du jeu."""

    # Look rétro tout en visant un format d’écran moderne : 854x480 
    # Résolution la plus courante pour des jeux 2D modernes : 1280x720
    largeur_fenetre: int = 1280
    hauteur_fenetre: int = 720
    titre_fenetre: str = "Pong Devastator solo"

    couleur_fond: tuple[int, int, int] = (167, 180, 255)
    couleur_raquette: tuple[int, int, int] = (255, 255, 255)
    couleur_balle: tuple[int, int, int] = (255, 255, 255)
    couleur_texte: tuple[int, int, int] = (255, 255, 255)

    fps: int = 60

    epaisseur_ligne_centrale: int = 5
    hauteur_pointille: int = 18
    espace_pointille: int = 14

    score_gagnant: int = 3

    vitesse_balle_initiale: float = 7.0
    vitesse_balle_maximale: float = 12.0
    increment_vitesse_balle: float = 0.35

    marge_ia: int = 10
    erreur_ia_maximale: int = 35