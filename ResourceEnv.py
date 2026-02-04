import numpy as np
import random
from enemy import Enemy
class ResourceEnvFromGrid:
    def __init__(self,
                mother,
                max_steps=50,
                death_penalty=-2.0
                ):
        self.grid = mother.grid
        self.mother = mother
        self.max_steps = max_steps
        self.death_penalty = death_penalty
        self.reset()

    def reset(self):
        self.mother.reset()
        self.player = [0, 0]
        self.base = [0, 0]
        self.inv_gold = 0
        self.inv_food = 0
        self.steps = 0

        self.targets = self.mother.gold
        self.target = random.choice(self.targets)
        self.target_collected = False

        return self._obs()

    def _obs(self):
        tx, ty = self.target
        ex0, ey0 = self.mother.enemies[0].pos
        ex1, ey1 = self.mother.enemies[1].pos
        ex2, ey2 = self.mother.enemies[2].pos
        return np.array(
            [
            self.player[0] / self.grid,
            self.player[1] / self.grid,
            tx / self.grid,
            ty / self.grid,
            ex0 / self.grid,
            ey0 / self.grid,
            ex1 / self.grid,
            ey1 / self.grid,
            ex2 / self.grid,
            ey2 / self.grid,
            self.inv_gold,
        
            ]
            , dtype=np.float32)

    def step(self, action):
        self.steps += 1
        reward = 0#-0.01
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

        # Collect target
        if self.player == self.target and self.target_collected == False:
            self.inv_gold += 1
            reward += 4.0
            self.mother.gold.remove(self.target)
            self.target_collected = True
        # Return to base the base with the target
        if self.player == self.base and self.inv_gold > 0:
            reward += 1.0 * self.inv_gold
            done = True

        if self.steps >= self.max_steps:
            done = True

        return self._obs(), reward, done

