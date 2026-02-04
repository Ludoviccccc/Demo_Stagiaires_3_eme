import pygame
import random
import sys

# --------------------
# CONFIG
# --------------------
OBJECTIVES = ["gold", "food", "plants", "mixed"]
LOG_FILE = "game_results.txt"

TILE_SIZE = 48
GRID_WIDTH = 10
GRID_HEIGHT = 10
WINDOW_WIDTH = GRID_WIDTH * TILE_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * TILE_SIZE

MAX_INVENTORY = 5
MAX_STEPS = 200
PLANT_GROW_TIME = 18

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (70, 130, 180)
CYAN = (80, 200, 220)
GREEN = (60, 200, 60)
DARK_GREEN = (30, 160, 30)
YELLOW = (240, 220, 70)
RED = (200, 50, 50)
BROWN = (160, 120, 80)
PURPLE = (160, 80, 200)
GRAY = (200, 200, 200)

print("Choose an objective for this game:")
for i, obj in enumerate(OBJECTIVES):
    print(f"{i}: {obj}")

choice = input("Enter objective number: ")

try:
    choice = int(choice)
    GAME_OBJECTIVE = OBJECTIVES[choice]
except:
    GAME_OBJECTIVE = "mixed"

print(f"Selected objective: {GAME_OBJECTIVE}")


# --------------------
# INIT
# --------------------
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Multi-Objective Game – Water Transport")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# --------------------
# GAME STATE
# --------------------
player = {"x": 1, "y": 1, "gold": 0, "food": 0, "water": 0}
base = {"x": 0, "y": 0}
exit_door = {"x": GRID_WIDTH - 1, "y": GRID_HEIGHT - 1}

resources = []
plants = []
water_sources = []
enemies = []

score_gold = 0
score_food = 0
grown_plants = 0
steps = 0

# --------------------
# HELPERS
# --------------------
def random_position():
    return random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)

def spawn_resource():
    x, y = random_position()
    return {"x": x, "y": y, "type": random.choice(["gold", "food"])}

def spawn_plant():
    x, y = random_position()
    return {"x": x, "y": y, "watered": False, "timer": 0}

def spawn_enemy():
    x, y = random_position()
    return {"x": x, "y": y}

def spawn_water():
    x, y = random_position()
    return {"x": x, "y": y}

def move_randomly(entity):
    dx, dy = random.choice([(1,0), (-1,0), (0,1), (0,-1), (0,0)])
    nx, ny = entity["x"] + dx, entity["y"] + dy
    if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
        entity["x"], entity["y"] = nx, ny

def draw_tile(x, y, color):
    pygame.draw.rect(
        screen, color,
        (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    )

def draw_text(text, x, y):
    screen.blit(font.render(text, True, BLACK), (x, y))

def inventory_size():
    return player["gold"] + player["food"] + player["water"]

# --------------------
# INITIAL SPAWN
# --------------------
for _ in range(3):
    resources.append(spawn_resource())

for _ in range(4):
    plants.append(spawn_plant())

for _ in range(2):
    water_sources.append(spawn_water())

for _ in range(2):
    enemies.append(spawn_enemy())

# --------------------
# MAIN LOOP
# --------------------
running = True
reason = ""

while running:
    clock.tick(10)
    screen.fill(GRAY)

    # EVENTS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    dx, dy = 0, 0
    if keys[pygame.K_UP]:
        dy = -1
    elif keys[pygame.K_DOWN]:
        dy = 1
    elif keys[pygame.K_LEFT]:
        dx = -1
    elif keys[pygame.K_RIGHT]:
        dx = 1
    elif keys[pygame.K_ESCAPE]:
        pygame.quit()
        sys.exit()

    # MOVE PLAYER
    if dx or dy:
        nx, ny = player["x"] + dx, player["y"] + dy
        if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
            player["x"], player["y"] = nx, ny
            steps += 1

    # STEP LIMIT
    if steps >= MAX_STEPS:
        running = False
        reason = "Out of steps"

    # MOVE ENEMIES
    for e in enemies:
        move_randomly(e)

    # WATER COLLECTION
    for w in water_sources:
        if w["x"] == player["x"] and w["y"] == player["y"]:
            if inventory_size() < MAX_INVENTORY:
                player["water"] += 1

    # WATER PLANTS
    for p in plants:
        if (p["x"] == player["x"] and p["y"] == player["y"]
                and not p["watered"] and player["water"] > 0):
            player["water"] -= 1
            p["watered"] = True

    # GROW PLANTS
    for p in plants[:]:
        if p["watered"]:
            p["timer"] += 1
            if p["timer"] >= PLANT_GROW_TIME:
                resources.append({"x": p["x"], "y": p["y"], "type": "food"})
                plants.remove(p)
                grown_plants += 1

    # RESOURCE COLLECTION
    for r in resources[:]:
        if r["x"] == player["x"] and r["y"] == player["y"]:
            if inventory_size() < MAX_INVENTORY:
                if r["type"] == "gold":
                    player["gold"] += 1
                else:
                    player["food"] += 1
                resources.remove(r)

    # BASE DEPOSIT
    if player["x"] == base["x"] and player["y"] == base["y"]:
        score_gold += player["gold"]
        score_food += player["food"]
        player["gold"] = 0
        player["food"] = 0

    # ENEMY COLLISION
    for e in enemies:
        if e["x"] == player["x"] and e["y"] == player["y"]:
            running = False
            reason = "Killed by enemy"

    # EXIT
    if player["x"] == exit_door["x"] and player["y"] == exit_door["y"]:
        running = False
        reason = "Exited safely"

    # DRAW GRID
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            pygame.draw.rect(
                screen, WHITE,
                (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1
            )

    draw_tile(base["x"], base["y"], BLUE)
    draw_tile(exit_door["x"], exit_door["y"], PURPLE)

    for w in water_sources:
        draw_tile(w["x"], w["y"], CYAN)

    for r in resources:
        draw_tile(r["x"], r["y"], YELLOW if r["type"] == "gold" else GREEN)

    for p in plants:
        draw_tile(p["x"], p["y"], DARK_GREEN if p["watered"] else BROWN)

    for e in enemies:
        draw_tile(e["x"], e["y"], RED)

    draw_tile(player["x"], player["y"], BLACK)

    # HUD
    draw_text(f"Steps: {steps}/{MAX_STEPS}", 5, 5)
    draw_text(
        f"Inv G:{player['gold']} F:{player['food']} W:{player['water']}",
        5, 25
    )
    draw_text(
        f"Score G:{score_gold} F:{score_food} Plants:{grown_plants}",
        5, 45
    )
    draw_text(f"Objective: {GAME_OBJECTIVE}", 5, 65)


    pygame.display.flip()

# --------------------
# GAME OVER
# --------------------
screen.fill(WHITE)
draw_text("GAME OVER", 160, 180)
draw_text(reason, 140, 205)
draw_text(f"Gold: {score_gold}", 140, 235)
draw_text(f"Food: {score_food}", 140, 255)
draw_text(f"Plants Grown: {grown_plants}", 140, 275)
pygame.display.flip()
pygame.time.wait(4000)

with open(LOG_FILE, "a") as f:
    f.write(
        f"objective={GAME_OBJECTIVE}, "
        f"outcome={reason}, "
        f"gold={score_gold}, "
        f"food={score_food}, "
        f"plants={grown_plants}, "
        f"steps={steps}\n"
    )

pygame.quit()

