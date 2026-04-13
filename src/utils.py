import pygame
import math
from src.settings import *

# ─────────────────────────────────────────────────────────────
# SURFACE DE FOND (pré-rendu pour la performance)
# ─────────────────────────────────────────────────────────────
_bg_surface = None

def build_bg():
    global _bg_surface
    _bg_surface = pygame.Surface((SW, SH))
    for y in range(SH - 80):
        t = y / max(SH - 81, 1)
        c = (int(SKY_TOP[0] + (SKY_BOT[0]-SKY_TOP[0])*t),
             int(SKY_TOP[1] + (SKY_BOT[1]-SKY_TOP[1])*t),
             int(SKY_TOP[2] + (SKY_BOT[2]-SKY_TOP[2])*t))
        pygame.draw.line(_bg_surface, c, (0, y), (SW, y))
    for tx in range(0, SW, 50):
        for ty in range(SH - 80, SH, 30):
            col = GRASS_A if ((tx//50 + ty//30) % 2 == 0) else GRASS_B
            pygame.draw.rect(_bg_surface, col, (tx, ty, 50, 30))
    pygame.draw.rect(_bg_surface, (52, 160, 38), (0, SH-80, SW, 6))

def get_bg():
    return _bg_surface

# ─────────────────────────────────────────────────────────────
# UTILITAIRES
# ─────────────────────────────────────────────────────────────
_fc = {}
def gf(size, bold=True):
    k=(size,bold)
    if k not in _fc: _fc[k]=pygame.font.SysFont('Arial',size,bold=bold)
    return _fc[k]

def txt(surf, text, x, y, size=22, color=BLACK, center=False, shadow=False):
    font = gf(size)
    if shadow:
        s=font.render(text,True,(0,0,0)); r=s.get_rect()
        if center: r.center=(x+2,y+2)
        else: r.topleft=(x+2,y+2)
        surf.blit(s,r)
    lbl=font.render(text,True,color); rect=lbl.get_rect()
    if center: rect.center=(x,y)
    else: rect.topleft=(x,y)
    surf.blit(lbl,rect)
    return rect

def rr(surf, color, rect, r=10, bw=0, bc=BLACK):
    if color: pygame.draw.rect(surf, color, rect, border_radius=r)
    if bw:    pygame.draw.rect(surf, bc, rect, bw, border_radius=r)

def lerp(a,b,t): return a+(b-a)*t

def draw_gradient_box(surf, rect, c_top, c_bot, radius=10):
    clip = surf.get_clip()
    surf.set_clip(rect.inflate(0,0))
    x,y,w,h = rect
    for dy in range(h):
        t = dy/max(h-1,1)
        c = tuple(int(lerp(c_top[i],c_bot[i],t)) for i in range(3))
        pygame.draw.line(surf,c,(x,y+dy),(x+w,y+dy))
    surf.set_clip(clip)
    pygame.draw.rect(surf, BLACK, rect, 2, border_radius=radius)

def draw_sun(surf, cx=690, cy=75):
    t = pygame.time.get_ticks() / 800
    pygame.draw.circle(surf, (*SUN_RAY, 80), (cx,cy), 52)
    for i in range(12):
        angle = i*math.pi/6 + t*0.3
        for r1,r2,thick in [(55,72,3),(55,68,1)]:
            x1 = cx+int(r1*math.cos(angle)); y1 = cy+int(r1*math.sin(angle))
            x2 = cx+int(r2*math.cos(angle)); y2 = cy+int(r2*math.sin(angle))
            pygame.draw.line(surf, SUN_RAY, (x1,y1), (x2,y2), thick)
    pygame.draw.circle(surf, SUN_COL, (cx,cy), 42)
    pygame.draw.circle(surf, YELLOW_LT,(cx-8,cy-8), 16)
    pygame.draw.circle(surf, BLACK, (cx,cy), 42, 2)

def draw_cloud(surf, cx, cy, cw):
    shadow_c = (200,220,240)
    for ox,oy,cr in [(-cw//2+10,8,cw//5),(0,5,cw//4),(cw//2-10,8,cw//5)]:
        pygame.draw.circle(surf, shadow_c, (cx+ox, cy+oy), cr)
    for ox,oy,cr in [(-cw//2+10,0,cw//5),(0,-5,cw//4+2),(cw//2-10,0,cw//5)]:
        pygame.draw.circle(surf, WHITE, (cx+ox, cy+oy), cr)

def btn(surf, label, cx, cy, w=200, h=50, col=(90,180,80), hover=False):
    c   = tuple(min(255,v+30) for v in col) if hover else col
    r   = pygame.Rect(cx-w//2, cy-h//2, w, h)
    sh  = pygame.Rect(cx-w//2+4, cy-h//2+5, w, h)
    pygame.draw.rect(surf, tuple(max(0,v-50) for v in col), sh, border_radius=14)
    draw_gradient_box(surf, r, tuple(min(255,v+25) for v in c), c, 14)
    txt(surf, label, cx, cy, 22, WHITE, center=True, shadow=True)
    return r

def br(cx,cy,w,h): return pygame.Rect(cx-w//2,cy-h//2,w,h)
