import pygame
import math
import random
from src.settings import *
from src.utils import gf, txt, rr, lerp, draw_gradient_box


class Obstacle:
    R = 19

    def __init__(self):
        side = random.choice(['left','right','top'])
        if side=='left':
            self.x=float(-self.R); self.y=float(random.randint(60,SH-160))
            spd=random.uniform(2.5,4.0); ang=random.uniform(-0.4,0.4)
        elif side=='right':
            self.x=float(SW+self.R); self.y=float(random.randint(60,SH-160))
            spd=random.uniform(2.5,4.0); ang=math.pi+random.uniform(-0.4,0.4)
        else:
            self.x=float(random.randint(60,SW-60)); self.y=float(-self.R)
            spd=random.uniform(2.0,3.5); ang=math.pi/2+random.uniform(-0.3,0.3)
        self.vx=math.cos(ang)*spd; self.vy=math.sin(ang)*spd
        self.t = random.uniform(0, math.pi*2)

    def update(self):
        self.x+=self.vx; self.y+=self.vy
        self.t+=0.1
        if self.x<self.R:          self.x=self.R;          self.vx= abs(self.vx)
        if self.x>SW-self.R:       self.x=SW-self.R;       self.vx=-abs(self.vx)
        if self.y<self.R+45:       self.y=self.R+45;       self.vy= abs(self.vy)
        if self.y>SH-84-self.R:    self.y=SH-84-self.R;    self.vy=-abs(self.vy)

    def draw(self, surf):
        cx,cy = int(self.x), int(self.y)
        r2 = self.R + int(math.sin(self.t)*3)
        pygame.draw.ellipse(surf,(0,0,0,60),
                            pygame.Rect(cx-r2,cy-4,r2*2,8))
        for i in range(7):
            a = i*2*math.pi/7 + self.t*0.5
            tr = r2+10+int(math.sin(self.t+i)*3)
            tx = cx+int(tr*math.cos(a)); ty = cy+int(tr*math.sin(a))
            pygame.draw.circle(surf,(165,35,35),(tx,ty),6)
            pygame.draw.circle(surf,BLACK,(tx,ty),6,1)
            pygame.draw.line(surf,(165,35,35),(cx,cy),(tx,ty),3)
        pygame.draw.circle(surf,(45,0,0),(cx+2,cy+2),r2)
        pygame.draw.circle(surf,(185,45,45),(cx,cy),r2)
        pygame.draw.circle(surf,(230,100,100),(cx-r2//3,cy-r2//3),r2//3)
        pygame.draw.circle(surf,BLACK,(cx,cy),r2,2)
        for ex,ey in [(cx-7,cy-4),(cx+7,cy-4)]:
            pygame.draw.circle(surf,(255,80,0),(ex,ey),7)
            pygame.draw.circle(surf,YELLOW,(ex,ey),5)
            pygame.draw.circle(surf,BLACK,(ex,ey),3)
            pygame.draw.circle(surf,WHITE,(ex+1,ey-1),1)
        pygame.draw.arc(surf,BLACK,pygame.Rect(cx-7,cy+5,14,9),0,math.pi,2)
        for tx in [cx-5,cx,cx+5]:
            pygame.draw.line(surf,BLACK,(tx,cy+6),(tx,cy+10),1)

    def get_rect(self):
        return pygame.Rect(int(self.x)-self.R,int(self.y)-self.R,self.R*2,self.R*2)


class Boss:
    BW,BH = 160,180
    MAX_HP = 10

    def __init__(self):
        self.x=float(SW//2); self.y=float(185)
        self.hp=self.MAX_HP; self.vx=2.0
        self.hit_flash=0; self.t=0.0

    def update(self):
        self.x+=self.vx; self.t+=0.04
        if self.x<self.BW//2+20 or self.x>SW-self.BW//2-20: self.vx*=-1
        if self.hit_flash>0: self.hit_flash-=1
        speed=2.0+(self.MAX_HP-self.hp)*0.38
        self.vx=math.copysign(speed,self.vx)

    def take_hit(self):
        self.hp-=1; self.hit_flash=22
        return self.hp<=0

    def draw(self, surf):
        cx,cy = int(self.x), int(self.y)
        bob   = int(math.sin(self.t)*4)
        cy   += bob
        c = (255,140,140) if self.hit_flash>0 else (150,70,220)

        sh = pygame.Surface((self.BW+20,22),pygame.SRCALPHA)
        pygame.draw.ellipse(sh,(0,0,0,70),sh.get_rect())
        surf.blit(sh,(cx-self.BW//2-10,int(self.y)+self.BH//2-8))

        TLIST = list(TRASH_C.values())
        for i,ang in enumerate([0,math.pi/3,2*math.pi/3,math.pi,4*math.pi/3,5*math.pi/3]):
            a2 = ang+self.t*0.4
            bx2=cx+int((self.BW//2+30)*math.cos(a2))
            by2=cy+int((self.BH//3+5)*math.sin(a2))+10
            pygame.draw.circle(surf,TLIST[i%4],(bx2,by2),22)
            pygame.draw.circle(surf,TRASH_LT[list(TRASH_C.keys())[i%4]],(bx2-6,by2-6),7)
            pygame.draw.circle(surf,BLACK,(bx2,by2),22,2)

        body=pygame.Rect(cx-self.BW//2,cy-self.BH//2,self.BW,self.BH)
        draw_gradient_box(surf,body,tuple(min(255,v+20) for v in c),c,24)

        for i in range(8):
            kx=cx-49+i*14; ky=cy-self.BH//2-16
            pygame.draw.circle(surf,TLIST[i%4],(kx,ky),9)
            pygame.draw.circle(surf,BLACK,(kx,ky),9,1)

        for ex,ey in [(cx-36,cy-32),(cx+36,cy-32)]:
            pygame.draw.circle(surf,WHITE,(ex,ey),26)
            pygame.draw.circle(surf,(255,60,0),(ex,ey),20)
            pygame.draw.circle(surf,BLACK,(ex+4,ey+4),13)
            pygame.draw.circle(surf,WHITE,(ex+8,ey+1),5)
            pygame.draw.circle(surf,BLACK,(ex,ey),26,2)

        mouth=pygame.Rect(cx-42,cy+14,84,42)
        pygame.draw.ellipse(surf,(40,20,20),mouth)
        pygame.draw.ellipse(surf,BLACK,mouth,2)
        pygame.draw.circle(surf,(200,50,80),(cx,cy+38),6)
        for i in range(6):
            tx=mouth.x+8+i*14
            pygame.draw.polygon(surf,WHITE,[
                (tx,mouth.y+2),(tx+9,mouth.y+2),(tx+4,mouth.y+16)])
        for i in range(5):
            tx=mouth.x+14+i*14
            pygame.draw.polygon(surf,WHITE,[
                (tx,mouth.bottom-2),(tx+9,mouth.bottom-2),(tx+4,mouth.bottom-16)])

        bw=230; bx=cx-bw//2; by=cy-self.BH//2-42
        rr(surf,(80,0,0),pygame.Rect(bx,by,bw,20),10)
        hp_w=max(0,int(bw*self.hp/self.MAX_HP))
        for dx in range(hp_w):
            t2=dx/max(hp_w-1,1)
            lc2=(int(lerp(255,220,t2)),int(lerp(50,30,t2)),int(lerp(50,30,t2)))
            pygame.draw.line(surf,lc2,(bx+dx,by),(bx+dx,by+20))
        pygame.draw.rect(surf,BLACK,pygame.Rect(bx,by,bw,20),2,border_radius=10)
        txt(surf,f'Boss PV : {self.hp}/{self.MAX_HP}',cx,by-14,16,RED,center=True,shadow=True)

    def get_rect(self):
        return pygame.Rect(int(self.x)-self.BW//2,int(self.y)-self.BH//2,
                           self.BW,self.BH)
