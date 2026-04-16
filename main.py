import sys
import pygame
import random

class Raquette:
    """Représente une raquette du jeu."""

    def __init__(self, x, y, largeur, hauteur, couleur, vitesse, hauteur_fenetre):
        self.rect = pygame.Rect(x, y, largeur, hauteur)
        self.couleur = couleur
        self.vitesse = vitesse
        self.limite_bas = hauteur_fenetre
        self.pos_y_avant_deplacement = 0

    def deplacer(self, direction):
        """Déplace la raquette dans la direction 0, 1 ou -1 et à la vitesse définie."""
        self.pos_y_avant_deplacement = self.rect.y
        self.rect.y += direction * self.vitesse

        # Empêche la raquette de sortir de la fenêtre."""
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > self.limite_bas:
            self.rect.bottom = self.limite_bas

    def dessiner(self, surface):
        """Dessine la raquette dans la fenêtre."""
        pygame.draw.rect(surface, self.couleur, self.rect, border_radius=4)


class Balle:
    """Représente la balle du jeu."""

    def __init__(self, x, y, rayon, couleur, vitesse_x,
                 vitesse_y, largeur_fenetre, hauteur_fenetre):
        self.x = x
        self.y = y
        self.rayon = rayon
        self.couleur = couleur
        self.vitesse_x = vitesse_x
        self.vitesse_y = vitesse_y
        self.limite_droite = largeur_fenetre
        self.limite_bas = hauteur_fenetre
        self.son_rebond_raquette = pygame.mixer.Sound("rebond_raquette.wav")
        self.son_rebond_mur = pygame.mixer.Sound("rebond_mur.wav")
        self.son_perdue = pygame.mixer.Sound("perdue.wav")

    def deplacer(self):
        """Déplace la balle selon sa vitesse."""
        self.x += self.vitesse_x
        self.y += self.vitesse_y

        # Rebond sur les murs haut et bas"""
        if self.y - self.rayon <= 0:
            self.y = self.rayon
            self.vitesse_y = -self.vitesse_y
            self.son_rebond_mur.play()

        elif self.y + self.rayon >= self.limite_bas:
            self.y = self.limite_bas - self.rayon
            self.vitesse_y = -self.vitesse_y
            self.son_rebond_mur.play()

        if self.x + self.rayon < 0:
            self.son_perdue.play()
        elif self.x - self.rayon > self.limite_droite:
            self.son_perdue.play()


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
        self.son_rebond_raquette.play()
        self.vitesse_x = -self.vitesse_x

        self.x = raquette.rect.right + self.rayon  # recalage

        ecart_centre = self.y - raquette.rect.centery
        mouvement_raquette = raquette.rect.y - raquette.pos_y_avant_deplacement

        self.vitesse_y = ecart_centre // 10 + mouvement_raquette
        self.vitesse_y = max(-8, min(8, self.vitesse_y))


    def dessiner(self, surface):
        """Dessine la balle dans la fenêtre."""
        pygame.draw.circle(surface, self.couleur, (self.x, self.y), self.rayon)


class Jeu:
    def __init__(self):
        """Initialisation du jeu et de Pygame"""

        pygame.init()
        pygame.mixer.init()

        # Valeur de configuration principales du jeu 
        # Look rétro tout en visant un format d’écran moderne : 854x480 
        # Résolution la plus courante pour des jeux 2D modernes : 1280x720
        self.largeur_fenetre = 800
        self.hauteur_fenetre = 600
        self.titre_fenetre = "Pong Devastator solo"
        self.couleur_fond = (0, 60, 0)
        self.couleur_raquette = (255, 255, 255)
        self.couleur_balle = (255, 255, 255)
        self.couleur_ligne_centrale = (255, 255, 255)
        self.epaisseur_ligne_centrale = 2
        self.hauteur_pointille = 18
        self.espace_pointille = 14
        self.fps = 60

        # Création de la fenetre
        self.fenetre = pygame.display.set_mode(
            (self.largeur_fenetre, self.hauteur_fenetre),
 #           pygame.FULLSCREEN | pygame.SCALED,
        )
        pygame.display.set_caption(self.titre_fenetre)

        # Horloge pour limiter la boucle principale
        self.horloge = pygame.time.Clock()

        # État principal de la boucle de jeu
        self.en_cours = True

        self.creer_objets()

    def creer_objets(self):
        """Création des objets du jeu (raquettes, balle, etc.)"""

        self.raquette_joueur = Raquette(
            50,
            280,
            10,
            100,
            self.couleur_raquette,
            5,
            self.hauteur_fenetre,
        )
        self.raquette_ordinateur = Raquette(
            self.largeur_fenetre - 60,
            280,
            10,
            100,
            self.couleur_raquette,
            0,
            self.hauteur_fenetre,
        )
        self.balle = Balle(
            self.largeur_fenetre // 2,
            self.hauteur_fenetre // 2,
            10,
            self.couleur_balle,
            -5,
            5,
            self.largeur_fenetre,
            self.hauteur_fenetre,
        )

    def gerer_evenements(self):
        """Gestion des événements utilisateur"""

        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                self.en_cours = False

            elif evenement.type == pygame.KEYDOWN:
                if evenement.key == pygame.K_ESCAPE:
                    self.en_cours = False

    def mettre_a_jour(self):
        """Mise à jour de l'état du jeu"""

        direction_joueur = 0

        touches= pygame.key.get_pressed()

        if touches[pygame.K_UP]:
            direction_joueur = -1
        
        if touches[pygame.K_DOWN]:
            direction_joueur = 1

        self.raquette_joueur.deplacer(direction_joueur)
        self.balle.deplacer()

        # Vérifier les collisions avec les raquettes
        if self.balle.rect.colliderect(self.raquette_joueur.rect):
            self.balle.rebondir_sur_raquette(self.raquette_joueur)

        if self.balle.rect.colliderect(self.raquette_ordinateur.rect):
            self.balle.rebondir_sur_raquette(self.raquette_ordinateur)

    def dessiner(self):
        """Dessin des éléments du jeu"""

        self.fenetre.fill(self.couleur_fond)

        # Dessin de la ligne centrale en pointillés
        for y in range(
            0,
            self.hauteur_fenetre,
            self.hauteur_pointille + self.espace_pointille
        ):
            pygame.draw.line(
                self.fenetre,
                self.couleur_ligne_centrale,
                (self.largeur_fenetre // 2, y),
                (self.largeur_fenetre // 2, y + self.hauteur_pointille),
                self.epaisseur_ligne_centrale,
            )

        self.raquette_joueur.dessiner(self.fenetre)
        self.raquette_ordinateur.dessiner(self.fenetre)
        self.balle.dessiner(self.fenetre)

        pygame.display.flip()

    def executer(self):
        """Boucle principale du jeu"""

        while self.en_cours:
            self.gerer_evenements()
            self.mettre_a_jour()
            self.dessiner()
            self.horloge.tick(self.fps)

        self.fermer()

    def fermer(self):
        """Fermeture propre de Pygame"""

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    jeu = Jeu()
    jeu.executer()