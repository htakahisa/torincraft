import math

BROWN, GUARD, BLADE = (110, 70, 40), (150, 100, 55), (205, 165, 105)


class Item:
    """手持ちアイテムの基底クラス。新しいアイテムはこれを継承する"""
    def use(self): pass
    def update(self, dt): pass
    def hit(self, x, y, fh, fv, targets): pass
    def draw(self, s, box, x, y, z, fh, fv, back): pass


class SwordBranch(Item):
    DUR = 0.25   # 振りの長さ（秒）
    DMG = 1      # 1回の攻撃のダメージ（ハート1つ分）

    def __init__(self):
        self.using, self.t = False, 0.0
        self.done = set()   # 今回の振りで当たった敵（多段ヒット防止）

    def use(self):
        if not self.using:
            self.using, self.t = True, 0.0
            self.done = set()

    def hit(self, x, y, fh, fv, targets):
        if not self.using: return
        fx, fy = (fh + fv) / 2, (fv - fh) / 2
        rx, ry = -fy, fx
        c = math.cos(self.angle())
        f = 0.4 + 0.8 * math.sin(math.pi * self.t / self.DUR)
        hx, hy = x + rx * 0.6, y + ry * 0.6
        for e in targets:
            if e in self.done: continue
            for i in range(10):   # 柄〜刃先までの判定点
                r = 0.3 + i * 0.12
                bx = hx + (c * rx + f * fx) * r
                by = hy + (c * ry + f * fy) * r
                if math.hypot(e.x - bx, e.y - by) < 0.5:
                    e.knock(e.x - x, e.y - y, dmg=self.DMG)
                    self.done.add(e)
                    break

    def update(self, dt):
        if self.using:
            self.t += dt
            if self.t >= self.DUR:
                self.using = False

    def angle(self):
        k = self.t / self.DUR if self.using else 0
        return math.radians(45 + 180 * k)   # 右上(45°)→真上→左下(225°)

    def draw(self, s, box, x, y, z, fh, fv, back):
        fx, fy = (fh + fv) / 2, (fv - fh) / 2   # キャラが向いているワールド方向
        rx, ry = -fy, fx                        # キャラの右手側
        a = self.angle()
        c, sn = math.cos(a), math.sin(a)
        f = 0.4 + 0.8 * math.sin(math.pi * (self.t / self.DUR if self.using else 0))   # 振りの中間で最も前に出る
        hx, hy = x + rx * 0.6, y + ry * 0.6     # 右手の位置（頭の外側）
        mx = hx + (c * rx + f * fx) * 0.8
        my = hy + (c * ry + f * fy) * 0.8
        if (mx + my > x + y) == back: return
        for r, w, col in [(0.0, 0.12, BROWN), (0.15, 0.2, GUARD)] + [(0.3 + i * 0.12, 0.12, BLADE) for i in range(8)]:
            bx = hx + (c * rx + f * fx) * r   # 右 → 左へ横切りつつ、前方に膨らむ
            by = hy + (c * ry + f * fy) * r
            bz = z + sn * r
            box(s, bx - w / 2, by - w / 2, bz - w / 2, w, w, w, col)