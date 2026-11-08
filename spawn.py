import random
from ghost import Ghost

def spawn(n):
    return [Ghost(random.uniform(2, n - 2), random.uniform(2, n - 2)) for _ in range(random.randint(1, 2))]