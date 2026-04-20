import logging
import sys
import pygame
import random
from raquette import Raquette
from balle import Balle
from commun import Cote, EtatJeu
from configuration import ConfigurationJeu

class Jeu:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        logging.basicConfig(level=logging.INFO)

        self.configuration = ConfigurationJeu()
        self.initialiser_configuration()
        self.initialiser_etat_partie()

        # Création de la fenêtre de jeu. 
        self.fenetre = pygame.display.set_mode(
            (self.largeur_fenetre, self.hauteur_fenetre),
            pygame.FULLSCREEN | pygame.SCALED,
        )
        pygame.display.set_caption(self.titre_fenetre)

        # On cache le curseur de la souris
        pygame.mouse.set_visible(False)

        self.charger_sons()
        self.charger_images()
        self.creer_objets()

    def initialiser_configuration(self):
        """Initialise les configurations principales du jeu.
        """
        self.largeur_fenetre = self.configuration.largeur_fenetre
        self.hauteur_fenetre = self.configuration.hauteur_fenetre
        self.titre_fenetre = self.configuration.titre_fenetre
        
        self.couleur_fond = self.configuration.couleur_fond
        self.couleur_raquette = self.configuration.couleur_raquette
        self.couleur_balle = self.configuration.couleur_balle
        self.couleur_texte = self.configuration.couleur_texte
        
        self.fps = self.configuration.fps
        
        self.epaisseur_ligne_centrale = self.configuration.epaisseur_ligne_centrale
        self.hauteur_pointille = self.configuration.hauteur_pointille
        self.espace_pointille = self.configuration.espace_pointille
        
        self.score_gagnant = self.configuration.score_gagnant
        self.vitesse_balle_initiale = self.configuration.vitesse_balle_initiale
        self.vitesse_balle_maximale = self.configuration.vitesse_balle_maximale
        self.increment_vitesse_balle = self.configuration.increment_vitesse_balle

        self.marge_ia = self.configuration.marge_ia
        self.erreur_ia_maximale = self.configuration.erreur_ia_maximale

        self.horloge = pygame.time.Clock()
        self.police_score = pygame.font.SysFont("dejavusansmono", 72, bold=True)
        self.police_message = pygame.font.SysFont("dejavusansmono", 26, bold=True)
        self.anticrenelage_texte = True


    def initialiser_etat_partie(self):
        """Initialise l'état courant de la partie."""

        self.score_joueur = 0
        self.score_ordinateur = 0
        self.gagnant = None
        self.erreur_ia = 0
        self.etat_jeu = EtatJeu.ECRAN_TITRE

    def reinitialiser_partie(self):
        """Redémarre une nouvelle partie."""

        self.initialiser_etat_partie()
        self.etat_jeu = EtatJeu.MISE_AU_JEU
        self.balle.reinitialiser_position(Cote.GAUCHE)

    def charger_sons(self):
        """Charge les sons utilisés par le jeu."""

        self.sons_balle = {
            "rebond_raquette": pygame.mixer.Sound("assets/sons/rebond_raquette.wav"),
            "rebond_mur": pygame.mixer.Sound("assets/sons/rebond_mur.wav"),
            "perdue": pygame.mixer.Sound("assets/sons/perdue.wav"),
        }

    def charger_images(self):
        """Charge les images utilisées par le jeu."""
        self.images = {
            "balle": pygame.image.load("assets/images/balle.png").convert_alpha(),
            "raquette_gauche": pygame.image.load("assets/images/raquette1.png").convert_alpha(),
            "raquette_droite": pygame.image.load("assets/images/raquette2.png").convert_alpha(),
        }

    def creer_objets(self):
        """Création des objets du jeu."""

        self.raquette_joueur = Raquette(
            50,
            self.hauteur_fenetre // 2 - 50,
            20,
            140,
            self.couleur_raquette,
            5,
            self.hauteur_fenetre,
            self.images["raquette_gauche"],
        )
        self.raquette_ordinateur = Raquette(
            self.largeur_fenetre - 60,
            self.hauteur_fenetre // 2 - 50,
            20,
            140,
            self.couleur_raquette,
            4,
            self.hauteur_fenetre,
            self.images["raquette_droite"],
        )
        self.balle = Balle(
            self.largeur_fenetre // 2,
            self.hauteur_fenetre // 2,
            16,
            self.couleur_balle,
            self.vitesse_balle_initiale,
            self.increment_vitesse_balle,
            self.vitesse_balle_maximale,
            self.largeur_fenetre,
            self.hauteur_fenetre,
            self.sons_balle,
            self.images["balle"],
        )

        self.balle.reinitialiser_position(Cote.GAUCHE)

    def gerer_collisions(self):
        """Gère l'ensemble des collisions."""   
        
        if (self.balle.direction_x < 0
            and self.balle.rect.colliderect(self.raquette_joueur.rect)
        ):
            self.balle.rebondir_sur_raquette(self.raquette_joueur)

        if (self.balle.direction_x > 0
            and self.balle.rect.colliderect(self.raquette_ordinateur.rect)
        ):
            self.balle.rebondir_sur_raquette(self.raquette_ordinateur)

    def mettre_a_jour_ia_ordinateur(self):
        """Déplace simplement la raquette ordinateur vers la balle."""
        
        direction_ordinateur = 0
        marge = self.marge_ia
        centre_cible = self.hauteur_fenetre // 2
        y_cible = self.balle.y + self.erreur_ia

        # Si la balle se dirige vers l'ordinateur, on la suit.
        if self.balle.direction_x > 0:
            if y_cible < self.raquette_ordinateur.rect.centery - marge:
                direction_ordinateur = -1
            elif y_cible > self.raquette_ordinateur.rect.centery + marge:
                direction_ordinateur = 1

        # Sinon, on revient doucement vers le centre pour se replacer.
        else:
            if self.raquette_ordinateur.rect.centery < centre_cible - marge:
                direction_ordinateur = 1
            elif self.raquette_ordinateur.rect.centery > centre_cible + marge:
                direction_ordinateur = -1

        self.raquette_ordinateur.deplacer(direction_ordinateur)

    def dessiner_terrain(self):
        """Dessine le terrain de jeu"""

        self.fenetre.fill(self.couleur_fond)

        # Dessin de la ligne centrale en pointillés lorsque le jeu est en jeu ou en 
        # mise en service.
        if self.etat_jeu == EtatJeu.EN_JEU or self.etat_jeu == EtatJeu.MISE_AU_JEU:
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

    def dessiner_ecran_titre(self):
        """Dessine l'écran titre du jeu."""

        self.fenetre.fill(self.couleur_fond)

        texte_titre = self.police_score.render(
            self.titre_fenetre,
            self.anticrenelage_texte,
            self.couleur_texte,
        )
        texte_instructions = self.police_message.render(
            "Flèches HAUT/BAS pour déplacer la raquette\n" \
            "ESC pour quitter\n" \
            "ESPACE pour commencer\n",
            self.anticrenelage_texte,
            self.couleur_texte,
        )

        self.fenetre.blit(
            texte_titre,
            texte_titre.get_rect(
                center=(self.largeur_fenetre // 2, self.hauteur_fenetre // 2 - 100)
            ),
        )
        self.fenetre.blit(
            texte_instructions,
            texte_instructions.get_rect(
                center=(self.largeur_fenetre // 2, self.hauteur_fenetre // 2)
            ),
        )

    def dessiner_score(self):
        """Dessine le score des joueurs"""

        texte_score_joueur = self.police_score.render(
            str(self.score_joueur), self.anticrenelage_texte, self.couleur_texte
        )
        texte_score_ordinateur = self.police_score.render(
            str(self.score_ordinateur), self.anticrenelage_texte, self.couleur_texte
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
        if self.etat_jeu == EtatJeu.MISE_AU_JEU:
            texte_mise_au_jeu = self.police_message.render(
                "Appuyez sur ESPACE pour mettre la balle au jeu",
                self.anticrenelage_texte,
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
                    self.anticrenelage_texte,
                    self.couleur_texte,
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
                    self.anticrenelage_texte,
                    self.couleur_texte,
                )
                rect_sens_mise_au_jeu = texte_sens_mise_au_jeu.get_rect(
                    centery=int(self.balle.y)
                )
                rect_sens_mise_au_jeu.left = (
                    int(self.balle.x) + self.balle.rayon + marge_sens_mise_au_jeu
                )

            self.fenetre.blit(texte_sens_mise_au_jeu, rect_sens_mise_au_jeu)

        if self.etat_jeu == EtatJeu.PARTIE_TERMINEE:
            message_gagnant = (
                "Joueur gagne!"
                if self.gagnant == Cote.GAUCHE
                else "Ordinateur gagne!"
            )

            texte_gagnant = self.police_score.render(
                message_gagnant,
                True,
                self.couleur_texte,
                self.couleur_fond,
            )

            texte_rejouer = self.police_message.render(
                "ESPACE : rejouer    ESC : quitter",
                True,
                self.couleur_texte,
                self.couleur_fond,
            )

            self.fenetre.blit(
                texte_gagnant,
                texte_gagnant.get_rect(
                    center=(
                        self.largeur_fenetre // 2,
                        self.hauteur_fenetre // 2 - 50,
                    )
                ),
            )

            self.fenetre.blit(
                texte_rejouer,
                texte_rejouer.get_rect(
                    center=(
                        self.largeur_fenetre // 2,
                        self.hauteur_fenetre // 2 + 10,
                    )
                ),
            )



    def traiter_point_marque(self, sortie_ecran):
        """Met à jour le score après une sortie de la balle."""

        if sortie_ecran == Cote.GAUCHE:
            self.score_ordinateur += 1

            if self.score_ordinateur >= self.score_gagnant:
                self.gagnant = Cote.DROITE
                self.etat_jeu = EtatJeu.PARTIE_TERMINEE
                return

        elif sortie_ecran == Cote.DROITE:
            self.score_joueur += 1
            if self.score_joueur >= self.score_gagnant:
                self.gagnant = Cote.GAUCHE
                self.etat_jeu = EtatJeu.PARTIE_TERMINEE
                return
        
        # On ajoute une erreur aléatoire à l'IA pour éviter qu'elle soit imbattable, 
        # surtout à la longue.
        self.erreur_ia = random.randint(  #AJOUT
            -self.erreur_ia_maximale,
            self.erreur_ia_maximale,
        )

        self.balle.reinitialiser_position(sortie_ecran)
        self.etat_jeu = EtatJeu.MISE_AU_JEU


    def gerer_evenements(self):
        """Gestion des événements utilisateur"""

        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                self.etat_jeu = EtatJeu.EN_FERMETURE

            elif evenement.type == pygame.KEYDOWN:
                if evenement.key == pygame.K_ESCAPE:
                    self.etat_jeu = EtatJeu.EN_FERMETURE
                elif evenement.key == pygame.K_SPACE:
                    if self.etat_jeu == EtatJeu.ECRAN_TITRE:
                        self.etat_jeu = EtatJeu.MISE_AU_JEU
                    elif self.etat_jeu == EtatJeu.MISE_AU_JEU:
                        self.etat_jeu = EtatJeu.EN_JEU
                    elif self.etat_jeu == EtatJeu.PARTIE_TERMINEE:
                        self.reinitialiser_partie()

    def mettre_a_jour(self):
        """Mise à jour de l'état du jeu"""

        # On ne met pas à jour si la partie n'est pas en cours.
        #if self.etat_jeu != EtatJeu.EN_JEU:
        #    return

        direction_joueur = 0
        touches = pygame.key.get_pressed()

        if touches[pygame.K_UP] and not touches[pygame.K_DOWN]:
            direction_joueur = -1
        elif touches[pygame.K_DOWN] and not touches[pygame.K_UP]:
            direction_joueur = 1

        self.raquette_joueur.deplacer(direction_joueur)
        self.mettre_a_jour_ia_ordinateur()
        
        sortie_ecran = None
        if self.etat_jeu == EtatJeu.EN_JEU:
            sortie_ecran = self.balle.deplacer()

        # Si la balle n'est pas sortie de l'écran, on gère les collisions. Sinon, on met
        # à jour le score et on remet la balle en jeu si pas de gagnant. 
        if sortie_ecran is None:
            self.gerer_collisions()
        else:
            self.traiter_point_marque(sortie_ecran)

    def dessiner(self):
        """Dessin des éléments du jeu"""

        if self.etat_jeu == EtatJeu.ECRAN_TITRE:
            self.dessiner_ecran_titre()
        else:
            self.dessiner_terrain()
            self.raquette_joueur.dessiner(self.fenetre)
            self.raquette_ordinateur.dessiner(self.fenetre)
            self.balle.dessiner(self.fenetre)
            self.dessiner_score()
            self.dessiner_messages()

        pygame.display.flip()

    def executer(self):
        """Boucle principale du jeu"""

        while self.etat_jeu is not EtatJeu.EN_FERMETURE:
            self.gerer_evenements()
            self.mettre_a_jour()
            self.dessiner()
            self.horloge.tick(self.fps)

        self.fermer()

    def fermer(self):
        """Fermeture propre de Pygame"""
        
        pygame.mouse.set_visible(True)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    jeu = Jeu()
    jeu.executer()
