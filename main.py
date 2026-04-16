import sys
import pygame
from raquette import Raquette
from balle import Balle
from commun import Cote

class Jeu:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.initialiser_configuration()

        # Création de la fenêtre de jeu. 
        self.fenetre = pygame.display.set_mode(
            (self.largeur_fenetre, self.hauteur_fenetre),
            pygame.FULLSCREEN | pygame.SCALED,
        )
        pygame.display.set_caption(self.titre_fenetre)

        self.creer_objets()

    def initialiser_configuration(self):
        """Initialise les configurations principales du jeu.
        """
        # Look rétro tout en visant un format d’écran moderne : 854x480 
        # Résolution la plus courante pour des jeux 2D modernes : 1280x720
        self.largeur_fenetre = 800
        self.hauteur_fenetre = 600

        self.titre_fenetre = "Pong Devastator solo"
        self.couleur_fond = (0, 60, 0)
        self.couleur_raquette = (255, 255, 255)
        self.couleur_balle = (255, 255, 255)
        self.couleur_texte = (255, 255, 255)
        self.fps = 60
        self.epaisseur_ligne_centrale = 2
        self.hauteur_pointille = 18
        self.espace_pointille = 14
        self.score_joueur = 0
        self.score_ordinateur = 0        
        self.horloge = pygame.time.Clock()
        self.en_cours = True
        self.police_score = pygame.font.SysFont(None, 72)
        self.police_message = pygame.font.SysFont(None, 24)
        self.score_gagnant = 3
        self.gagnant = None
        self.vitesse_balle_initiale = 5
        self.vitesse_balle_maximale = 10
        self.increment_vitesse_balle = 0.2

    def creer_objets(self):
        """Création des objets du jeu."""

        self.raquette_joueur = Raquette(
            50,
            self.hauteur_fenetre // 2 - 50,
            10,
            100,
            self.couleur_raquette,
            5,
            self.hauteur_fenetre,
        )
        self.raquette_ordinateur = Raquette(
            self.largeur_fenetre - 60,
            self.hauteur_fenetre // 2 - 50,
            10,
            100,
            self.couleur_raquette,
            4,
            self.hauteur_fenetre,
        )
        self.balle = Balle(
            self.largeur_fenetre // 2,
            self.hauteur_fenetre // 2,
            10,
            self.couleur_balle,
            self.vitesse_balle_initiale,
            self.vitesse_balle_initiale,
            self.increment_vitesse_balle,
            self.vitesse_balle_maximale,
            self.largeur_fenetre,
            self.hauteur_fenetre,
        )

        self.balle.reinitialiser_position(Cote.GAUCHE)

    def gerer_evenements(self):
        """Gestion des événements utilisateur"""

        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                self.en_cours = False

            elif evenement.type == pygame.KEYDOWN:
                if evenement.key == pygame.K_ESCAPE:
                    self.en_cours = False
                elif evenement.key == pygame.K_SPACE:
                    if self.gagnant is not None:
                        self.reinitialiser_partie()
                    elif self.balle.en_attente_mise_au_jeu:
                        self.balle.lancer_mise_au_jeu()

    def mettre_a_jour(self):
        """Mise à jour de l'état du jeu"""

        # On ne met pas à jour si on a un gagnant
        if self.gagnant is not None:
            return

        direction_joueur = 0
        touches = pygame.key.get_pressed()

        if touches[pygame.K_UP] and not touches[pygame.K_DOWN]:
            direction_joueur = -1
        elif touches[pygame.K_DOWN] and not touches[pygame.K_UP]:
            direction_joueur = 1

        self.raquette_joueur.deplacer(direction_joueur)
        self.mettre_a_jour_ia_ordinateur()
        
        sortie_ecran = self.balle.deplacer()

        # Si la balle n'est pas sortie de l'écran, on gère les collisions. Sinon, on met
        # à jour le score et on remet la balle en jeu si pas de gagnant. 
        if sortie_ecran is None:
            self.gerer_collisions()
        else:
            if sortie_ecran == Cote.GAUCHE:
                self.score_ordinateur += 1
                if self.score_ordinateur >= self.score_gagnant:
                    self.gagnant = Cote.DROITE
            elif sortie_ecran == Cote.DROITE:
                self.score_joueur += 1
                if self.score_joueur >= self.score_gagnant:
                    self.gagnant = Cote.GAUCHE
            
            if self.gagnant is None:
                self.balle.reinitialiser_position(sortie_ecran)

    def gerer_collisions(self):
        """Gère l'ensemble des collisions."""   
        
        if self.balle.rect.colliderect(self.raquette_joueur.rect):
            self.balle.rebondir_sur_raquette(self.raquette_joueur)

        if self.balle.rect.colliderect(self.raquette_ordinateur.rect):
            self.balle.rebondir_sur_raquette(self.raquette_ordinateur)

    def mettre_a_jour_ia_ordinateur(self):
        """Déplace simplement la raquette ordinateur vers la balle."""
        
        direction_ordinateur = 0
        marge = 8
        centre_cible = self.hauteur_fenetre // 2

        # Si la balle se dirige vers l'ordinateur, on la suit.
        if self.balle.vitesse_x > 0:
            if self.balle.y < self.raquette_ordinateur.rect.centery - marge:
                direction_ordinateur = -1
            elif self.balle.y > self.raquette_ordinateur.rect.centery + marge:
                direction_ordinateur = 1

        # Sinon, on revient doucement vers le centre pour se replacer.
        else:
            if self.raquette_ordinateur.rect.centery < centre_cible - marge:
                direction_ordinateur = 1
            elif self.raquette_ordinateur.rect.centery > centre_cible + marge:
                direction_ordinateur = -1

        self.raquette_ordinateur.deplacer(direction_ordinateur)

    def dessiner(self):
        """Dessin des éléments du jeu"""

        self.dessiner_terrain()
        self.raquette_joueur.dessiner(self.fenetre)
        self.raquette_ordinateur.dessiner(self.fenetre)
        self.balle.dessiner(self.fenetre)
        self.dessiner_score()
        self.dessiner_messages()

        pygame.display.flip()

    def dessiner_terrain(self):
        """Dessine le terrain de jeu"""

        self.fenetre.fill(self.couleur_fond)

        # Dessin de la ligne centrale en pointillés
        for y in range(
            0,
            self.hauteur_fenetre,
            self.hauteur_pointille + self.espace_pointille
        ):
            pygame.draw.line(
                self.fenetre,
                self.couleur_texte,
                (self.largeur_fenetre // 2, y),
                (self.largeur_fenetre // 2, y + self.hauteur_pointille),
                self.epaisseur_ligne_centrale,
            )

    def dessiner_score(self):
        """Dessine le score des joueurs"""

        texte_score_joueur = self.police_score.render(
            str(self.score_joueur), True, self.couleur_texte
        )
        texte_score_ordinateur = self.police_score.render(
            str(self.score_ordinateur), True, self.couleur_texte
        )

        self.fenetre.blit(
            texte_score_joueur,
            (self.largeur_fenetre // 2 - 80, 30),
        )
        self.fenetre.blit(
            texte_score_ordinateur,
            (self.largeur_fenetre // 2 + 50, 30),
        )        

    def dessiner_messages(self):
        """Dessine les messages aux différents moments du jeu."""

        # Si en attente de mise au jeu, on affiche un message en bas au centre pour
        # inviter à appuyer sur ESPACE et démarrer l'échange. 
        if self.balle.en_attente_mise_au_jeu:
            texte_mise_au_jeu = self.police_message.render(
                "Appuyez sur ESPACE pour mettre la balle au jeu",
                True,
                self.couleur_texte,
                self.couleur_fond,
            )
            self.fenetre.blit(
                texte_mise_au_jeu, 
                texte_mise_au_jeu.get_rect(
                    center=(self.largeur_fenetre // 2, self.hauteur_fenetre - 40)
                ),
            )

            marge_sens_mise_au_jeu = 12

            if self.balle.cote_mise_au_jeu == Cote.GAUCHE:
                texte_sens_mise_au_jeu = self.police_message.render(
                    "<<<",
                    True,
                    self.couleur_texte,
                    self.couleur_fond,
                )
                rect_sens_mise_au_jeu = texte_sens_mise_au_jeu.get_rect(
                    centery=int(self.balle.y)
                )
                rect_sens_mise_au_jeu.right = (
                    int(self.balle.x) - self.balle.rayon - marge_sens_mise_au_jeu
                )
            else:
                texte_sens_mise_au_jeu = self.police_message.render(
                    ">>>",
                    True,
                    self.couleur_texte,
                    self.couleur_fond,
                )
                rect_sens_mise_au_jeu = texte_sens_mise_au_jeu.get_rect(
                    centery=int(self.balle.y)
                )
                rect_sens_mise_au_jeu.left = (
                    int(self.balle.x) + self.balle.rayon + marge_sens_mise_au_jeu
                )

            self.fenetre.blit(texte_sens_mise_au_jeu, rect_sens_mise_au_jeu)

        if self.gagnant is not None:
            texte_gagnant = self.police_score.render(
                "Joueur gagne!" if self.gagnant == Cote.GAUCHE else "Ordinateur gagne!",
                True,
                self.couleur_texte,
                self.couleur_fond,
            )
            self.fenetre.blit(
                texte_gagnant,
                texte_gagnant.get_rect(
                    center=(self.largeur_fenetre // 2, 
                            self.hauteur_fenetre // 2)
                    ),
            )

    def reinitialiser_partie(self):
        """Redémarre une nouvelle partie."""

        self.score_joueur = 0
        self.score_ordinateur = 0
        self.gagnant = None
        self.balle.reinitialiser_position(Cote.GAUCHE)

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
