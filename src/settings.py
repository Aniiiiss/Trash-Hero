import pygame

pygame.init()

SW, SH = 800, 600
FPS    = 60
GRAVITY = 0.22

# Mot de passe mode développeur
DEV_PASSWORD = "trash2025"

# ─────────────────────────────────────────────────────────────
# PALETTE COULEURS — style cartoon vibrant
# ─────────────────────────────────────────────────────────────
WHITE      = (255, 255, 255)
BLACK      = (20,  20,  30)

GRAY       = (160, 160, 175)
SKY_TOP    = (65,  130, 230)
SKY_BOT    = (175, 225, 255)
GRASS_A    = (88,  196, 72)
GRASS_B    = (78,  180, 62)
RED        = (235, 60,  65)
RED_LT     = (255, 130, 135)
YELLOW     = (255, 235, 55)
YELLOW_LT  = (255, 248, 160)
ORANGE     = (255, 155, 40)
PURPLE     = (160, 80,  225)
TEAL       = (50,  210, 195)
PINK       = (255, 135, 185)
SUN_COL    = (255, 240, 100)
SUN_RAY    = (255, 220, 50)

# Types de déchets
TRASH_C  = {'papier':(75,130,230), 'verre':(60,200,120),
             'plastique':(255,215,55), 'organique':(190,120,55)}
TRASH_LT = {'papier':(155,195,255), 'verre':(145,245,185),
             'plastique':(255,248,165), 'organique':(235,178,118)}
TRASH_DK = {'papier':(40,80,165),  'verre':(30,140,75),
             'plastique':(200,160,15), 'organique':(130,75,25)}
TRASH_LB = {'papier':'Papier','verre':'Verre',
             'plastique':'Plastique','organique':'Bio'}

BIN_F  = {'papier':(65,110,215),'verre':(50,160,90),'plastique':(210,170,25),'organique':(145,88,32)}
BIN_S  = {'papier':(40,78,165), 'verre':(30,115,60),'plastique':(165,130,10),'organique':(100,58,18)}
BIN_T  = {'papier':(115,165,255),'verre':(105,230,162),'plastique':(255,248,110),'organique':(228,160,88)}

LEVELS = [
    {'name':'Niveau 1 — Tutoriel','hint':'2 types · Pas d\'obstacles',
     'types':['papier','verre'],'target':5,'speed':(1.5,2.5),'spawn':150,'obstacles':0,'time':90},
    {'name':'Niveau 2 — En Route !','hint':'3 types · 1 obstacle',
     'types':['papier','verre','plastique'],'target':8,'speed':(2.0,3.0),'spawn':120,'obstacles':1,'time':90},
    {'name':'Niveau 3 — Ça se Complique','hint':'4 types · 2 obstacles',
     'types':['papier','verre','plastique','organique'],'target':12,'speed':(2.5,3.5),'spawn':90,'obstacles':2,'time':90},
    {'name':'Niveau 4 — Déchets Furieux','hint':'4 types · 3 obstacles · Rapide !',
     'types':['papier','verre','plastique','organique'],'target':15,'speed':(3.0,4.5),'spawn':70,'obstacles':3,'time':90},
    {'name':'Niveau 5 — Avant le Boss','hint':'Mode EXPERT !',
     'types':['papier','verre','plastique','organique'],'target':20,'speed':(3.5,5.5),'spawn':55,'obstacles':4,'time':90},
]
