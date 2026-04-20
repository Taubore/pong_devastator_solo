import logging
import pygame
import random
import math
from commun import Cote

logger = logging.getLogger(__name__)


class Balle:
    """Représente la balle du jeu."""

    def __init__(self,
                 x,
                 y,
                 rayon,
                 couleur,
                 vitesse,
                 increment_vitesse_balle,
                 vitesse_maximale,
                 largeur_fenetre,
                 hauteur_fenetre,
                 sons,
                 image = None
        ):
        # On stocke la position en flottant pour préparer des déplacements
        # plus fins que le simple pixel par pixel.
        self.x = float(x)
        self.y = float(y)
        self.rayon = rayon
        self.couleur = couleur
        self.vitesse = abs(vitesse)
        self.vitesse_initiale = abs(vitesse)
        self.vitesse_maximale = vitesse_maximale
        self.direction_x = 1
        self.direction_y = 0
        self.increment_vitesse_balle = increment_vitesse_balle
        self.limite_droite = largeur_fenetre
        self.limite_bas = hauteur_fenetre
        self.en_attente_mise_au_jeu = True
        self.cote_mise_au_jeu = Cote.GAUCHE
        self.sons = sons
        self.image = image
        self.facteur_angle_rebond = 12
        self.influence_mouvement_raquette = 0.2

    def deplacer(self):
        """Déplace la balle selon sa vitesse."""
 
        self.x += self.direction_x * self.vitesse
        self.y += self.direction_y * self.vitesse

        # Rebond sur les murs horizontalement invisibles du terrain : si le bord haut 
        # ou bas de la balle touche la limite, on la recale juste à l'intérieur puis on 
        # inverse sa vitesse verticale.
        if self.y - self.rayon <= 0:
            self.y = self.rayon
            self.direction_y = -self.direction_y
            self.sons["rebond_mur"].play()

        elif self.y + self.rayon >= self.limite_bas:
            self.y = self.limite_bas - self.rayon
            self.direction_y = -self.direction_y
            self.sons["rebond_mur"].play()

        # Si toute la balle a quitté l'écran par un côté, on signale quel joueur a 
        # perdu l'échange. Le jeu décidera du pointage et de la remise en jeu.
        if self.x + self.rayon < 0:
            self.sons["perdue"].play()
            return Cote.GAUCHE
        elif self.x - self.rayon > self.limite_droite:
            self.sons["perdue"].play()
            return Cote.DROITE
        
        return None  # Pas de sortie d'écran

    def reinitialiser_position(self, direction_x):
        """Remet la balle au centre dans la direction précisée."""
        
        self.x = self.limite_droite // 2
        self.y = self.limite_bas // 2
       
        self.vitesse = self.vitesse_initiale
        self.direction_x = int(direction_x)
        
        self.direction_y = 0
        while self.direction_y == 0:
            self.direction_y = random.uniform(-0.8, 0.8)

        self.normaliser_direction()

        self.en_attente_mise_au_jeu = True
        self.cote_mise_au_jeu = Cote(direction_x)

    def normaliser_direction(self):
        """Ramène la direction de la balle à une longueur de 1."""

        longueur = math.hypot(self.direction_x, self.direction_y)

        # Sécurité : évite une division par zéro si la direction est invalide.
        if longueur == 0:
            self.direction_x = 1
            self.direction_y = 0
            return

        self.direction_x /= longueur
        self.direction_y /= longueur

    @property
    def rect(self):
        """Retourne un rectangle pour les collisions de la balle."""
 
        return pygame.Rect(
            self.x - self.rayon,
            self.y - self.rayon,
            self.rayon * 2,
            self.rayon * 2,
        )

    def rebondir_sur_raquette(self, raquette):
        """Fait rebondir la balle sur une raquette donnée."""
 
        self.sons["rebond_raquette"].play()

        # Recalage sur la face touchée, selon le sens d'arrivée de la balle.
        if self.direction_x < 0:
            self.x = raquette.rect.right + self.rayon
        else:
            self.x = raquette.rect.left - self.rayon

        self.accelerer()
        self.direction_x = -self.direction_x

        ecart_centre = self.y - raquette.rect.centery
        mouvement_raquette = (raquette.rect.y - raquette.pos_y_avant_deplacement)

        # Plus la balle touche loin du centre de la raquette, plus l'angle
        # vertical du rebond devient marqué.
        ecart_normalise = ecart_centre / (raquette.rect.height / 2)
        vitesse_y_selon_impact = ecart_normalise * 0.8

        # Le mouvement de la raquette ajoute une petite influence contrôlée.
        mouvement_raquette_normalise = mouvement_raquette / raquette.vitesse
        vitesse_y_selon_raquette = (
            mouvement_raquette_normalise * self.influence_mouvement_raquette
        )
        
        self.direction_y = (vitesse_y_selon_impact + vitesse_y_selon_raquette)
        self.direction_y = max(-0.9, min(0.9, self.direction_y))

        self.normaliser_direction() 

        logger.debug(
            "Rebond sur raquette : vitesse=%.1f, direction_x=%.2f, direction_y=%.2f",
            self.vitesse,
            self.direction_x,
            self.direction_y,
        )

    def accelerer(self):
        """Augmente progressivement la vitesse horizontale de la balle."""

        if self.vitesse >= self.vitesse_maximale:
            return

        self.vitesse += self.increment_vitesse_balle
        self.vitesse = min(self.vitesse, self.vitesse_maximale)

    def dessiner(self, surface):
        """Dessine la balle dans la fenêtre."""
 
        if self.image is not None:
            rect_image = self.image.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(self.image, rect_image)
        else:
            pygame.draw.circle(
                surface,
                self.couleur,
                (int(self.x), int(self.y)),
                self.rayon)
