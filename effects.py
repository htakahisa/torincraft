import pygame

hearts = []   # [x, y, z, 残り寿命]

def spawn_hearts(x, y, dmg, color=(255, 80, 110), z0=0.0):
    offs = {1: (0.0,), 2: (-0.15, 0.15), 3: (-0.25, 0.0, 0.25)}.get(dmg, (-0.25, 0.0, 0.25))
    for i, o in enumerate(offs):   # ダメージ分のハートを横に等間隔で
        hearts.append([x + o, y - o, z0 + 1.6 + i % 2 * 0.3, 0.8 - i * 0.1, color])

def update(dt):
    hearts[:] = [[x, y, z + 1.0 * dt, l - dt, c] for x, y, z, l, c in hearts if l - dt > 0]

def heart(s, cx, cy, c):
    pygame.draw.circle(s, c, (cx - 4, cy), 5)
    pygame.draw.circle(s, c, (cx + 4, cy), 5)
    pygame.draw.polygon(s, c, [(cx - 9, cy + 1), (cx + 9, cy + 1), (cx, cy + 11)])

def draw(s, P):
    for hx, hy, hz, _, c in hearts:
        cx, cy = (int(v) for v in P(hx, hy, hz))
        heart(s, cx, cy, c)