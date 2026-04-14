import pygame
import sys
import math
import random
from src.settings import *
from src.utils import *
from src.player import Player
from src.waste import TrashItem, ThrownTrash
from src.bin import TrashBin
from src.boss import Boss, Obstacle


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SW, SH))
        pygame.display.set_caption("Trash Hero 2 — Trie les déchets !")
        self.clock = pygame.time.Clock()
        build_bg()

        self.state          = 'menu'
        self.unlocked       = 1
        self.dev_mode       = False
        self.current_level  = 0
        self.player         = None
        self.trash_items    = []
        self.bins           = []
        self.obstacles      = []
        self.boss           = None
        self.score          = 0
        self.timer          = 0
        self.spawn_timer    = 0
        self.obs_spawn      = 0
        self.message        = ''
        self.msg_color      = WHITE
        self.msg_timer      = 0
        self.particles      = []
        self.thrown_items    = []
        self.trash_spawned  = 0
        # Saisie mot de passe dev
        self.dev_input       = ''
        self.dev_input_active = False
        self.dev_msg         = ''
        self.dev_msg_timer   = 0
        # Décor
        self.stars  = [(random.randint(0,SW),random.randint(0,SH//3),
                         random.randint(1,3)) for _ in range(50)]
        self.clouds = [(random.randint(0,SW),random.randint(25,100),
                         random.randint(80,140)) for _ in range(5)]
        self.menu_bg_items = [
            {'x':random.randint(0,SW),'y':random.randint(0,SH),
             'type':random.choice(list(TRASH_C.keys())),
             'vx':random.uniform(-0.5,0.5),'vy':random.uniform(-0.5,0.5),
             'r':random.randint(12,22),'a':random.uniform(0,6.28)}
            for _ in range(18)]

    # ── DÉMARRAGE ─────────────────────────────────────────────

    def start_level(self, idx):
        cfg=LEVELS[idx]; self.current_level=idx
        self.player=Player(); self.trash_items=[]; self.obstacles=[]
        self.thrown_items=[]; self.particles=[]; self.score=0
        self.trash_spawned=0
        self.timer=cfg['time']*FPS; self.spawn_timer=0; self.obs_spawn=0
        types=cfg['types']; spacing=SW//(len(types)+1)
        self.bins=[TrashBin(t,spacing*(i+1)) for i,t in enumerate(types)]
        self.state='playing'

    def start_boss(self):
        self.boss=Boss(); self.player=Player()
        self.trash_items=[]; self.obstacles=[]; self.thrown_items=[]; self.particles=[]
        self.score=0; self.trash_spawned=0
        self.timer=120*FPS; self.spawn_timer=0; self.obs_spawn=0
        types=list(TRASH_C.keys()); spacing=SW//(len(types)+1)
        self.bins=[TrashBin(t,spacing*(i+1)) for i,t in enumerate(types)]
        self.state='boss'

    # ── BOUCLE PRINCIPALE ─────────────────────────────────────

    def run(self):
        while True:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()

    # ── ÉVÉNEMENTS ────────────────────────────────────────────

    def handle_events(self):
        mp=pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()

            if event.type==pygame.KEYDOWN:
                # Saisie mot de passe dev
                if self.dev_input_active:
                    if event.key == pygame.K_RETURN:
                        self._check_dev_password()
                    elif event.key == pygame.K_ESCAPE:
                        self.dev_input_active = False
                        self.dev_input = ''
                    elif event.key == pygame.K_BACKSPACE:
                        self.dev_input = self.dev_input[:-1]
                    else:
                        if event.unicode and len(self.dev_input) < 20:
                            self.dev_input += event.unicode
                    continue

                if event.key==pygame.K_ESCAPE:
                    if self.state in('playing','boss'): self.state='level_select'
                    elif self.state=='level_select': self.state='menu'
                    elif self.state=='rules': self.state='menu'

                # Touche E pour déposer dans la poubelle
                if event.key == pygame.K_e and self.state in ('playing', 'boss'):
                    self._try_deposit()

                # Touche F pour lancer le déchet vers la bonne poubelle
                if event.key == pygame.K_f and self.state in ('playing', 'boss'):
                    self._try_throw()

            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                self._click(mp)

    def _check_dev_password(self):
        if self.dev_input == DEV_PASSWORD:
            self.dev_mode = True
            self.unlocked = 6
            self.dev_msg = 'Mode Dev activé ! Tous les niveaux débloqués !'
            self.dev_msg_timer = 120
        else:
            self.dev_msg = 'Mot de passe incorrect !'
            self.dev_msg_timer = 90
        self.dev_input_active = False
        self.dev_input = ''

    def _try_deposit(self):
        if self.player and self.player.held:
            for b in self.bins:
                if self.player.feet_rect.colliderect(b.rect):
                    res = self.player.deposit(b)
                    if res:
                        self.score += 1
                        self._spawn_confetti(b.cx, b.y)
                        self._msg('+1  Bien trié !', (80,240,80))
                        if self.state == 'boss':
                            if self.boss.take_hit():
                                self.state = 'victory'; return
                    else:
                        self.player.held = None
                        if self.score > 0: self.score -= 1
                        self._msg('Mauvaise poubelle !', ORANGE)
                    break

    def _try_throw(self):
        if self.player and self.player.held:
            # Trouver la poubelle correspondante au type porté
            target_bin = None
            for b in self.bins:
                if b.type == self.player.held:
                    target_bin = b
                    break
            if target_bin is None:
                return
            # Lancer le déchet vers la poubelle cible
            thrown = ThrownTrash(
                self.player.held,
                self.player.x, self.player.y - 40,
                target_bin.cx, target_bin.y + 20
            )
            self.thrown_items.append(thrown)
            self.player.held = None

    def _click(self, pos):
        if self.state=='menu':
            if br(SW//2,330,220,54).collidepoint(pos): self.state='level_select'
            if br(SW//2,395,220,54).collidepoint(pos): self.state='rules'
            if br(SW//2,460,220,54).collidepoint(pos): pygame.quit(); sys.exit()
            # Bouton mode dev
            if br(SW//2,520,220,40).collidepoint(pos):
                self.dev_input_active = True
                self.dev_input = ''
        elif self.state=='rules':
            if br(SW//2,SH-40,200,46).collidepoint(pos): self.state='menu'
        elif self.state=='level_select':
            for i in range(5):
                if self._cr(i).collidepoint(pos) and i<self.unlocked:
                    self.start_level(i); return
            if br(SW//2,512,220,50).collidepoint(pos) and self.unlocked>5:
                self.start_boss()
            if br(80,32,120,36).collidepoint(pos): self.state='menu'
        elif self.state in('level_complete','level_fail'):
            if br(SW//2,370,200,50).collidepoint(pos): self.start_level(self.current_level)
            if br(SW//2,435,200,50).collidepoint(pos): self.state='level_select'
        elif self.state in('victory','gameover'):
            if br(SW//2,410,240,56).collidepoint(pos): self.state='menu'

    def _cr(self, i):
        col=i%3; row=i//3
        x=130+col*200; y=190+row*155
        return pygame.Rect(x-85,y-65,170,130)

    # ── MISE À JOUR ───────────────────────────────────────────

    def update(self):
        if self.dev_msg_timer > 0:
            self.dev_msg_timer -= 1

        if self.state not in('playing','boss'): return
        keys=pygame.key.get_pressed()
        cfg=LEVELS[self.current_level] if self.state=='playing' else None
        self.player.update(keys)
        self.timer-=1
        if self.timer<=0 and self.state=='playing':
            self.state='level_fail'; return

        # Spawn déchets (limité au total défini pour le niveau)
        self.spawn_timer+=1
        interval=cfg['spawn'] if cfg else 45
        total_limit=cfg['total'] if cfg else 999
        if self.spawn_timer>=interval and self.trash_spawned<total_limit:
            self.spawn_timer=0
            types=cfg['types'] if cfg else list(TRASH_C.keys())
            speed=cfg['speed'] if cfg else (3.5,5.5)
            count = 1 if self.state=='playing' else 2
            for _ in range(count):
                if self.trash_spawned<total_limit:
                    self.trash_items.append(TrashItem(types,speed))
                    self.trash_spawned+=1

        # Spawn obstacles
        if self.state=='playing' and cfg['obstacles']>0:
            self.obs_spawn+=1
            if self.obs_spawn>180 and len(self.obstacles)<cfg['obstacles']:
                self.obs_spawn=0; self.obstacles.append(Obstacle())
        if self.state=='boss':
            if len(self.obstacles)<5:
                self.obs_spawn+=1
                if self.obs_spawn>75:
                    self.obs_spawn=0; self.obstacles.append(Obstacle())
            self.boss.update()
            if self.player.rect.colliderect(self.boss.get_rect()):
                if self.player.take_hit():
                    self._msg('Touché par le Boss !',RED)

        for item in self.trash_items: item.update()
        for obs  in self.obstacles:   obs.update()

        # Ramassage auto (au contact)
        if self.player.held is None:
            for item in self.trash_items:
                if item.alive and self.player.rect.colliderect(item.get_rect()):
                    if self.player.pick_up(item): break

        # (Le dépôt se fait maintenant avec la touche E — voir handle_events)

        # Mise à jour des déchets lancés
        for thrown in self.thrown_items:
            thrown.update()
        # Collision déchets lancés → poubelles
        for thrown in list(self.thrown_items):
            if not thrown.alive:
                continue
            for b in self.bins:
                if thrown.get_rect().colliderect(b.rect):
                    if thrown.type == b.type:
                        self.score += 1
                        self._spawn_confetti(b.cx, b.y)
                        self._msg('+1  Bien lancé !', (80,240,80))
                        b.hit_good()
                        if self.state == 'boss':
                            if self.boss.take_hit():
                                self.state = 'victory'; return
                    else:
                        if self.score > 0: self.score -= 1
                        self._msg('Mauvaise poubelle !', ORANGE)
                        b.hit_bad()
                    thrown.alive = False
                    break
        self.thrown_items = [t for t in self.thrown_items if t.alive]

        # Obstacles
        for obs in self.obstacles:
            if self.player.rect.colliderect(obs.get_rect()):
                if self.player.take_hit():
                    self._msg('Aïe !',RED)

        if self.player.lives<=0:
            self.state='gameover' if self.state=='boss' else 'level_fail'; return
        # Échec si tous les déchets ont été spawn et qu'il n'en reste plus à ramasser
        if (self.state=='playing' and self.trash_spawned>=cfg['total']
                and len(self.trash_items)==0 and len(self.thrown_items)==0
                and self.player.held is None and self.score<cfg['target']):
            self.state='level_fail'; return
        if self.state=='playing' and self.score>=cfg['target']:
            if self.current_level+2>self.unlocked and not self.dev_mode:
                self.unlocked=min(self.current_level+2,6)
            elif self.current_level+2>self.unlocked and self.dev_mode:
                pass  # déjà tout débloqué
            self.state='level_complete'

        if self.msg_timer>0: self.msg_timer-=1
        self.particles=[(x,y+vy,vy-0.12,l-1,c)
                        for x,y,vy,l,c in self.particles if l>0]
        self.trash_items=[i for i in self.trash_items if i.alive]

    def _msg(self,text,color=WHITE):
        self.message=text; self.msg_color=color; self.msg_timer=65

    def _spawn_confetti(self,cx,cy):
        colors=[(255,220,50),(100,255,100),(255,100,200),(100,200,255),(255,150,50)]
        for _ in range(16):
            self.particles.append((
                cx+random.randint(-25,25), float(cy),
                random.uniform(-4.5,-1), 50,
                random.choice(colors)))

    # ── DESSIN ────────────────────────────────────────────────

    def draw(self):
        if   self.state=='menu':           self._menu()
        elif self.state=='rules':          self._rules()
        elif self.state=='level_select':   self._level_select()
        elif self.state in('playing','boss'):self._game()
        elif self.state=='level_complete': self._end(True)
        elif self.state=='level_fail':     self._end(False)
        elif self.state=='victory':        self._victory()
        elif self.state=='gameover':       self._gameover()

    def _draw_world(self):
        self.screen.blit(get_bg(),(0,0))
        draw_sun(self.screen)
        t = pygame.time.get_ticks()/1000
        for i,(cx,cy,cw) in enumerate(self.clouds):
            dx = int(math.sin(t*0.2+i)*8)
            draw_cloud(self.screen, cx+dx, cy, cw)

    def _game(self):
        self._draw_world()
        for b in self.bins: b.draw(self.screen)
        # Surbrillance de la bonne poubelle
        if self.player and self.player.held:
            tick = pygame.time.get_ticks()//350
            if tick%2==0:
                for b in self.bins:
                    if b.type==self.player.held:
                        glow=pygame.Surface((b.BW+24,b.BH+24),pygame.SRCALPHA)
                        pygame.draw.rect(glow,(255,235,50,140),glow.get_rect(),
                                         border_radius=12)
                        self.screen.blit(glow,(b.cx-b.BW//2-12,b.y-12))
        for item in self.trash_items: item.draw(self.screen)
        for thrown in self.thrown_items: thrown.draw(self.screen)
        for obs in self.obstacles: obs.draw(self.screen)
        if self.state=='boss' and self.boss: self.boss.draw(self.screen)
        for px,py,vy,life,c in self.particles:
            r2=max(1,int(life/10))
            pygame.draw.circle(self.screen,c,(int(px),int(py)),r2)
        if self.player: self.player.draw(self.screen)
        self._hud()
        if self.msg_timer>0:
            txt(self.screen, self.message,
                SW//2, SH//2-75, 32, self.msg_color, center=True, shadow=True)

    def _hud(self):
        hud_surf=pygame.Surface((SW,48),pygame.SRCALPHA)
        pygame.draw.rect(hud_surf,(20,20,50,180),(0,0,SW,48),border_radius=0)
        self.screen.blit(hud_surf,(0,0))

        cfg=LEVELS[self.current_level] if self.state=='playing' else None
        target=cfg['target'] if cfg else (self.boss.MAX_HP if self.boss else '?')
        score_surf=pygame.Surface((180,36),pygame.SRCALPHA)
        pygame.draw.rect(score_surf,(255,235,50,60),(0,0,180,36),border_radius=10)
        self.screen.blit(score_surf,(6,6))
        txt(self.screen,f'Score : {self.score} / {target}',14,24,22,YELLOW)

        secs=max(0,self.timer//FPS)
        tcol=RED if secs<15 else WHITE
        rr(self.screen,(255,255,255,40),pygame.Rect(SW//2-55,6,110,36),10)
        txt(self.screen,f'Temps : {secs}s',SW//2,24,22,tcol,center=True)

        for i in range(self.player.lives):
            hx=SW-22-i*32; hy=24
            pygame.draw.circle(self.screen,RED,(hx-7,hy-3),7)
            pygame.draw.circle(self.screen,RED,(hx+7,hy-3),7)
            pygame.draw.polygon(self.screen,RED,[(hx-14,hy),(hx,hy+14),(hx+14,hy)])
            pygame.draw.circle(self.screen,RED_LT,(hx-9,hy-6),3)

        name=(LEVELS[self.current_level]['name']
              if self.state=='playing' else 'BOSS FINAL')
        txt(self.screen,name,SW//2,42,12,(200,230,255),center=True)

        # Indicateur déchet porté + rappel touche E
        if self.player.held:
            c=TRASH_C[self.player.held]
            ind_surf=pygame.Surface((SW-40,24),pygame.SRCALPHA)
            pygame.draw.rect(ind_surf,(*c,80),(0,0,SW-40,24),border_radius=8)
            self.screen.blit(ind_surf,(20,SH-28))
            txt(self.screen,f'Tu portes : {TRASH_LB[self.player.held]}  —  [E] Déposer  |  [F] Lancer',
                SW//2,SH-16,16,WHITE,center=True)

        # Indicateur mode dev
        if self.dev_mode:
            txt(self.screen,'[DEV]',SW-40,42,12,(255,100,100),center=True)

        # Déchets restants à spawn
        if cfg:
            remaining = cfg['total'] - self.trash_spawned + len(self.trash_items)
            txt(self.screen,f'Déchets restants : {remaining}',SW//2,SH-50,12,(200,230,255),center=True)

        # Rappel contrôles
        txt(self.screen,'ESPACE=Sauter  E=Déposer  F=Lancer',SW//2,SH-38,11,(200,200,220),center=True)

    def _menu(self):
        self.screen.fill((28,22,62))
        t=pygame.time.get_ticks()/1000
        for sx,sy,sr in self.stars:
            alpha=int(155+math.sin(t+sx)*100)
            c=tuple(min(255,v) for v in (alpha,alpha,alpha))
            pygame.draw.circle(self.screen,c,(sx,sy),sr)
        for item in self.menu_bg_items:
            item['x']=(item['x']+item['vx'])%SW
            item['y']=(item['y']+item['vy'])%SH
            item['a']=(item['a']+0.02)%(math.pi*2)
            c=TRASH_C[item['type']]
            pygame.draw.circle(self.screen,(*c,80),(int(item['x']),int(item['y'])),item['r'])
        title_r=pygame.Rect(SW//2-220,60,440,80)
        draw_gradient_box(self.screen,title_r,(80,40,140),(50,20,100),18)
        txt(self.screen,'TRASH HERO 2',SW//2+3,105,56,BLACK,center=True)
        txt(self.screen,'TRASH HERO 2',SW//2,103,56,YELLOW,center=True,shadow=False)
        txt(self.screen,'Trie les déchets — Sauve la planète !',
            SW//2,168,20,(175,235,155),center=True)
        for i,(t2,c) in enumerate(TRASH_C.items()):
            bx=110+i*150
            bob=int(math.sin(pygame.time.get_ticks()/500+i)*4)
            pygame.draw.circle(self.screen,TRASH_DK[t2],(bx+2,252+bob+2),26)
            pygame.draw.circle(self.screen,c,(bx,250+bob),26)
            pygame.draw.circle(self.screen,TRASH_LT[t2],(bx-7,242+bob),9)
            pygame.draw.circle(self.screen,BLACK,(bx,250+bob),26,2)
            txt(self.screen,TRASH_LB[t2],bx,284+bob,14,WHITE,center=True)
        mp=pygame.mouse.get_pos()
        btn(self.screen,'JOUER',   SW//2,330,220,54,(70,175,70), br(SW//2,330,220,54).collidepoint(mp))
        btn(self.screen,'RÈGLES',  SW//2,395,220,54,(55,120,190), br(SW//2,395,220,54).collidepoint(mp))
        btn(self.screen,'QUITTER', SW//2,460,220,54,(175,55,55), br(SW//2,460,220,54).collidepoint(mp))
        # Bouton Mode Dev
        btn(self.screen,'MODE DEV', SW//2,520,220,40,(100,80,160), br(SW//2,520,220,40).collidepoint(mp))

        # Champ de saisie du mot de passe
        if self.dev_input_active:
            overlay = pygame.Surface((SW, SH), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            box = pygame.Rect(SW//2-180, SH//2-60, 360, 120)
            draw_gradient_box(self.screen, box, (60, 40, 120), (40, 20, 80), 14)
            txt(self.screen, 'Mot de passe développeur :', SW//2, SH//2-35, 18, WHITE, center=True)
            # Champ texte
            input_box = pygame.Rect(SW//2-140, SH//2-8, 280, 36)
            pygame.draw.rect(self.screen, (30, 20, 60), input_box, border_radius=8)
            pygame.draw.rect(self.screen, WHITE, input_box, 2, border_radius=8)
            display_text = '*' * len(self.dev_input)
            txt(self.screen, display_text, SW//2-130, SH//2+2, 20, WHITE)
            txt(self.screen, 'Entrée = Valider  |  Echap = Annuler', SW//2, SH//2+42, 13, GRAY, center=True)

        # Message de retour dev
        if self.dev_msg_timer > 0:
            col = (100, 255, 100) if self.dev_mode else RED
            txt(self.screen, self.dev_msg, SW//2, SH//2+80, 20, col, center=True, shadow=True)

        if self.dev_mode:
            txt(self.screen, 'Mode Dev ACTIF', SW//2, SH-40, 16, (100, 255, 100), center=True)

        txt(self.screen,'EFREI Paris — Module TI250 — 2025-2026',
            SW//2,SH-16,14,(120,120,148),center=True)

    def _rules(self):
        self.screen.fill((28,22,62))
        t = pygame.time.get_ticks()/1000
        for sx,sy,sr in self.stars:
            alpha=int(155+math.sin(t+sx)*100)
            c=tuple(min(255,v) for v in (alpha,alpha,alpha))
            pygame.draw.circle(self.screen,c,(sx,sy),sr)

        # Titre
        title_r = pygame.Rect(SW//2-180, 30, 360, 55)
        draw_gradient_box(self.screen, title_r, (55,120,190), (35,80,150), 14)
        txt(self.screen, 'RÈGLES DU JEU', SW//2, 58, 36, YELLOW, center=True)

        # Cadre des règles
        box = pygame.Rect(50, 100, SW-100, 400)
        draw_gradient_box(self.screen, box, (45,35,85), (30,22,62), 14)

        rules = [
            ("1.", "Attrape les déchets qui tombent en les touchant."),
            ("2.", "Chaque déchet a une couleur : Papier (bleu),"),
            ("",   "Verre (vert), Plastique (jaune), Bio (marron)."),
            ("3.", "Dépose le déchet dans la bonne poubelle"),
            ("",   "en appuyant sur [E] quand tu es devant."),
            ("4.", "Tu peux aussi LANCER le déchet avec [F] !"),
            ("",   "Il vole tout seul vers la bonne poubelle."),
            ("5.", "Appuie sur ESPACE pour sauter par-dessus"),
            ("",   "les monstres rouges qui te font perdre une vie."),
            ("6.", "Tu as 3 vies (les coeurs en haut à droite)."),
            ("",   "Si tu en perds trop, c'est perdu !"),
            ("7.", "Attention : il y a un nombre limité de déchets."),
            ("",   "Ne te trompe pas trop de poubelle !"),
            ("8.", "Finis tous les niveaux pour affronter le BOSS !"),
        ]

        y = 120
        for num, line in rules:
            if num:
                txt(self.screen, num, 80, y, 18, YELLOW)
            txt(self.screen, line, 110, y, 17, WHITE)
            y += 26

        # Légende couleurs
        y += 10
        txt(self.screen, 'Les couleurs des poubelles :', SW//2, y, 18, YELLOW, center=True)
        y += 28
        labels = [('Papier', TRASH_C['papier']), ('Verre', TRASH_C['verre']),
                  ('Plastique', TRASH_C['plastique']), ('Bio', TRASH_C['organique'])]
        total_w = len(labels) * 140
        start_x = SW//2 - total_w//2 + 70
        for i, (name, col) in enumerate(labels):
            bx = start_x + i * 140
            pygame.draw.circle(self.screen, col, (bx, y), 14)
            pygame.draw.circle(self.screen, BLACK, (bx, y), 14, 2)
            txt(self.screen, name, bx, y + 22, 14, WHITE, center=True)

        mp = pygame.mouse.get_pos()
        btn(self.screen, '<- Retour', SW//2, SH-40, 200, 46, (65,70,115),
            br(SW//2, SH-40, 200, 46).collidepoint(mp))

    def _level_select(self):
        self.screen.fill((24,42,75))
        for sx,sy,sr in self.stars[:30]:
            pygame.draw.circle(self.screen,WHITE,(sx,sy),sr)
        txt(self.screen,'CHOISIS TON NIVEAU',SW//2+2,72,40,BLACK,center=True)
        txt(self.screen,'CHOISIS TON NIVEAU',SW//2,70,40,YELLOW,center=True,shadow=False)
        mp=pygame.mouse.get_pos()
        for i,cfg in enumerate(LEVELS):
            r=self._cr(i)
            locked=i>=self.unlocked
            hover=r.collidepoint(mp) and not locked
            c_top=(85,140,215) if not locked else (42,60,92)
            c_bot=(60,110,185) if not locked else (32,50,78)
            if hover: c_top=(100,160,240); c_bot=(75,130,210)
            bc=(220,220,240) if hover else (90,130,175)
            sh_r=pygame.Rect(r.x+3,r.y+4,r.w,r.h)
            pygame.draw.rect(self.screen,(0,0,0,80),sh_r,border_radius=14)
            draw_gradient_box(self.screen,r,c_top,c_bot,14)
            pygame.draw.rect(self.screen,bc,r,2,border_radius=14)
            if locked:
                txt(self.screen,'Verrouillé',r.centerx,r.centery-4,16,GRAY,center=True)
            else:
                txt(self.screen,cfg['name'],r.centerx,r.y+20,13,WHITE,center=True)
                txt(self.screen,f"Objectif : {cfg['target']} tris",r.centerx,r.centery+2,
                    15,YELLOW,center=True)
                txt(self.screen,cfg['hint'],r.centerx,r.centery+28,12,(200,230,255),center=True)
                if i<self.unlocked-1:
                    txt(self.screen,'***',r.centerx,r.bottom-18,18,YELLOW,center=True)
        boss_ok=self.unlocked>5
        bc2=(195,45,45) if boss_ok else (75,45,45)
        btn(self.screen,'BOSS FINAL',SW//2,512,220,50,bc2,
            br(SW//2,512,220,50).collidepoint(mp) and boss_ok)
        if not boss_ok:
            txt(self.screen,'Complète tous les niveaux !',SW//2,542,13,GRAY,center=True)
        btn(self.screen,'<- Retour',80,32,120,36,(65,70,115),
            br(80,32,120,36).collidepoint(mp))

        if self.dev_mode:
            txt(self.screen,'[MODE DEV ACTIF]',SW//2,SH-16,14,(255,100,100),center=True)

    def _end(self, success):
        self._draw_world()
        ov=pygame.Surface((SW,SH),pygame.SRCALPHA)
        ov.fill((0,0,0,175)); self.screen.blit(ov,(0,0))
        mp=pygame.mouse.get_pos()
        if success:
            t=pygame.time.get_ticks()/400
            for i in range(20):
                a=i*2*math.pi/20+t
                cx2=int(SW//2+math.cos(a)*(120+math.sin(t+i)*30))
                cy2=int(250+math.sin(a)*60)
                c2=list(TRASH_C.values())[i%4]
                pygame.draw.circle(self.screen,c2,(cx2,cy2),6)
            txt(self.screen,'NIVEAU RÉUSSI !',SW//2+2,190,52,BLACK,center=True)
            txt(self.screen,'NIVEAU RÉUSSI !',SW//2,188,52,YELLOW,center=True)
            txt(self.screen,f'Score : {self.score}',SW//2,262,30,WHITE,center=True)
            if not self.dev_mode:
                msg=f'Niveau {self.unlocked} débloqué !' if self.unlocked<=5 else 'Boss Final débloqué !'
            else:
                msg='Mode Dev — Tout est déjà débloqué !'
            txt(self.screen,msg,SW//2,308,22,(100,255,100),center=True,shadow=True)
        else:
            txt(self.screen,'NIVEAU ÉCHOUÉ...',SW//2,188,52,RED,center=True,shadow=True)
            txt(self.screen,'Plus de vies ou temps écoulé !',SW//2,262,22,GRAY,center=True)
        btn(self.screen,'Rejouer', SW//2,370,200,50,(70,175,70), br(SW//2,370,200,50).collidepoint(mp))
        btn(self.screen,'Niveaux', SW//2,435,200,50,(55,90,175),br(SW//2,435,200,50).collidepoint(mp))

    def _victory(self):
        self.screen.fill((15,45,15))
        t=pygame.time.get_ticks()/1000
        for i in range(60):
            a=i*2*math.pi/60+t*0.5
            rx=int(SW//2+math.cos(a)*(200+math.sin(t*2+i)*50))
            ry=int(SH//2+math.sin(a)*(150+math.cos(t+i)*40))
            c2=list(TRASH_C.values())[i%4]
            pygame.draw.circle(self.screen,c2,(rx,ry),5)
        txt(self.screen,'VICTOIRE !',SW//2+3,160,68,BLACK,center=True)
        txt(self.screen,'VICTOIRE !',SW//2,158,68,YELLOW,center=True)
        txt(self.screen,'Tu as vaincu le Boss des Déchets !',SW//2,248,28,WHITE,center=True)
        txt(self.screen,'La planète est sauvée !',SW//2,292,24,(100,255,100),center=True)
        txt(self.screen,'Tu es un vrai Trash Hero !',SW//2,332,20,YELLOW,center=True)
        mp=pygame.mouse.get_pos()
        btn(self.screen,'Menu Principal',SW//2,410,240,56,(70,145,70),
            br(SW//2,410,240,56).collidepoint(mp))

    def _gameover(self):
        self.screen.fill((45,8,8))
        for sx,sy,sr in self.stars:
            pygame.draw.circle(self.screen,(180,50,50),(sx,sy),sr)
        txt(self.screen,'GAME OVER',SW//2+3,168,68,BLACK,center=True)
        txt(self.screen,'GAME OVER',SW//2,166,68,RED,center=True)
        txt(self.screen,f'Score final : {self.score}',SW//2,258,32,WHITE,center=True)
        txt(self.screen,'Le Boss des Déchets a gagné... cette fois.',SW//2,306,20,GRAY,center=True)
        txt(self.screen,'Réessaie — tu peux y arriver !',SW//2,338,18,ORANGE,center=True)
        mp=pygame.mouse.get_pos()
        btn(self.screen,'Menu Principal',SW//2,410,240,56,(120,38,38),
            br(SW//2,410,240,56).collidepoint(mp))
