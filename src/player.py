import pygame
import math
from src.settings import *
from src.utils import txt, draw_gradient_box


class Player:
    PW, PH = 40, 56
    COLORS = [
        {'body':(55,130,225),'hair':(30,20,80),'skin':(255,210,165),'shoe':(30,30,80)},
    ]

    JUMP_FORCE = -7.0
    PLAYER_GRAVITY = 0.35
    GROUND_Y = SH - 85

    def __init__(self):
        self.x     = float(SW//2)
        self.y     = float(self.GROUND_Y - self.PH//2)
        self.speed = 5
        self.lives = 3
        self.held  = None
        self.inv   = 0
        self.blink = 0
        self.bob   = 0.0
        self.dir   = 1
        self.pal   = self.COLORS[0]
        # Saut
        self.vy        = 0.0
        self.on_ground = True

    def update(self, keys):
        moved = False
        if keys[pygame.K_LEFT]:
            self.x -= self.speed; self.dir=-1; moved=True
        if keys[pygame.K_RIGHT]:
            self.x += self.speed; self.dir= 1; moved=True
        self.x = max(self.PW//2+5, min(SW-self.PW//2-5, self.x))

        # Saut (ESPACE ou FLÈCHE HAUT)
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.on_ground:
            self.vy = self.JUMP_FORCE
            self.on_ground = False

        # Gravité
        if not self.on_ground:
            self.vy += self.PLAYER_GRAVITY
            self.y  += self.vy
            if self.y >= self.GROUND_Y - self.PH//2:
                self.y = self.GROUND_Y - self.PH//2
                self.vy = 0.0
                self.on_ground = True

        if moved and self.on_ground:
            self.bob = (self.bob+0.35) % (math.pi*2)
        if self.inv > 0:
            self.inv  -= 1
            self.blink = (self.blink+1) % 6
        else:
            self.blink = 0

    def take_hit(self):
        if self.inv == 0:
            self.lives -= 1
            self.held   = None
            self.inv    = 90
            return True
        return False

    def pick_up(self, item):
        if self.held is None:
            self.held = item.type
            item.alive = False
            return True
        return False

    def deposit(self, b):
        if self.held is None: return False
        if b.type == self.held:
            self.held = None; b.hit_good(); return True
        else:
            b.hit_bad(); return False

    def draw(self, surf):
        if self.blink >= 3: return
        cx = int(self.x)
        bob_y = int(math.sin(self.bob) * 2) if self.on_ground else 0
        cy = int(self.y) + bob_y
        p  = self.pal

        # Ombre
        sh = pygame.Surface((40,10), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0,0,0,60), sh.get_rect())
        surf.blit(sh, (cx-20, int(self.GROUND_Y)+self.PH//2-30))

        # Cape
        cape_pts = [
            (cx-16+2, cy-2),
            (cx-26+2, cy+26),
            (cx+26+2, cy+26),
            (cx+16+2, cy-2),
        ]
        pygame.draw.polygon(surf, (190,40,40), cape_pts)
        pygame.draw.polygon(surf, BLACK, cape_pts, 2)

        # Corps
        body = pygame.Rect(cx-14, cy-4, 28, 32)
        draw_gradient_box(surf, body, tuple(min(255,v+25) for v in p['body']),
                          p['body'], 7)
        txt(surf, 'H', cx, cy+10, 18, WHITE, center=True)

        # Bras
        arm_y = cy+8
        pygame.draw.line(surf, p['body'], (cx-14, arm_y), (cx-22, arm_y+12), 5)
        pygame.draw.line(surf, p['body'], (cx+14, arm_y), (cx+22, arm_y+12), 5)
        pygame.draw.circle(surf, p['skin'], (cx-22, arm_y+13), 5)
        pygame.draw.circle(surf, p['skin'], (cx+22, arm_y+13), 5)

        # Tête
        pygame.draw.circle(surf, BLACK,    (cx+1, cy-19), 17)
        pygame.draw.circle(surf, p['skin'], (cx,   cy-20), 17)

        # Cheveux
        pygame.draw.arc(surf, p['hair'],
                        pygame.Rect(cx-15, cy-36, 30, 20),
                        0, math.pi, 5)
        for hx in range(cx-12, cx+14, 5):
            pygame.draw.line(surf, p['hair'], (hx, cy-35), (hx, cy-28), 3)

        # Yeux
        for ex in [cx-6, cx+6]:
            pygame.draw.circle(surf, WHITE,  (ex, cy-21), 6)
            pygame.draw.circle(surf, (50,100,200), (ex+self.dir, cy-20), 4)
            pygame.draw.circle(surf, BLACK,  (ex+self.dir, cy-20), 2)
            pygame.draw.circle(surf, WHITE,  (ex+self.dir+1, cy-22), 1)
        pygame.draw.circle(surf, (255,180,180), (cx-10, cy-14), 4)
        pygame.draw.circle(surf, (255,180,180), (cx+10, cy-14), 4)
        pygame.draw.arc(surf, BLACK,
                        pygame.Rect(cx-6, cy-13, 12, 8),
                        math.pi, 2*math.pi, 2)

        # Jambes
        leg_anim = int(math.sin(self.bob)*6) if self.on_ground else 0
        pygame.draw.rect(surf, TRASH_DK.get('papier',(30,60,140)),
                         pygame.Rect(cx-12, cy+27, 11, 22+leg_anim), border_radius=4)
        pygame.draw.rect(surf, TRASH_DK.get('papier',(30,60,140)),
                         pygame.Rect(cx+1,  cy+27, 11, 22-leg_anim), border_radius=4)
        pygame.draw.ellipse(surf, p['shoe'], pygame.Rect(cx-18, cy+46+leg_anim, 18, 9))
        pygame.draw.ellipse(surf, p['shoe'], pygame.Rect(cx+1,  cy+44-leg_anim, 18, 9))

        # Objet porté
        if self.held:
            halo_c = TRASH_C[self.held]
            halo   = pygame.Surface((34,34), pygame.SRCALPHA)
            pygame.draw.circle(halo, (*halo_c, 70), (17,17), 17)
            surf.blit(halo, (cx-17, cy-57))
            pygame.draw.circle(surf, halo_c, (cx, cy-50), 13)
            pygame.draw.circle(surf, TRASH_LT[self.held], (cx-4, cy-54), 5)
            pygame.draw.circle(surf, BLACK, (cx, cy-50), 13, 2)

    @property
    def rect(self):
        return pygame.Rect(int(self.x)-self.PW//2, int(self.y)-self.PH//2,
                           self.PW, self.PH)

    @property
    def feet_rect(self):
        return pygame.Rect(int(self.x)-self.PW//2-8, int(self.y)+8,
                           self.PW+16, self.PH//2)
