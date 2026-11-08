import math
import effects
from collections import deque

def next_waypoint(sx, sy, tx, ty, solid, n):
    start, goal = (int(sx), int(sy)), (int(tx), int(ty))
    if start == goal:
        return tx, ty
    dirs = ((1, 0), (-1, 0), (0, 1), (0, -1))
    if goal in solid:   # 相手がブロックの上にいるときは、その隣のマスを目標にする
        goals = {(goal[0] + a, goal[1] + b) for a, b in dirs} - set(solid)
    else:
        goals = {goal}
    prev = {start: None}
    q = deque([start])
    end = None
    while q:
        c = q.popleft()
        if c in goals:
            end = c
            break
        for a, b in dirs:
            nx, ny = c[0] + a, c[1] + b
            if 0 <= nx < n and 0 <= ny < n and (nx, ny) not in solid and (nx, ny) not in prev:
                prev[(nx, ny)] = c
                q.append((nx, ny))
    if end is None or end == start:
        return None
    c = end
    while prev[c] != start:
        c = prev[c]
    return c[0] + 0.5, c[1] + 0.5

class Ghost:
    speed = 1.0
    CLIMB = 1.5   # 上昇・下降速度（高さ/秒）

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.z = 0.0   # 現在の高さ
        self.kx = self.ky = 0.0   # ノックバック速度
        self.flash = 0.0          # 赤点滅の残り時間
        self.hp = 2               # 体力（ハート2つ）
        self.cool = 0.0           # 攻撃クールダウン

    def knock(self, dx, dy, power=6.0, dmg=1):
        d = math.hypot(dx, dy) or 1
        self.kx, self.ky = dx / d * power, dy / d * power
        self.flash = 0.4
        self.hp -= dmg
        effects.spawn_hearts(self.x, self.y, dmg)

    def update(self, dt, px, py, solid, n):
        self.flash = max(0.0, self.flash - dt)
        self.cool = max(0.0, self.cool - dt)
        nx, ny = self.x + self.kx * dt, self.y + self.ky * dt
        if 0 <= nx < n and 0 <= ny < n and (int(nx), int(ny)) not in solid:
            self.x, self.y = nx, ny
        else:
            self.kx = self.ky = 0.0
        f = max(0.0, 1 - 8 * dt)   # 減衰
        self.kx *= f
        self.ky *= f
        gh = lambda x, y: 1.0 if (int(x), int(y)) in solid else 0.0
        near = math.hypot(px - self.x, py - self.y) <= 0.8
        w = None if near else next_waypoint(self.x, self.y, px, py, (), n)   # ブロックを障害物にしない
        want = gh(*w) if w else gh(self.x, self.y)   # 次のマスの高さへ
        self.z += max(-self.CLIMB * dt, min(self.CLIMB * dt, want - self.z))   # 高さの更新はここだけ
        if near:
            if self.cool <= 0:
                self.cool = 1.0
                return True   # 攻撃した
            return
        if w is None or self.z < want - 0.01:
            return   # 登り終わるまでその場で待つ
        dx, dy = w[0] - self.x, w[1] - self.y
        dd = math.hypot(dx, dy)
        if dd > 0:
            step = min(self.speed * dt, dd)
            self.x += dx / dd * step
            self.y += dy / dd * step

    def draw(self, s, t, box, P):
        import pygame
        x, y = self.x, self.y
        z = self.z + 0.3 + 0.1 * math.sin(t * 3)
        sx, sy = P(x, y, self.z)
        pygame.draw.ellipse(s, (60, 100, 50), (sx - 16, sy - 6, 32, 12))
        W, K = (245, 245, 250), (30, 30, 40)
        if self.flash > 0:
            W = (235, 60, 60)   # ダメージ中は赤
        z += 0.2
        wig = 0.08 * math.sin(t * 6)
        for i, (fx, fy) in enumerate(((-0.35, -0.35), (0.15, -0.35), (-0.35, 0.15), (0.15, 0.15))):
            d = wig if i % 2 == 0 else -wig
            box(s, x+fx, y+fy, z-0.2+d, 0.2, 0.2, 0.4, W)   # 足
        box(s, x-0.4, y-0.4, z+0.2, 0.8, 0.8, 1.0, W)         # 胴体
        box(s, x-0.22, y+0.4, z+0.85, 0.14, 0.02, 0.22, K)    # 目（左下向きの面）
        box(s, x+0.08, y+0.4, z+0.85, 0.14, 0.02, 0.22, K)
        box(s, x+0.4, y-0.22, z+0.85, 0.02, 0.14, 0.22, K)    # 目（右下向きの面）
        box(s, x+0.4, y+0.08, z+0.85, 0.02, 0.14, 0.22, K)
