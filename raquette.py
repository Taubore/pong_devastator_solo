import pygame


class Raquette:
    """Représente une raquette du jeu."""

    def __init__(self,
                 x,
                 y,
                 largeur,
                 hauteur,
                 couleur,
                 vitesse,
                 hauteur_fenetre,
                 image = None
        ):
        self.rect = pygame.Rect(x, y, largeur, hauteur)
        self.couleur = couleur
        self.vitesse = vitesse
        self.limite_bas = hauteur_fenetre
        self.pos_y_avant_deplacement = self.rect.y
        self.image = image

    def deplacer(self, direction):
        """Déplace la raquette -1, 0 ou 1."""
        self.pos_y_avant_deplacement = self.rect.y
        self.rect.y += direction * self.vitesse

        # Garde la raquette entièrement visible dans la fenêtre.
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > self.limite_bas:
            self.rect.bottom = self.limite_bas

    def dessiner(self, surface):
        """Dessine la raquette dans la fenêtre."""

        if self.image is not None:
            surface.blit(self.image, self.rect)
        else:
            pygame.draw.rect(surface, self.couleur, self.rect, border_radius=4)
