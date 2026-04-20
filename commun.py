from enum import Enum, IntEnum, auto

class Cote(IntEnum):
    GAUCHE = -1
    DROITE = 1 

class EtatJeu(Enum):
    MISE_AU_JEU = auto()
    EN_JEU = auto()
    PARTIE_TERMINEE = auto()
    EN_FERMETURE = auto()

