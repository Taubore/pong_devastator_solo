import sys
import pygame
import random

# Constantes de la fenêtre
LARGEUR_FENETRE = 800
HAUTEUR_FENETRE = 600
VITESSE_RAQUETTE = 6
VITESSE_BALLE_INITIALE_X = 5
VITESSE_BALLE_INITIALE_Y = 5
COULEUR_FOND = (0, 0, 0)
COULEUR_RAQUETTE = (255, 255, 255)
COULEUR_BALLE = (255, 255, 255)
COULEUR_TEXTE = (255, 255, 255)
COULEUR_LIGNE_CENTRALE = (255, 255, 255)
TAILLE_TEXTE_SCORE = 64
TAILLE_TEXTE_INFO = 24
HAUTEUR_POINTILLE = 18
ESPACE_POINTILLE = 14
EPAISSEUR_LIGNE_CENTRALE = 2
TITRE_FENETRE = "pong_devastator_solo"
POSITION_SCORE_JOUEUR = (LARGEUR_FENETRE // 4, 30)
POSITION_SCORE_ORDINATEUR = (LARGEUR_FENETRE * 3 // 4, 30)
MARGE_IA = 15   # Permet de créer une zone morte pour l'IA afin d'éviter qu'elle ne 
                # suive la balle de manière trop parfaite
ERREUR_IA = 70


# Initialisation de Pygame
pygame.init()

# Initialisation du module audio
pygame.mixer.init()

# Création de la fenêtre
fenetre = pygame.display.set_mode((LARGEUR_FENETRE, HAUTEUR_FENETRE))
pygame.display.set_caption(TITRE_FENETRE)

# Horloge pour limiter le nombre d'images par seconde
horloge = pygame.time.Clock()

# Police pour afficher le texte
police_score = pygame.font.Font(None, TAILLE_TEXTE_SCORE)
police_info = pygame.font.Font(None, TAILLE_TEXTE_INFO)

# Chargement des sons
son_rebond_raquette = pygame.mixer.Sound("rebond_raquette.wav")
son_rebond_mur = pygame.mixer.Sound("rebond_mur.wav")
son_perdu = pygame.mixer.Sound("perdu.wav")

# Raquette du joueur
raquette_joueur = pygame.Rect(50, 280, 10, 100)

# Raquette de droite (adversaire)
raquette_ordinateur = pygame.Rect(LARGEUR_FENETRE - 60, 280, 10, 100)

# Balle
balle_x = LARGEUR_FENETRE // 2
balle_y = HAUTEUR_FENETRE // 2
vitesse_balle_x = 0
vitesse_balle_y = 0
rayon_balle = 10

# Scores
score_joueur = 0
score_ordinateur = 0
balle_en_mouvement = False

# Gestion IA
erreur_ia = 0  # Permet de faire des erreurs à l'IA pour rendre le jeu plus équilibré

# Variable de contrôle de la boucle principale
en_cours = True

while en_cours:
    # --- Gestion des événements ---
    
    for evenement in pygame.event.get():
        if evenement.type == pygame.QUIT:
            en_cours = False
        elif evenement.type == pygame.KEYDOWN:
            if evenement.key == pygame.K_ESCAPE:
                en_cours = False

            # Action "one-shot" : lancer la balle sur un appui (pas en continu)
            if evenement.key == pygame.K_SPACE and not balle_en_mouvement:
                balle_en_mouvement = True
                vitesse_balle_x = -VITESSE_BALLE_INITIALE_X
                vitesse_balle_y = VITESSE_BALLE_INITIALE_Y

    # --- Lecture du clavier ---
    
    ancien_y_raquette_joueur = raquette_joueur.y
    ancien_y_raquette_ordinateur = raquette_ordinateur.y

    touches = pygame.key.get_pressed()
    
    if touches[pygame.K_UP]:
        raquette_joueur.y -= VITESSE_RAQUETTE
    
    if touches[pygame.K_DOWN]:
        raquette_joueur.y += VITESSE_RAQUETTE

    # --- Logique du jeu ---
    
    # IA très simple
    balle_y_erreur = balle_y + erreur_ia
    if balle_y_erreur < raquette_ordinateur.centery - MARGE_IA:
        raquette_ordinateur.y -= VITESSE_RAQUETTE
    elif balle_y_erreur > raquette_ordinateur.centery + MARGE_IA:
        raquette_ordinateur.y += VITESSE_RAQUETTE
            
    # Recalage des raquettes pour éviter qu'elles ne sortent de l'écran
    if raquette_joueur.top < 0:
        raquette_joueur.top = 0
    if raquette_joueur.bottom > HAUTEUR_FENETRE:
        raquette_joueur.bottom = HAUTEUR_FENETRE

    if raquette_ordinateur.top < 0:
        raquette_ordinateur.top = 0
    if raquette_ordinateur.bottom > HAUTEUR_FENETRE:
        raquette_ordinateur.bottom = HAUTEUR_FENETRE

    # --- Déplacement de la balle ---
    
    if balle_en_mouvement:
        balle_x += vitesse_balle_x
        balle_y += vitesse_balle_y

    # --- Collisions ---

    # Balle avec les murs
    if balle_y - rayon_balle <= 0:
        vitesse_balle_y = -vitesse_balle_y
        balle_y = rayon_balle  # recalage pour éviter une sortie d'écran
        son_rebond_mur.play()
    
    if balle_y + rayon_balle >= HAUTEUR_FENETRE:
        vitesse_balle_y = -vitesse_balle_y
        balle_y = HAUTEUR_FENETRE - rayon_balle  # recalage
        son_rebond_mur.play()

    # Rectangle de la balle pour les collisions
    rect_balle = pygame.Rect(
        balle_x - rayon_balle,
        balle_y - rayon_balle,
        rayon_balle * 2,
        rayon_balle * 2,
    )   

    # Balle avec la raquette gauche (joueur)
    if rect_balle.colliderect(raquette_joueur) and vitesse_balle_x < 0:
        son_rebond_raquette.play()

        vitesse_balle_x = -vitesse_balle_x
        balle_x = raquette_joueur.right + rayon_balle  # recalage

        centre_raquette = raquette_joueur.centery
        ecart_centre = balle_y - centre_raquette
        mouvement_raquette = raquette_joueur.y - ancien_y_raquette_joueur

        vitesse_balle_y = ecart_centre // 10 + mouvement_raquette
        vitesse_balle_y = max(-8, min(8, vitesse_balle_y))

    # Balle avec la raquette droite (ordinateur)
    if rect_balle.colliderect(raquette_ordinateur) and vitesse_balle_x > 0:
        son_rebond_raquette.play()

        vitesse_balle_x = -vitesse_balle_x
        balle_x = raquette_ordinateur.left - rayon_balle
        mouvement_raquette = raquette_ordinateur.y - ancien_y_raquette_ordinateur

        centre_raquette = raquette_ordinateur.centery
        ecart_centre = balle_y - centre_raquette
        vitesse_balle_y = ecart_centre // 10 + mouvement_raquette
        vitesse_balle_y = max(-8, min(8, vitesse_balle_y))

        # Génération d'une erreur aléatoire pour l'IA à chaque contact avec la balle
        erreur_ia = random.randint(ERREUR_IA * -1, ERREUR_IA)


    # Balle perdue (côté gauche) : point pour l'ordinateur, remise au centre
    if balle_x + rayon_balle < 0:
        son_perdu.play()
        score_ordinateur += 1
        balle_en_mouvement = False
        balle_x = LARGEUR_FENETRE // 2
        balle_y = HAUTEUR_FENETRE // 2
        vitesse_balle_x = 0
        vitesse_balle_y = 0

    # Balle perdue (côté droit) : point pour le joueur, remise au centre
    if balle_x - rayon_balle > LARGEUR_FENETRE:
        son_perdu.play()
        score_joueur += 1
        balle_en_mouvement = False
        balle_x = LARGEUR_FENETRE // 2
        balle_y = HAUTEUR_FENETRE // 2
        vitesse_balle_x = 0
        vitesse_balle_y = 0

    # --- Dessin ---

    fenetre.fill(COULEUR_FOND)
    for y in range(0, HAUTEUR_FENETRE, HAUTEUR_POINTILLE + ESPACE_POINTILLE):
        pygame.draw.line(
            fenetre,
            COULEUR_LIGNE_CENTRALE,
            (LARGEUR_FENETRE // 2, y),
            (LARGEUR_FENETRE // 2, y + HAUTEUR_POINTILLE),
            EPAISSEUR_LIGNE_CENTRALE,
        )

    pygame.draw.rect(fenetre, COULEUR_RAQUETTE, raquette_joueur, border_radius=4)
    pygame.draw.rect(fenetre, COULEUR_RAQUETTE, raquette_ordinateur, border_radius=4)
    pygame.draw.circle(fenetre, COULEUR_BALLE, (balle_x, balle_y), rayon_balle)

    # Affichage du score
    texte_score_joueur = police_score.render(
        str(score_joueur),
        True,
        COULEUR_TEXTE,
    )
    rectangle_score_joueur = texte_score_joueur.get_rect(
        center=POSITION_SCORE_JOUEUR)
    fenetre.blit(texte_score_joueur, rectangle_score_joueur)
    pygame.draw.rect(
        fenetre, 
        COULEUR_TEXTE, 
        rectangle_score_joueur.inflate(80, 5),
        width=2,
        border_radius=5,
    )

    texte_score_ordinateur = police_score.render(
        str(score_ordinateur),
        True,
        COULEUR_TEXTE,
    )
    rectangle_score_ordinateur = texte_score_ordinateur.get_rect(
        center=POSITION_SCORE_ORDINATEUR)
    fenetre.blit(texte_score_ordinateur, rectangle_score_ordinateur)
    pygame.draw.rect(
        fenetre, 
        COULEUR_TEXTE, 
        rectangle_score_ordinateur.inflate(80, 5),
        width=2,
        border_radius=5,
    )

    # Si balle pas en mouvement affichage d'un message d'instruction
    if not balle_en_mouvement:
        texte_info = police_info.render(
            "Appuyez sur ESPACE pour lancer la balle",
            True,
            COULEUR_TEXTE,
        )
        rectangle_info = texte_info.get_rect(
            center=(LARGEUR_FENETRE // 2, HAUTEUR_FENETRE - TAILLE_TEXTE_INFO))
        fenetre.blit(texte_info, rectangle_info)

    # --- Affichage ---

    pygame.display.flip()  # Met à jour l'affichage de la fenêtre
    horloge.tick(60)  # Limite la boucle à 60 images par seconde

# Fermeture de Pygame et sortie du programme
pygame.quit()
sys.exit()
