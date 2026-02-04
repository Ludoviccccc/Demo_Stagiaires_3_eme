import pygame
import time
import numpy as np
#from exploit import ActorNumpy

# ----------------------------
# MotherGrid Visualization (with Enemies) - Numpy Version
# ----------------------------
def visualize_mother_grid_numpy(env, actor_numpy, npz_path=None, delay=0.25, cell_size=80):
    pygame.init()

    grid = env.grid
    width = height = grid * cell_size
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("MotherGrid Policy Visualization (Enemies) - Numpy")

    font = pygame.font.SysFont(None, 24)
    clock = pygame.time.Clock()

    # Load numpy actor if npz_path is provided
    actor = actor_numpy

    state = env.reset()
    done = False
    dead = False

    # ---------- Drawing helpers ----------
    def draw_grid():
        for x in range(grid):
            for y in range(grid):
                pygame.draw.rect(
                    screen,
                    (220, 220, 220),
                    pygame.Rect(
                        x * cell_size,
                        y * cell_size,
                        cell_size,
                        cell_size
                    ),
                    1
                )

    def draw_resources():
        # Gold
        for gx, gy in env.mother.gold:
            pygame.draw.circle(
                screen, (255, 200, 0),
                (gx * cell_size + cell_size // 2,
                 gy * cell_size + cell_size // 2),
                cell_size // 4
            )

        # Water
        for wx, wy in env.mother.water:
            pygame.draw.rect(
                screen, (0, 180, 255),
                (wx * cell_size + 12,
                 wy * cell_size + 12,
                 cell_size - 24,
                 cell_size - 24)
            )

        # Plants
        for (px, py), watered in env.mother.plant_watered.items():
            color = (0, 130, 0) if watered else (0, 200, 0)
            pygame.draw.rect(
                screen, color,
                (px * cell_size + 15,
                 py * cell_size + 15,
                 cell_size - 30,
                 cell_size - 30)
            )

    def draw_enemies():
        for enemy in env.mother.enemies:
            ex, ey = enemy.pos
            cx = ex * cell_size + cell_size // 2
            cy = ey * cell_size + cell_size // 2

            # Red circle
            pygame.draw.circle(screen, (200, 40, 40), (cx, cy), cell_size // 3)

            # Cross
            pygame.draw.line(screen, (0, 0, 0),
                             (cx - 10, cy - 10), (cx + 10, cy + 10), 3)
            pygame.draw.line(screen, (0, 0, 0),
                             (cx + 10, cy - 10), (cx - 10, cy + 10), 3)

    def draw_agent():
        ax, ay = env.player
        color = (90, 90, 90) if dead else (70, 120, 255)

        pygame.draw.circle(
            screen, color,
            (ax * cell_size + cell_size // 2,
             ay * cell_size + cell_size // 2),
            cell_size // 3
        )

    def draw_target():
        target = None
        if hasattr(env, "target"):
            target = env.target
        elif hasattr(env, "target_plant"):
            target = env.target_plant

        if target:
            tx, ty = target
            pygame.draw.rect(
                screen, (255, 50, 50),
                (tx * cell_size + 6,
                 ty * cell_size + 6,
                 cell_size - 12,
                 cell_size - 12),
                3
            )

    def draw_hud():
        hud = []

        if hasattr(env, "inv_gold"):
            hud.append(f"Gold: {env.inv_gold}")
            hud.append(f"Food: {env.inv_food}")

        if hasattr(env, "carry_water"):
            hud.append(f"Water carried: {env.carry_water}")

        if hasattr(env, "grow_timer"):
            hud.append(f"Growth: {env.grow_timer}/{env.grow_time}")

        hud.append(f"Steps: {env.steps}/{env.max_steps}")

        for i, txt in enumerate(hud):
            surf = font.render(txt, True, (0, 0, 0))
            screen.blit(surf, (5, 5 + i * 20))

    # ---------- Main loop ----------
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        # Convert state to numpy array with proper shape
        state_np = np.array(state, dtype=np.float32).reshape(1, -1)  # shape: (1, state_dim)
        
        # Get action probabilities using numpy actor
        probs = actor.forward(state_np)
        action = np.argmax(probs[0])  # Get action from first (and only) batch element

        state, reward, done = env.step(action)

        if env.mother.agent_dead(env.player):
            dead = True

        screen.fill((245, 245, 245))
        draw_grid()
        draw_resources()
        draw_target()
        draw_enemies()
        draw_agent()
        draw_hud()

        pygame.display.flip()
        clock.tick(1 / delay)

    # ---------- End state ----------
    if dead:
        text = font.render("AGENT DIED", True, (180, 0, 0))
    else:
        text = font.render("EPISODE COMPLETE", True, (0, 120, 0))

    screen.blit(text, (width // 2 - 80, height // 2 - 10))
    pygame.display.flip()
    time.sleep(2)
    pygame.quit()

