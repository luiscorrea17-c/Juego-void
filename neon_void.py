"""
NEON VOID - Shooter espacial de supervivencia (pygame)

Instalación:  pip install pygame
Ejecución:    python neon_void.py

Controles:
  W A S D / Flechas   mover
  Ratón               apuntar
  Clic izq. / J       disparar
  ESPACIO             dash (esquiva e invulnerabilidad breve)
  P / ESC             pausa
  R                   reiniciar (en Game Over)
"""
import pygame
import json
import math
import os
import random
import sys

import pygame
from pygame import Vector2 as V

W, H = 1100, 700
FPS = 60
SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "neon_void_record.json")

BG = (8, 8, 18)
WHITE = (235, 240, 255)
CYAN = (80, 235, 255)
RED = (255, 80, 110)
PURPLE = (190, 110, 255)
ORANGE = (255, 160, 60)
GREEN = (110, 255, 160)
YELLOW = (255, 230, 90)
BLUE = (100, 150, 255)

ENEMY_TYPES = {
    "chaser":  dict(hp=20, speed=150, r=13, color=RED,    score=10, dmg=15, sides=3),
    "shooter": dict(hp=30, speed=95,  r=16, color=PURPLE, score=25, dmg=15, sides=4),
    "tank":    dict(hp=90, speed=65,  r=26, color=ORANGE, score=50, dmg=25, sides=6),
    "boss":    dict(hp=700, speed=55, r=58, color=YELLOW, score=500, dmg=35, sides=8),
}

POWERUPS = {
    "heal":   (GREEN,  "+"),
    "rapid":  (YELLOW, "R"),
    "triple": (CYAN,   "3"),
    "shield": (BLUE,   "S"),
}


def poly(surf, color, center, radius, sides, angle, width=0):
    pts = [
        (center[0] + math.cos(angle + i * math.tau / sides) * radius,
         center[1] + math.sin(angle + i * math.tau / sides) * radius)
        for i in range(sides)
    ]
    pygame.draw.polygon(surf, color, pts, width)


def glow(surf, color, pos, radius, alpha=70):
    s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(s, (*color, alpha), (radius, radius), radius)
    surf.blit(s, (pos[0] - radius, pos[1] - radius), special_flags=pygame.BLEND_RGBA_ADD)


class Particle:
    def __init__(self, pos, vel, life, color, size):
        self.pos, self.vel = V(pos), V(vel)
        self.life = self.max = life
        self.color, self.size = color, size

    def update(self, dt):
        self.life -= dt
        self.pos += self.vel * dt
        self.vel *= 0.96


class Bullet:
    def __init__(self, pos, vel, dmg, friendly, color, r=4, life=1.4):
        self.pos, self.vel = V(pos), V(vel)
        self.dmg, self.friendly, self.color = dmg, friendly, color
        self.r, self.life = r, life

    def update(self, dt):
        self.pos += self.vel * dt
        self.life -= dt


class Enemy:
    def __init__(self, kind, pos, wave):
        d = ENEMY_TYPES[kind]
        self.kind = kind
        self.pos = V(pos)
        self.hp = self.max_hp = d["hp"] * (1 + 0.07 * wave)
        self.speed = d["speed"] * (1 + 0.015 * wave)
        self.r, self.color, self.score = d["r"], d["color"], d["score"]
        self.dmg, self.sides = d["dmg"], d["sides"]
        self.angle = 0.0
        self.shoot_t = random.uniform(0.5, 1.5)
        self.spawn_t = random.uniform(3, 5)
        self.flash = 0.0
        self.phase = random.random() * 10

    def update(self, dt, game):
        p = game.player.pos
        to_p = p - self.pos
        dist = to_p.length() or 1
        dirv = to_p / dist
        self.angle = math.atan2(dirv.y, dirv.x)
        self.flash = max(0, self.flash - dt)
        self.phase += dt

        if self.kind in ("chaser", "tank"):
            self.pos += dirv * self.speed * dt
        elif self.kind == "shooter":
            side = V(-dirv.y, dirv.x)
            if dist > 340:
                self.pos += dirv * self.speed * dt
            elif dist < 240:
                self.pos -= dirv * self.speed * dt
            self.pos += side * math.sin(self.phase) * 60 * dt
            self.shoot_t -= dt
            if self.shoot_t <= 0:
                self.shoot_t = 1.6
                game.bullets.append(Bullet(self.pos, dirv * 330, 10, False, PURPLE, 5, 4))
        elif self.kind == "boss":
            target = V(W / 2, 170)
            if (target - self.pos).length() > 8:
                self.pos += (target - self.pos).normalize() * self.speed * dt
            else:
                self.pos.x += math.sin(self.phase * 0.6) * 140 * dt
            enraged = self.hp < self.max_hp * 0.5
            self.shoot_t -= dt
            if self.shoot_t <= 0:
                self.shoot_t = 0.9 if enraged else 1.3
                n = 18 if enraged else 12
                off = self.phase
                for i in range(n):
                    a = off + i * math.tau / n
                    game.bullets.append(Bullet(self.pos, V(math.cos(a), math.sin(a)) * 260, 10, False, YELLOW, 6, 6))
                if enraged:
                    game.bullets.append(Bullet(self.pos, dirv * 420, 14, False, RED, 8, 5))
            self.spawn_t -= dt
            if self.spawn_t <= 0:
                self.spawn_t = 4.5 if enraged else 6
                for _ in range(3):
                    game.enemies.append(Enemy("chaser", self.pos + V(random.uniform(-50, 50), random.uniform(-50, 50)), game.wave))

    def draw(self, surf):
        col = WHITE if self.flash > 0 else self.color
        glow(surf, self.color, self.pos, int(self.r * 2.2), 50)
        poly(surf, col, self.pos, self.r, self.sides, self.angle)
        poly(surf, BG, self.pos, self.r * 0.55, self.sides, self.angle)
        if self.kind in ("tank", "boss"):
            w = self.r * 2
            x, y = self.pos.x - w / 2, self.pos.y - self.r - 12
            pygame.draw.rect(surf, (40, 40, 60), (x, y, w, 5))
            pygame.draw.rect(surf, self.color, (x, y, w * max(0, self.hp / self.max_hp), 5))


class PowerUp:
    def __init__(self, pos, kind):
        self.pos, self.kind, self.life, self.t = V(pos), kind, 9.0, 0.0

    def update(self, dt):
        self.life -= dt
        self.t += dt


class Player:
    def __init__(self):
        self.pos = V(W / 2, H / 2)
        self.vel = V()
        self.hp = self.max_hp = 100
        self.angle = 0.0
        self.fire_cd = 0.0
        self.inv = 0.0
        self.dash_cd = 0.0
        self.dash_t = 0.0
        self.dash_dir = V(1, 0)
        self.rapid = self.triple = self.shield = 0.0
        self.r = 13


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("NEON VOID")
        self.screen = pygame.display.set_mode((W, H))
        self.canvas = pygame.Surface((W, H))
        self.clock = pygame.time.Clock()
        self.f_small = pygame.font.SysFont("consolas,menlo,dejavusansmono", 18, bold=True)
        self.f_mid = pygame.font.SysFont("consolas,menlo,dejavusansmono", 28, bold=True)
        self.f_big = pygame.font.SysFont("consolas,menlo,dejavusansmono", 72, bold=True)
        self.stars = [[random.uniform(0, W), random.uniform(0, H), random.uniform(10, 70), random.choice((1, 1, 2))]
                      for _ in range(120)]
        self.record = self.load_record()
        self.state = "menu"
        self.reset()

    # ---------- utilidades ----------
    def load_record(self):
        try:
            with open(SAVE_FILE) as f:
                return int(json.load(f).get("record", 0))
        except Exception:
            return 0

    def save_record(self):
        try:
            with open(SAVE_FILE, "w") as f:
                json.dump({"record": self.record}, f)
        except OSError:
            pass

    def reset(self):
        self.player = Player()
        self.enemies, self.bullets, self.particles, self.powerups = [], [], [], []
        self.score = 0
        self.wave = 0
        self.combo = 1
        self.combo_t = 0.0
        self.shake = 0.0
        self.queue = []
        self.spawn_t = 0.0
        self.wave_delay = 1.5
        self.banner_t = 0.0
        self.banner = ""

    def text(self, surf, font, txt, color, pos, center=False):
        img = font.render(txt, True, color)
        rect = img.get_rect(center=pos) if center else img.get_rect(topleft=pos)
        surf.blit(img, rect)

    def burst(self, pos, color, n=18, speed=260, size=3):
        for _ in range(n):
            a = random.uniform(0, math.tau)
            v = V(math.cos(a), math.sin(a)) * random.uniform(40, speed)
            self.particles.append(Particle(pos, v, random.uniform(0.3, 0.8), color, random.uniform(1.5, size)))

    # ---------- oleadas ----------
    def start_wave(self):
        self.wave += 1
        n = self.wave
        q = []
        if n % 5 == 0:
            q.append("boss")
            q += ["chaser"] * (n // 2)
        else:
            q += ["chaser"] * (4 + n * 2)
            q += ["shooter"] * max(0, n - 1)
            q += ["tank"] * (n // 3)
        random.shuffle(q)
        if "boss" in q:
            q.remove("boss")
            q.insert(0, "boss")
        self.queue = q
        self.banner = f"OLEADA {n}" + ("  -  JEFE" if n % 5 == 0 else "")
        self.banner_t = 2.2

    def spawn_enemy(self, kind):
        side = random.randrange(4)
        m = 40
        pos = {0: (random.uniform(0, W), -m), 1: (random.uniform(0, W), H + m),
               2: (-m, random.uniform(0, H)), 3: (W + m, random.uniform(0, H))}[side]
        if kind == "boss":
            pos = (W / 2, -80)
        self.enemies.append(Enemy(kind, pos, self.wave))

    # ---------- entrada ----------
    def read_input(self):
        k = pygame.key.get_pressed()
        mv = V((k[pygame.K_d] or k[pygame.K_RIGHT]) - (k[pygame.K_a] or k[pygame.K_LEFT]),
               (k[pygame.K_s] or k[pygame.K_DOWN]) - (k[pygame.K_w] or k[pygame.K_UP]))
        aim = V(pygame.mouse.get_pos())
        fire = pygame.mouse.get_pressed()[0] or k[pygame.K_j]
        return mv, aim, fire

    def dash(self):
        p = self.player
        if p.dash_cd <= 0:
            mv, aim, _ = self.read_input()
            p.dash_dir = mv.normalize() if mv.length() else (aim - p.pos).normalize() if (aim - p.pos).length() else V(1, 0)
            p.dash_t, p.dash_cd, p.inv = 0.16, 1.2, max(p.inv, 0.3)
            self.burst(p.pos, CYAN, 14, 200)

    # ---------- lógica ----------
    def hurt(self, dmg):
        p = self.player
        if p.inv > 0:
            return
        if p.shield > 0:
            p.shield = 0
            p.inv = 0.6
            self.burst(p.pos, BLUE, 25, 300)
            self.shake = max(self.shake, 8)
            return
        p.hp -= dmg
        p.inv = 0.6
        self.shake = max(self.shake, 14)
        self.burst(p.pos, RED, 16)
        if p.hp <= 0:
            self.burst(p.pos, CYAN, 80, 450, 4)
            self.state = "gameover"
            if self.score > self.record:
                self.record = self.score
                self.save_record()

    def kill(self, e):
        self.burst(e.pos, e.color, 30 if e.kind != "boss" else 150, 320 if e.kind != "boss" else 600, 4)
        self.combo_t = 2.0
        self.combo = min(5, self.combo + 1)
        self.score += e.score * self.combo
        self.shake = max(self.shake, 6 if e.kind != "boss" else 25)
        if random.random() < (0.14 if e.kind != "boss" else 1.0):
            self.powerups.append(PowerUp(e.pos, random.choice(list(POWERUPS))))

    def shoot(self, aim):
        p = self.player
        base = math.atan2(aim.y - p.pos.y, aim.x - p.pos.x)
        angles = (-0.2, 0, 0.2) if p.triple > 0 else (0,)
        for off in angles:
            a = base + off
            self.bullets.append(Bullet(p.pos + V(math.cos(a), math.sin(a)) * 18,
                                       V(math.cos(a), math.sin(a)) * 820, 10, True, CYAN))
        p.fire_cd = 0.075 if p.rapid > 0 else 0.17

    def update(self, dt):
        p = self.player
        mv, aim, fire = self.read_input()
        p.angle = math.atan2(aim.y - p.pos.y, aim.x - p.pos.x)

        # movimiento
        if p.dash_t > 0:
            p.dash_t -= dt
            p.vel = p.dash_dir * 900
            if random.random() < 0.8:
                self.particles.append(Particle(p.pos, (0, 0), 0.3, CYAN, 4))
        else:
            if mv.length():
                p.vel += mv.normalize() * 2400 * dt
            p.vel *= max(0.0, 1 - 7 * dt)
            if p.vel.length() > 340:
                p.vel.scale_to_length(340)
        p.pos += p.vel * dt
        p.pos.x = max(p.r, min(W - p.r, p.pos.x))
        p.pos.y = max(p.r, min(H - p.r, p.pos.y))

        for attr in ("inv", "dash_cd", "rapid", "triple", "shield", "fire_cd"):
            setattr(p, attr, max(0.0, getattr(p, attr) - dt))
        if fire and p.fire_cd <= 0:
            self.shoot(aim)

        # combo
        if self.combo_t > 0:
            self.combo_t -= dt
            if self.combo_t <= 0:
                self.combo = 1

        # oleadas
        self.banner_t = max(0, self.banner_t - dt)
        if self.queue:
            self.spawn_t -= dt
            if self.spawn_t <= 0:
                self.spawn_enemy(self.queue.pop())
                self.spawn_t = max(0.25, 0.8 - self.wave * 0.03)
        elif not self.enemies:
            self.wave_delay -= dt
            if self.wave_delay <= 0:
                self.wave_delay = 2.0
                p.hp = min(p.max_hp, p.hp + 10)
                self.start_wave()

        # enemigos
        for e in self.enemies:
            e.update(dt, self)
        for i, a in enumerate(self.enemies):
            for b in self.enemies[i + 1:]:
                d = a.pos - b.pos
                dist = d.length()
                lim = (a.r + b.r) * 0.9
                if 0 < dist < lim:
                    push = d / dist * (lim - dist) * 0.5
                    a.pos += push
                    b.pos -= push
        for e in self.enemies:
            if (e.pos - p.pos).length() < e.r + p.r:
                self.hurt(e.dmg)
                if e.kind != "boss":
                    e.hp = 0
                    e.flash = 0.1

        # balas
        for b in self.bullets:
            b.update(dt)
            if b.friendly:
                for e in self.enemies:
                    if e.hp > 0 and (e.pos - b.pos).length() < e.r + b.r:
                        e.hp -= b.dmg
                        e.flash = 0.06
                        b.life = 0
                        self.burst(b.pos, b.color, 4, 150, 2)
                        break
            elif (b.pos - p.pos).length() < p.r + b.r:
                b.life = 0
                self.hurt(b.dmg)
        for e in [e for e in self.enemies if e.hp <= 0]:
            self.kill(e)
        self.enemies = [e for e in self.enemies if e.hp > 0]
        self.bullets = [b for b in self.bullets
                        if b.life > 0 and -50 < b.pos.x < W + 50 and -50 < b.pos.y < H + 50]

        # power-ups
        for pu in self.powerups:
            pu.update(dt)
            if (pu.pos - p.pos).length() < 26:
                pu.life = 0
                if pu.kind == "heal":
                    p.hp = min(p.max_hp, p.hp + 35)
                elif pu.kind == "rapid":
                    p.rapid = 10
                elif pu.kind == "triple":
                    p.triple = 10
                elif pu.kind == "shield":
                    p.shield = 15
                self.burst(pu.pos, POWERUPS[pu.kind][0], 20)
        self.powerups = [pu for pu in self.powerups if pu.life > 0]

        # partículas y fondo
        for pt in self.particles:
            pt.update(dt)
        self.particles = [pt for pt in self.particles if pt.life > 0]
        self.shake = max(0, self.shake - 40 * dt)

    # ---------- dibujo ----------
    def draw_world(self, s):
        s.fill(BG)
        for st in self.stars:
            c = 40 + int(st[2])
            pygame.draw.circle(s, (c, c, c + 30), (st[0], st[1]), st[3])

        for pu in self.powerups:
            col, ch = POWERUPS[pu.kind]
            if pu.life < 2 and int(pu.life * 8) % 2:
                continue
            y = pu.pos.y + math.sin(pu.t * 4) * 4
            glow(s, col, (pu.pos.x, y), 30, 70)
            pygame.draw.circle(s, col, (pu.pos.x, y), 14, 2)
            self.text(s, self.f_small, ch, col, (pu.pos.x, y), True)

        for e in self.enemies:
            e.draw(s)

        for b in self.bullets:
            tail = b.pos - b.vel.normalize() * (b.r * 3)
            pygame.draw.line(s, b.color, tail, b.pos, max(2, int(b.r)))
            glow(s, b.color, b.pos, int(b.r * 3), 60)

        for pt in self.particles:
            a = pt.life / pt.max
            col = tuple(int(c * a) for c in pt.color)
            pygame.draw.circle(s, col, pt.pos, max(1, pt.size * a))

        p = self.player
        if self.state != "gameover" and not (p.inv > 0 and int(p.inv * 20) % 2):
            glow(s, CYAN, p.pos, 36, 55)
            poly(s, CYAN, p.pos, p.r + 3, 3, p.angle)
            poly(s, BG, p.pos, p.r - 3, 3, p.angle)
            if p.shield > 0:
                pygame.draw.circle(s, BLUE, p.pos, 24, 2)

    def draw_hud(self, s):
        p = self.player
        pygame.draw.rect(s, (35, 35, 55), (20, 20, 220, 14), border_radius=4)
        pygame.draw.rect(s, GREEN if p.hp > 35 else RED,
                         (20, 20, 220 * max(0, p.hp) / p.max_hp, 14), border_radius=4)
        pygame.draw.rect(s, (35, 35, 55), (20, 40, 220, 6), border_radius=3)
        pygame.draw.rect(s, CYAN if p.dash_cd <= 0 else (60, 100, 120),
                         (20, 40, 220 * (1 - p.dash_cd / 1.2), 6), border_radius=3)

        img = self.f_mid.render(f"{self.score:,}", True, WHITE)
        s.blit(img, (W - 20 - img.get_width(), 16))
        img = self.f_small.render(f"RÉCORD {max(self.record, self.score):,}", True, (140, 150, 190))
        s.blit(img, (W - 20 - img.get_width(), 52))
        self.text(s, self.f_small, f"OLEADA {self.wave}", (140, 150, 190), (W // 2, 24), True)
        if self.combo > 1:
            self.text(s, self.f_mid, f"x{self.combo}", YELLOW, (W // 2, 56), True)

        x = 20
        for name, val, col in (("RÁPIDO", p.rapid, YELLOW), ("TRIPLE", p.triple, CYAN), ("ESCUDO", p.shield, BLUE)):
            if val > 0:
                self.text(s, self.f_small, f"{name} {val:0.0f}s", col, (x, H - 34))
                x += 150

        if self.banner_t > 0:
            self.text(s, self.f_big, self.banner, WHITE, (W // 2, H // 2 - 100), True)

    def overlay(self, title, lines, color=WHITE):
        dim = pygame.Surface((W, H), pygame.SRCALPHA)
        dim.fill((0, 0, 10, 170))
        self.screen.blit(dim, (0, 0))
        self.text(self.screen, self.f_big, title, color, (W // 2, H // 2 - 90), True)
        for i, ln in enumerate(lines):
            self.text(self.screen, self.f_mid, ln, WHITE, (W // 2, H // 2 + 10 + i * 40), True)

    def draw(self):
        self.draw_world(self.canvas)
        off = (random.uniform(-self.shake, self.shake), random.uniform(-self.shake, self.shake)) if self.shake else (0, 0)
        self.screen.fill(BG)
        self.screen.blit(self.canvas, off)
        if self.state != "menu":
            self.draw_hud(self.screen)
        if self.state == "menu":
            self.overlay("NEON VOID", ["Clic o ENTER para empezar", "",
                                       f"Récord: {self.record:,}"], CYAN)
        elif self.state == "paused":
            self.overlay("PAUSA", ["P o ESC para continuar"])
        elif self.state == "gameover":
            self.overlay("GAME OVER", [f"Puntos: {self.score:,}   Oleada: {self.wave}",
                                       "¡NUEVO RÉCORD!" if self.score >= self.record and self.score > 0 else
                                       f"Récord: {self.record:,}",
                                       "R para reiniciar"], RED)
        pygame.display.flip()

    # ---------- bucle principal ----------
    def run(self):
        while True:
            dt = min(self.clock.tick(FPS) / 1000, 0.05)
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if ev.type == pygame.KEYDOWN:
                    if self.state == "menu" and ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.reset()
                        self.state = "playing"
                    elif self.state == "playing":
                        if ev.key == pygame.K_SPACE:
                            self.dash()
                        elif ev.key in (pygame.K_p, pygame.K_ESCAPE):
                            self.state = "paused"
                    elif self.state == "paused" and ev.key in (pygame.K_p, pygame.K_ESCAPE):
                        self.state = "playing"
                    elif self.state == "gameover" and ev.key == pygame.K_r:
                        self.reset()
                        self.state = "playing"
                if ev.type == pygame.MOUSEBUTTONDOWN and self.state == "menu":
                    self.reset()
                    self.state = "playing"

            for st in self.stars:
                st[1] += st[2] * dt
                if st[1] > H:
                    st[0], st[1] = random.uniform(0, W), 0
            if self.state == "playing":
                self.update(dt)
            elif self.state == "gameover":
                for pt in self.particles:
                    pt.update(dt)
                self.particles = [pt for pt in self.particles if pt.life > 0]
                self.shake = max(0, self.shake - 40 * dt)
            self.draw()


if __name__ == "__main__":
    Game().run()
