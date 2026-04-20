import logging
import pygame
import random
from commun import Cote

logger = logging.getLogger(__name__)


class Balle:
    """Représente la balle du jeu."""

    def __init__(self,
                 x,
                 y,
                 rayon,
                 couleur,
                 vitesse_x,
                 vitesse_y,
                 increment_vitesse_balle,
                 vitesse_x_maximale,
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
        self.vitesse_x = vitesse_x
        self.vitesse_y = vitesse_y
        self.vitesse_x_initiale = abs(vitesse_x)
        self.increment_vitesse_balle = increment_vitesse_balle
        self.limite_droite = largeur_fenetre
        self.limite_bas = hauteur_fenetre
        self.en_attente_mise_au_jeu = True
        self.cote_mise_au_jeu = Cote.GAUCHE
        self.sons = sons
        self.image = image
        self.facteur_angle_rebond = 12
        self.influence_mouvement_raquette = 0.5
        self.vitesse_x_maximale = vitesse_x_maximale
        self.vitesse_y_maximale = 8

    def deplacer(self):
        """Déplace la balle selon sa vitesse."""
 
        self.x += self.vitesse_x
        self.y += self.vitesse_y

        # Rebond sur les murs horizontalement invisibles du terrain : si le bord haut 
        # ou bas de la balle touche la limite, on la recale juste à l'intérieur puis on 
        # inverse sa vitesse verticale.
        if self.y - self.rayon <= 0:
            self.y = self.rayon
            self.vitesse_y = -self.vitesse_y
            self.sons["rebond_mur"].play()

        elif self.y + self.rayon >= self.limite_bas:
            self.y = self.limite_bas - self.rayon
            self.vitesse_y = -self.vitesse_y
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
        self.vitesse_x = self.vitesse_x_initiale * direction_x
        
        self.vitesse_y = 0
        while self.vitesse_y == 0:
            self.vitesse_y = random.randint(-5, 5)

        self.en_attente_mise_au_jeu = True
        self.cote_mise_au_jeu = Cote(direction_x)

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
        if self.vitesse_x < 0:
            self.x = raquette.rect.right + self.rayon
        else:
            self.x = raquette.rect.left - self.rayon

        # Augmentation de la vitesse horizontale à chaque rebond, jusqu'à une limite.
        if abs(self.vitesse_x) < self.vitesse_x_maximale:
            self.vitesse_x += self.increment_vitesse_balle * (1 if self.vitesse_x > 0 else -1)
        
        self.vitesse_x = -self.vitesse_x

        ecart_centre = self.y - raquette.rect.centery
        mouvement_raquette = (
            raquette.rect.y - raquette.pos_y_avant_deplacement
        )

        # Plus la balle touche loin du centre de la raquette, plus l'angle
        # vertical du rebond devient marqué.
        vitesse_y_selon_impact = ecart_centre / self.facteur_angle_rebond

        # Le mouvement de la raquette ajoute une petite influence contrôlée.
        vitesse_y_selon_raquette = (
            mouvement_raquette * self.influence_mouvement_raquette
        )

        self.vitesse_y = vitesse_y_selon_impact + vitesse_y_selon_raquette

        # On limite l'angle pour éviter une balle presque verticale.
        self.vitesse_y = max(
            -self.vitesse_y_maximale,
            min(self.vitesse_y_maximale, self.vitesse_y),
        )

        logger.debug(
            "Rebond sur raquette : vitesse_x=%.1f, vitesse_y=%s",
            self.vitesse_x,
            self.vitesse_y,
        )

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
