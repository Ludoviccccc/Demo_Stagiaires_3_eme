import numpy as np
import random
from enemy import Enemy
class MotherGrid:
    def __init__(
        self,
        grid=6,
        n_gold=2,
        n_water=2,
        n_plants=2,
        n_enemies=1
    ):
        self.grid = grid
        self.n_gold = n_gold
        self.n_water = n_water
        self.n_plants = n_plants
        self.n_enemies = n_enemies
        self.reset()

    def reset(self):
        self.gold = self._spawn(self.n_gold)
        self.water = self._spawn(self.n_water, exclude=self.gold)
        self.plants = self._spawn(self.n_plants, exclude=self.gold + self.water)

        self.plant_watered = {tuple(p): False for p in self.plants}

        enemy_positions = self._spawn(
            self.n_enemies,
            exclude=self.gold + self.water + self.plants
        )
        self.enemies = [Enemy(p) for p in enemy_positions]

    def _spawn(self, n, exclude=None):
        exclude = exclude or []
        positions = []
        while len(positions) < n:
            p = [random.randint(0, self.grid - 1),
                 random.randint(0, self.grid - 1)]
            if p not in positions and p not in exclude:
                positions.append(p)
        return positions

    def step_enemies(self):
        for enemy in self.enemies:
            enemy.step(self.grid)

    def agent_dead(self, agent_pos):
        for enemy in self.enemies:
            if enemy.pos == agent_pos:
                return True
        return False

    def water_plant(self, pos):
        key = tuple(pos)
        if key in self.plant_watered:
            self.plant_watered[key] = True
            return True
        return False

