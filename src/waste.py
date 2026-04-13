import pygame
import math
import random
from src.settings import *

GROUND_Y = SH - 70
BOUNCE_FACTOR = 0.6
MAX_BOUNCES = 3


class TrashItem:
    R = 22

    def __init__(self, types, speed_range):
        self.type  = random.choice(types)
        self.x     = float(random.randint(self.R+20, SW-self.R-20))
        self.y     = float(-self.R*2)
        self.vx    = random.uniform(-1.3, 1.3)
        self.vy    = random.uniform(*speed_range)
        self.alive = True
        self.angle = random.uniform(0, math.pi*2)
        self.on_ground = False
        self.bounces   = 0
        self.ground_timer = 0

    def update(self):
        if self.on_ground:
            self.ground_timer += 1
            if self.ground_timer > 300:
                self.alive = False
            return

        self.vy   += GRAVITY
        self.x    += self.vx
        self.y    += self.vy
        self.angle = (self.angle + 0.06) % (math.pi*2)

        if self.x < self.R:    self.x=self.R;    self.vx= abs(self.vx)
        if self.x > SW-self.R: self.x=SW-self.R; self.vx=-abs(self.vx)

        # Rebondissement au sol
        if self.y >= GROUND_Y - self.R:
            self.y = GROUND_Y - self.R
            if self.bounces < MAX_BOUNCES:
                self.vy = -abs(self.vy) * BOUNCE_FACTOR
                self.vx *= 0.8
                self.bounces += 1
            else:
                self.on_ground = True
                self.vy = 0
                self.vx = 0

    def draw(self, surf):
        cx, cy = int(self.x), int(self.y)
        c  = TRASH_C[self.type]
        lc = TRASH_LT[self.type]
        dk = TRASH_DK[self.type]

        if self.type == 'papier':
            s = pygame.Surface((self.R*2+4, self.R*2+4), pygame.SRCALPHA)
            pygame.draw.rect(s, c, (2,2,self.R*2,self.R*2), border_radius=6)
            pygame.draw.rect(s, lc, (6,4,self.R*2//2,4), border_radius=3)
            pygame.draw.rect(s, lc, (6,10,self.R*2-10,3), border_radius=2)
            pygame.draw.rect(s, lc, (6,15,self.R*2-6,3), border_radius=2)
            pygame.draw.rect(s, BLACK, (2,2,self.R*2,self.R*2), 2, border_radius=6)
            rot = pygame.transform.rotate(s, math.degrees(self.angle)*0.3)
            surf.blit(rot, rot.get_rect(center=(cx,cy)))
        elif self.type == 'verre':
            pygame.draw.ellipse(surf, dk,     (cx-self.R+2, cy-self.R+3, self.R*2-2, self.R*2))
            pygame.draw.ellipse(surf, c,      (cx-self.R, cy-self.R, self.R*2-2, self.R*2))
            pygame.draw.ellipse(surf, lc,     (cx-self.R+5, cy-self.R+4, 14, 10))
            pygame.draw.rect(surf,   c,       (cx-6, cy-self.R-12, 12, 14), border_radius=4)
            pygame.draw.rect(surf,   BLACK,   (cx-6, cy-self.R-12, 12, 14), 2, border_radius=4)
            pygame.draw.ellipse(surf, BLACK,  (cx-self.R, cy-self.R, self.R*2-2, self.R*2), 2)
        elif self.type == 'plastique':
            pygame.draw.circle(surf, dk,  (cx+2, cy+2), self.R)
            pygame.draw.circle(surf, c,   (cx,   cy),   self.R)
            pygame.draw.circle(surf, lc,  (cx-7, cy-7), self.R//3)
            pygame.draw.circle(surf, BLACK,(cx,  cy),   self.R, 2)
        else:
            pts = []
            for i in range(9):
                a = i*2*math.pi/9 + self.angle*0.2
                r2 = self.R + random.randint(-4,4)
                pts.append((cx+int(r2*math.cos(a)), cy+int(r2*math.sin(a))))
            pygame.draw.polygon(surf, dk, [(x+2,y+2) for x,y in pts])
            pygame.draw.polygon(surf, c,  pts)
            pygame.draw.polygon(surf, BLACK, pts, 2)
            pygame.draw.circle(surf, lc, (cx-6, cy-6), 6)

        # Visage méchant
        eye_y = cy - 3
        pygame.draw.circle(surf, WHITE, (cx-7, eye_y), 5)
        pygame.draw.circle(surf, WHITE, (cx+7, eye_y), 5)
        pygame.draw.circle(surf, BLACK, (cx-6, eye_y), 3)
        pygame.draw.circle(surf, BLACK, (cx+8, eye_y), 3)
        pygame.draw.circle(surf, WHITE, (cx-5, eye_y-1), 1)
        pygame.draw.circle(surf, WHITE, (cx+9, eye_y-1), 1)
        pygame.draw.line(surf, BLACK, (cx-11,eye_y-8),(cx-3,eye_y-5), 2)
        pygame.draw.line(surf, BLACK, (cx+3, eye_y-5),(cx+11,eye_y-8), 2)
        pygame.draw.arc(surf, BLACK, pygame.Rect(cx-7,cy+4,14,9), math.pi, 2*math.pi, 2)

    def get_rect(self):
        return pygame.Rect(int(self.x)-self.R, int(self.y)-self.R, self.R*2, self.R*2)
