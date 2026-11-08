import random
from spawn import spawn

C, N = 5, 12                  # チャンク数、チャンク内のマス数
GAP_W = 4                     # 出入口の幅（マス）
DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))
HOUSE = (200, 90, 70)
TREE, FOREST, LAKE = 'tree', 'forest', 'lake'   # wallsの値に色の代わりに入れる目印（FORESTは外周の森）
BLOCK_COLORS = ((150, 150, 160), (170, 120, 70))


def make_maze():
    opened = {(i, j): {} for i in range(C) for j in range(C)}
    cur = random.choice(list(opened))
    seen, stack = {cur}, [cur]
    while stack:
        x, y = stack[-1]
        nb = [(a, b) for a, b in DIRS if (x + a, y + b) in opened and (x + a, y + b) not in seen]
        if not nb:
            stack.pop()
            continue
        a, b = random.choice(nb)
        g = random.randint(1, N - 5)   # 出入口の位置（隣と同じ値にして繋ぐ）
        opened[(x, y)][(a, b)] = g
        opened[(x + a, y + b)][(-a, -b)] = g
        seen.add((x + a, y + b))
        stack.append((x + a, y + b))
    return opened


def make_walls(opened, rim):
    w = {}
    for k in range(N):
        for tile, d in (((0, k), (-1, 0)), ((N - 1, k), (1, 0)), ((k, 0), (0, -1)), ((k, N - 1), (0, 1))):
            if not (d in opened and opened[d] <= k < opened[d] + GAP_W):
                w[tile] = rim
    return w

def connected(w, opened, keep):
    ends = [(0 if d[0] < 0 else N - 1 if d[0] > 0 else k, 0 if d[1] < 0 else N - 1 if d[1] > 0 else k)
            for d, g in opened.items() for k in range(g, g + GAP_W)]
    targets = ends + list(keep)
    seen, stack = {targets[0]}, [targets[0]]
    while stack:
        x, y = stack.pop()
        for a, b in DIRS:
            t = (x + a, y + b)
            if 0 <= t[0] < N and 0 <= t[1] < N and t not in w and t not in seen:
                seen.add(t)
                stack.append(t)
    return all(t in seen for t in targets)


def decorate(walls, opened, keep):
    """内側に木の列・木・湖を置く。出入口やkeepが繋がらなければやり直し"""
    for _ in range(20):
        w = dict(walls)
        for _ in range(random.randint(5, 10)):   # 木の列を置く（繋がりが切れる場合は取り消し）
            x, y = random.randint(1, N - 2), random.randint(1, N - 2)
            a, b = random.choice(((1, 0), (0, 1)))
            seg = [(x + a * i, y + b * i) for i in range(random.randint(3, 6))]
            seg = [t for t in seg if 1 <= t[0] <= N - 2 and 1 <= t[1] <= N - 2 and t not in w and t not in keep]
            old = dict(w)
            w.update({t: TREE for t in seg})
            if not connected(w, opened, keep):
                w = old
        for _ in range(random.randint(0, 6)):
            w[(random.randint(1, N - 2), random.randint(1, N - 2))] = TREE
        if random.random() < 0.5:
            for _ in range(random.randint(1, 2)):   # 長方形を重ねて湖にする
                x, y = random.randint(2, N - 5), random.randint(2, N - 5)
                for i in range(x, x + random.randint(2, 4)):
                    for j in range(y, y + random.randint(2, 4)):
                        w[(i, j)] = LAKE
        if not any(t in w for t in keep) and connected(w, opened, keep):
            return w
    return walls

def generate():
    maze = make_maze()
    cells = list(maze)
    start = random.choice(cells)
    goal = random.choice([c for c in cells if abs(c[0] - start[0]) + abs(c[1] - start[1]) >= 4])
    chunks = {}
    for c in cells:
        blocks = {(random.randint(2, N - 3), random.randint(2, N - 3)): random.choice(BLOCK_COLORS)
                  for _ in range(random.randint(0, 3))}
        walls = make_walls(maze[c], FOREST)   # 周囲は森
        keep = {(i, j) for i in range(4, 9) for j in range(4, 9)} if c in (start, goal) else set()
        walls = decorate(walls, maze[c], keep)
        blocks = {t: col for t, col in blocks.items() if t not in walls}
        if c == start:
            house = [(i, j) for i in (5, 6) for j in (5, 6)]
            for t in house + [(7, 5)]:
                blocks.pop(t, None)
            walls.update({t: HOUSE for t in house})
        if c == goal:
            blocks.pop((6, 6), None)
        chunks[c] = {'blocks': blocks, 'walls': walls, 'open': maze[c], 'goal': c == goal,
                     'enemies': [] if c == start else spawn(N)}
    return chunks, start, goal