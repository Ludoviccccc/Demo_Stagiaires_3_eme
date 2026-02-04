import random
import numpy as np

class Enemy:
    def __init__(self, pos):
        self.pos = pos

    def step(self, grid_size):
        dx, dy = random.choice([(0,1),(0,-1),(1,0),(-1,0),(0,0)])
        self.pos[0] = np.clip(self.pos[0] + dx, 0, grid_size - 1)
        self.pos[1] = np.clip(self.pos[1] + dy, 0, grid_size - 1)

