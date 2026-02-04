import random
import numpy as np
from enemy import Enemy
class PlantWaterEnvFromGrid:
    def __init__(
        self,
        mother,
        max_steps=50,
        grow_time=3,
        death_penalty=-10.0
    ):
        self.grid = mother.grid
        self.mother = mother
        self.max_steps = max_steps
        self.grow_time = grow_time
        self.death_penalty = death_penalty
        self.reset()

    def reset(self):
        self.mother.reset()
        self.player = [0, 0]
        self.carry_water = 0
        self.steps = 0
        self.grow_timer = 0

        self.water_source = random.choice(self.mother.water)
        self.target_plant = random.choice(self.mother.plants)

        return self._obs()

    def _obs(self):
        ex, ey = self.mother.enemies[0].pos
        return np.array([
            self.player[0] / self.grid,
            self.player[1] / self.grid,
            self.water_source[0] / self.grid,
            self.water_source[1] / self.grid,
            self.target_plant[0] / self.grid,
            self.target_plant[1] / self.grid,
            ex / self.grid,
            ey / self.grid,
            float(self.carry_water),
            float(self.mother.plant_watered[tuple(self.target_plant)]),
            #(self.max_steps - self.steps) / self.max_steps
        ], dtype=np.float32)

    def step(self, action):
        self.steps += 1
        reward = -0.01
        done = False

        # Agent move
        dx, dy = [(0,-1),(0,1),(-1,0),(1,0),(0,0)][action]
        self.player[0] = np.clip(self.player[0] + dx, 0, self.grid - 1)
        self.player[1] = np.clip(self.player[1] + dy, 0, self.grid - 1)

        # Enemy move
        self.mother.step_enemies()

        # Death check
        if self.mother.agent_dead(self.player):
            return self._obs(), self.death_penalty, True

        # Collect water
        if self.player == self.water_source and self.carry_water == 0:
            self.carry_water = 1
            reward += 5.0

        # Water plant
        if self.player == self.target_plant and self.carry_water == 1:
            self.carry_water = 0
            self.mother.water_plant(self.target_plant)
            reward += 5.0

        # Growth
        if self.mother.plant_watered[tuple(self.target_plant)]:
            self.grow_timer += 1
            if self.grow_timer >= self.grow_time:
                reward += 10.0
                done = True

        if self.steps >= self.max_steps:
            done = True

        return self._obs(), reward, done

