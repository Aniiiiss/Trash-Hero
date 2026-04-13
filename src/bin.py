import pygame
import math
from src.settings import *
from src.utils import gf, rr, lerp, draw_gradient_box


class TrashBin:
    BW, BH = 78, 94
    SIDE   = 12

    def __init__(self, trash_type, cx):
        self.type  = trash_type
        self.cx    = cx
        self.y     = SH - self.BH - 8
        self.flash = 0
        self.shake = 0
        self.scale = 1.0

    @property
    def rect(self):
        return pygame.Rect(self.cx-self.BW//2, self.y, self.BW, self.BH)

    def draw(self, surf):
        ox = int(math.sin(self.shake * 0.9) * 5) if self.shake > 0 else 0
        if self.shake > 0: self.shake -= 1
        good = self.flash > 0
        if self.flash > 0: self.flash -= 1

        cf = (130, 245, 130) if good else BIN_F[self.type]
        cs = (80,  180, 80)  if good else BIN_S[self.type]
        ct = (200, 255, 200) if good else BIN_T[self.type]

        bx = self.cx - self.BW//2 + ox
        by = self.y

        side_pts = [
            (bx+self.BW,     by),
            (bx+self.BW+self.SIDE, by-self.SIDE//2),
            (bx+self.BW+self.SIDE, by+self.BH-self.SIDE//2),
            (bx+self.BW,     by+self.BH),
        ]
        pygame.draw.polygon(surf, cs, side_pts)
        pygame.draw.polygon(surf, BLACK, side_pts, 1)

        top_pts = [
            (bx,              by),
            (bx+self.BW,      by),
            (bx+self.BW+self.SIDE, by-self.SIDE//2),
            (bx+self.SIDE,    by-self.SIDE//2),
        ]
        pygame.draw.polygon(surf, ct, top_pts)
        pygame.draw.polygon(surf, BLACK, top_pts, 1)

        front = pygame.Rect(bx, by, self.BW, self.BH)
        for dy in range(self.BH):
            t = dy/max(self.BH-1,1)
            c = tuple(int(lerp(min(255,cf[i]+15), max(0,cf[i]-25), t)) for i in range(3))
            pygame.draw.line(surf, c, (bx, by+dy), (bx+self.BW, by+dy))
        pygame.draw.rect(surf, BLACK, front, 2, border_radius=6)

        lid = pygame.Rect(bx-4, by-16, self.BW+8, 18)
        for dy in range(18):
            t = dy/17
            c = tuple(int(lerp(min(255,ct[i]+10), cf[i], t)) for i in range(3))
            pygame.draw.line(surf, c, (bx-4, by-16+dy), (bx-4+self.BW+8, by-16+dy))
        pygame.draw.rect(surf, BLACK, lid, 2, border_radius=5)

        handle = pygame.Rect(bx+self.BW//2-10, by-24, 20, 10)
        rr(surf, ct, handle, 4, 1)

        rx, ry = bx + self.BW//2, by + self.BH//2 - 10
        for i in range(3):
            a = i*2*math.pi/3 - math.pi/2
            ax = rx + int(14*math.cos(a))
            ay = ry + int(14*math.sin(a))
            pygame.draw.arc(surf, tuple(min(255,v+60) for v in cf),
                            pygame.Rect(ax-8, ay-8, 16, 16),
                            a+0.3, a+math.pi*1.3, 3)

        lbl = gf(13).render(TRASH_LB[self.type], True, WHITE)
        surf.blit(lbl, (self.cx-lbl.get_width()//2+ox, by+self.BH-22))

        fx, fy = self.cx+ox, by+self.BH//2-8
        pygame.draw.circle(surf, WHITE,  (fx-10, fy), 6)
        pygame.draw.circle(surf, WHITE,  (fx+10, fy), 6)
        pygame.draw.circle(surf, BLACK,  (fx-9,  fy), 3)
        pygame.draw.circle(surf, BLACK,  (fx+11, fy), 3)
        pygame.draw.circle(surf, WHITE,  (fx-8,  fy-1), 1)
        pygame.draw.circle(surf, WHITE,  (fx+12, fy-1), 1)
        pygame.draw.arc(surf, BLACK,
                        pygame.Rect(fx-9, fy+6, 18, 11),
                        math.pi, 2*math.pi, 2)

    def hit_good(self): self.flash=22
    def hit_bad(self):  self.shake=15
