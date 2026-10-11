import math
from pathlib import Path

import pygame
from ai_controller import choose_action, inspect_network
from assets.generate_assets import ensure_assets

pygame.init()

# --------------------------------------------------
# WINDOW / ASSETS
# --------------------------------------------------
WIDTH, HEIGHT = 900, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Merio - Pixel Platform Adventure")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 32)
small_font = pygame.font.Font(None, 22)
tiny_font = pygame.font.Font(None, 16)

ASSET_DIR = Path(__file__).resolve().parent / "assets"
ensure_assets()
ASSETS = {
    name: pygame.image.load(ASSET_DIR / filename).convert_alpha()
    for name, filename in {
        "sky": "sky.png", "cloud": "cloud.png", "ground": "ground.png",
        "platform": "platform.png", "brick": "brick.png",
        "question": "question_block.png", "player": "player.png",
        "coin": "coin.png", "pipe": "pipe.png", "enemy": "enemy.png",
        "spike": "spike.png", "flag": "flag.png", "hill": "hill.png",
    }.items()
}

# --------------------------------------------------
# GAME CONSTANTS
# --------------------------------------------------
WORLD_WIDTH = 4200
GROUND_Y = 450
PLAYER_START_X, PLAYER_START_Y = 90, 400
GRAVITY = 0.55
JUMP_STRENGTH = -13.2
PLAYER_SPEED = 5.2

NO_ACTION, MOVE_LEFT, MOVE_RIGHT, JUMP, LEFT_JUMP, RIGHT_JUMP = range(6)
ACTION_NAMES = {
    NO_ACTION: "Nothing", MOVE_LEFT: "Left", MOVE_RIGHT: "Right",
    JUMP: "Jump", LEFT_JUMP: "Left + Jump", RIGHT_JUMP: "Right + Jump",
}
WHITE = (255, 255, 255)
GOLD = (255, 220, 75)
RED = (239, 76, 86)
DARK = (24, 35, 55)

# --------------------------------------------------
# LEVEL 1: GREEN HILLS
# World coordinates are larger than the window; the camera scrolls.
# --------------------------------------------------
ground = pygame.Rect(0, GROUND_Y, WORLD_WIDTH, 100)
platforms = [
    pygame.Rect(250, 365, 132, 24),
    pygame.Rect(465, 315, 132, 24),
    pygame.Rect(710, 355, 125, 24),
    pygame.Rect(930, 285, 150, 24),
    pygame.Rect(1170, 355, 150, 24),
    pygame.Rect(1410, 300, 160, 24),
    pygame.Rect(1665, 350, 150, 24),
    pygame.Rect(1900, 280, 150, 24),
    pygame.Rect(2130, 350, 160, 24),
    pygame.Rect(2380, 300, 160, 24),
    pygame.Rect(2630, 355, 160, 24),
    pygame.Rect(2880, 285, 160, 24),
    pygame.Rect(3135, 345, 150, 24),
    pygame.Rect(3375, 295, 160, 24),
    pygame.Rect(3620, 350, 175, 24),
]
# Blocks can be landed on and bumped from below.
blocks = [
    pygame.Rect(570, 300, 32, 32), pygame.Rect(602, 300, 32, 32),
    pygame.Rect(1060, 225, 32, 32), pygame.Rect(1092, 225, 32, 32),
    pygame.Rect(1560, 240, 32, 32), pygame.Rect(1592, 240, 32, 32),
    pygame.Rect(2290, 275, 32, 32), pygame.Rect(2322, 275, 32, 32),
    pygame.Rect(3060, 240, 32, 32), pygame.Rect(3092, 240, 32, 32),
]
question_blocks = [
    pygame.Rect(635, 255, 32, 32), pygame.Rect(1115, 190, 32, 32),
    pygame.Rect(1625, 205, 32, 32), pygame.Rect(2350, 235, 32, 32),
    pygame.Rect(3125, 205, 32, 32), pygame.Rect(3525, 235, 32, 32),
]
pipes = [
    pygame.Rect(810, 362, 64, 88), pygame.Rect(1325, 386, 64, 64),
    pygame.Rect(1815, 362, 64, 88), pygame.Rect(2510, 386, 64, 64),
    pygame.Rect(3260, 362, 64, 88), pygame.Rect(3785, 386, 64, 64),
]
solid_surfaces = platforms + blocks + question_blocks + pipes + [ground]

# Six main collectible coins are deliberately spread along the level.
coin_positions = [
    (300, 325), (740, 305), (1000, 235),
    (1730, 300), (2460, 250), (3450, 245),
]
coins = [pygame.Rect(x, y, 24, 24) for x, y in coin_positions]
coin_collected = [False] * len(coins)

spikes = [
    pygame.Rect(390, 426, 64, 24), pygame.Rect(875, 426, 64, 24),
    pygame.Rect(1370, 426, 64, 24), pygame.Rect(2040, 426, 64, 24),
    pygame.Rect(2575, 426, 64, 24), pygame.Rect(3315, 426, 64, 24),
    pygame.Rect(3710, 426, 64, 24),
]

# Patrol enemies move back and forth within their own short lanes.
enemies = [
    {"rect": pygame.Rect(520, 422, 32, 28), "left": 490, "right": 640, "speed": 1.6},
    {"rect": pygame.Rect(1220, 422, 32, 28), "left": 1150, "right": 1360, "speed": 1.8},
    {"rect": pygame.Rect(1960, 422, 32, 28), "left": 1870, "right": 2070, "speed": 2.0},
    {"rect": pygame.Rect(2780, 422, 32, 28), "left": 2700, "right": 2860, "speed": 1.7},
    {"rect": pygame.Rect(3500, 422, 32, 28), "left": 3420, "right": 3600, "speed": 2.0},
]

goal = pygame.Rect(4020, 310, 32, 140)
restart_button = pygame.Rect(WIDTH // 2 - 100, 200, 200, 50)

# --------------------------------------------------
# GAME STATE
# --------------------------------------------------
player = pygame.Rect(PLAYER_START_X, PLAYER_START_Y, 32, 40)
velocity_y = 0.0
on_surface = False
score = 0
lives = 3
game_won = False
game_over = False
running = True
action_id = NO_ACTION
ai_enabled = False
camera_x = 0.0
hurt_cooldown = 0
question_hit = set()


def restart_game():
    global player, velocity_y, on_surface, score, lives
    global game_won, game_over, action_id, coin_collected
    global camera_x, hurt_cooldown, question_hit
    player = pygame.Rect(PLAYER_START_X, PLAYER_START_Y, 32, 40)
    velocity_y = 0.0
    on_surface = False
    score, lives = 0, 3
    game_won = game_over = False
    action_id = NO_ACTION
    coin_collected = [False] * len(coins)
    camera_x = 0.0
    hurt_cooldown = 0
    question_hit = set()
    for enemy in enemies:
        enemy["rect"].x = enemy["left"] + 30


def respawn_player():
    global lives, game_over, velocity_y, on_surface, hurt_cooldown
    lives -= 1
    player.x, player.y = PLAYER_START_X, PLAYER_START_Y
    velocity_y = 0.0
    on_surface = False
    hurt_cooldown = 70
    if lives <= 0:
        game_over = True


def draw_tiled(image, rect, camera):
    view_rect = pygame.Rect(round(rect.x - camera), rect.y, rect.width, rect.height)
    if view_rect.right < 0 or view_rect.left > WIDTH:
        return
    tile_w = image.get_width()
    tile_h = image.get_height()
    for x in range(view_rect.left, view_rect.right, tile_w):
        for y in range(view_rect.top, view_rect.bottom, tile_h):
            screen.blit(image, (x, y))


def draw_world_background():
    # Sky fills the screen; distant hills and clouds move at different speeds.
    screen.blit(pygame.transform.scale(ASSETS["sky"], (WIDTH, HEIGHT)), (0, 0))
    for i, x in enumerate(range(-220, WORLD_WIDTH, 430)):
        hill_x = int(x - camera_x * 0.18)
        if -250 < hill_x < WIDTH:
            screen.blit(ASSETS["hill"], (hill_x, 338 + (i % 2) * 20))
    for i, x in enumerate(range(-80, WORLD_WIDTH, 360)):
        cloud_x = int(x - camera_x * 0.32)
        if -120 < cloud_x < WIDTH:
            screen.blit(ASSETS["cloud"], (cloud_x, 55 + (i % 3) * 42))


def draw_network_panel(network_view):
    panel = pygame.Rect(610, 12, 278, 205)
    pygame.draw.rect(screen, (17, 22, 35), panel, border_radius=8)
    pygame.draw.rect(screen, (70, 90, 120), panel, 1, border_radius=8)
    screen.blit(small_font.render("NEURAL NETWORK", True, (100, 220, 200)), (panel.x + 10, panel.y + 7))
    screen.blit(tiny_font.render("LIVE FORWARD PASS | UNTRAINED", True, (220, 180, 100)), (panel.x + 10, panel.y + 29))
    layer_x = [panel.x + 24, panel.x + 137, panel.x + 250]
    layer_y = [
        [panel.y + 64 + i * 16 for i in range(8)],
        [panel.y + 75 + i * 23 for i in range(6)],
        [panel.y + 75 + i * 23 for i in range(6)],
    ]
    for layer in range(2):
        left_values = network_view["inputs"] if layer == 0 else network_view["hidden"]
        right_values = network_view["hidden"] if layer == 0 else network_view["outputs"]
        for i, y1 in enumerate(layer_y[layer]):
            for j, y2 in enumerate(layer_y[layer + 1]):
                strength = abs(left_values[i] * right_values[j])
                shade = int(45 + min(1.0, strength) * 110)
                pygame.draw.line(screen, (shade // 2, shade, shade),
                                 (layer_x[layer], y1), (layer_x[layer + 1], y2), 1)
    layers = (network_view["inputs"], network_view["hidden"], network_view["outputs"])
    for layer_index, values in enumerate(layers):
        for i, value in enumerate(values):
            x, y = layer_x[layer_index], layer_y[layer_index][i]
            strength = int(80 + abs(value) * 175)
            if layer_index == 2 and i == network_view["predicted_action"]:
                color = (255, 205, 80)
            elif value >= 0:
                color = (30, strength, 150)
            else:
                color = (180, 70, strength)
            pygame.draw.circle(screen, color, (x, y), 5)
            pygame.draw.circle(screen, (210, 220, 235), (x, y), 5, 1)
    screen.blit(tiny_font.render("IN", True, WHITE), (panel.x + 8, panel.y + 48))
    screen.blit(tiny_font.render("HIDDEN", True, WHITE), (panel.x + 111, panel.y + 48))
    screen.blit(tiny_font.render("ACTIONS", True, WHITE), (panel.x + 220, panel.y + 48))
    predicted_name = ACTION_NAMES[network_view["predicted_action"]]
    screen.blit(tiny_font.render(f"NN guess: {predicted_name}", True, GOLD), (panel.x + 10, panel.y + 185))


# --------------------------------------------------
# MAIN LOOP
# --------------------------------------------------
while running:
    jump_requested = False
    mouse_position = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                restart_game()
            elif event.key == pygame.K_i:
                ai_enabled = not ai_enabled
                print("AI mode:", "ON" if ai_enabled else "OFF")
            elif event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                jump_requested = True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if (game_won or game_over) and restart_button.collidepoint(event.pos):
                restart_game()

    # Preserve the AI controller's current six-coin observation format.
    state = [
        player.x, player.y, velocity_y, coins[0].x, coins[0].y,
        goal.x, goal.y, int(coin_collected[0]), int(on_surface),
        int(game_won), lives, int(game_over), score,
    ]
    for i, coin in enumerate(coins):
        state.extend([coin.x, coin.y, int(coin_collected[i])])
    for spike in spikes:
        state.extend([spike.x, spike.y])

    action_id = NO_ACTION
    if ai_enabled and not game_won and not game_over:
        action_id = choose_action(state)
    else:
        keys = pygame.key.get_pressed()
        left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        if left and not right:
            action_id = MOVE_LEFT
        elif right and not left:
            action_id = MOVE_RIGHT
        if jump_requested:
            if action_id == MOVE_LEFT:
                action_id = LEFT_JUMP
            elif action_id == MOVE_RIGHT:
                action_id = RIGHT_JUMP
            else:
                action_id = JUMP

    horizontal = 0
    if action_id in (MOVE_LEFT, LEFT_JUMP):
        horizontal = -1
    elif action_id in (MOVE_RIGHT, RIGHT_JUMP):
        horizontal = 1
    jump_requested = action_id in (JUMP, LEFT_JUMP, RIGHT_JUMP)

    if not game_won and not game_over:
        # Move patrolling enemies.
        for enemy in enemies:
            enemy["rect"].x += enemy["speed"]
            if enemy["rect"].right >= enemy["right"] or enemy["rect"].left <= enemy["left"]:
                enemy["speed"] *= -1

        # Horizontal movement and side collisions.
        dx = int(horizontal * PLAYER_SPEED)
        player.x += dx
        player.left = max(0, player.left)
        player.right = min(WORLD_WIDTH, player.right)
        for solid in solid_surfaces:
            if player.colliderect(solid):
                if dx > 0:
                    player.right = solid.left
                elif dx < 0:
                    player.left = solid.right

        # Vertical movement, landing, and bumping blocks from underneath.
        previous_top, previous_bottom = player.top, player.bottom
        velocity_y += GRAVITY
        player.y += int(velocity_y)
        on_surface = False
        for solid in solid_surfaces:
            if player.right <= solid.left or player.left >= solid.right:
                continue
            if velocity_y > 0 and previous_bottom <= solid.top and player.bottom >= solid.top:
                player.bottom = solid.top
                velocity_y = 0.0
                on_surface = True
            elif velocity_y < 0 and previous_top >= solid.bottom and player.top <= solid.bottom:
                player.top = solid.bottom
                velocity_y = 0.0
                if solid in question_blocks:
                    question_hit.add((solid.x, solid.y))
        if jump_requested and on_surface:
            velocity_y = JUMP_STRENGTH
            on_surface = False

        # Pickups.
        for i, coin in enumerate(coins):
            if not coin_collected[i] and player.colliderect(coin):
                coin_collected[i] = True
                score += 1

        # Hazard collisions: brief invulnerability avoids losing every life instantly.
        if hurt_cooldown > 0:
            hurt_cooldown -= 1
        elif any(player.colliderect(spike) for spike in spikes) or any(
            player.colliderect(enemy["rect"]) for enemy in enemies
        ):
            respawn_player()

        if player.top > HEIGHT + 180:
            respawn_player()

        if player.colliderect(goal):
            game_won = True
            print("You reached the flag!")

    # Camera follows the player, with a little space ahead to see obstacles.
    camera_x = int(max(0, min(WORLD_WIDTH - WIDTH, player.centerx - WIDTH * 0.38)))
    network_view = inspect_network(state)

    # --------------------------------------------------
    # DRAW
    # --------------------------------------------------
    draw_world_background()

    # Ground is tiled rather than a flat rectangle.
    draw_tiled(ASSETS["ground"], ground, camera_x)

    for platform in platforms:
        draw_tiled(ASSETS["platform"], platform, camera_x)
    for block in blocks:
        screen.blit(ASSETS["brick"], (block.x - camera_x, block.y))
    for block in question_blocks:
        sprite = ASSETS["brick"] if (block.x, block.y) in question_hit else ASSETS["question"]
        screen.blit(sprite, (block.x - camera_x, block.y))
    for pipe_rect in pipes:
        screen.blit(pygame.transform.scale(ASSETS["pipe"], pipe_rect.size),
                    (pipe_rect.x - camera_x, pipe_rect.y))

    for i, coin in enumerate(coins):
        if not coin_collected[i]:
            bob = int(math.sin(pygame.time.get_ticks() / 180 + i) * 3)
            screen.blit(ASSETS["coin"], (coin.x - camera_x, coin.y + bob))

    for spike in spikes:
        screen.blit(pygame.transform.scale(ASSETS["spike"], spike.size),
                    (spike.x - camera_x, spike.y))
    for enemy in enemies:
        screen.blit(ASSETS["enemy"], (enemy["rect"].x - camera_x, enemy["rect"].y))

    screen.blit(ASSETS["flag"], (goal.x - camera_x - 8, goal.y - 4))
    # Flash the character briefly after respawning.
    if hurt_cooldown == 0 or hurt_cooldown % 8 < 4:
        screen.blit(ASSETS["player"], (player.x - camera_x, player.y))

    # HUD and controls.
    pygame.draw.rect(screen, (17, 30, 48), (12, 10, 260, 118), border_radius=8)
    pygame.draw.rect(screen, (65, 100, 125), (12, 10, 260, 118), 1, border_radius=8)
    screen.blit(font.render(f"COINS  {score}/{len(coins)}", True, GOLD), (24, 18))
    screen.blit(small_font.render(f"Lives: {'♥ ' * max(0, lives)}", True, WHITE), (24, 51))
    screen.blit(small_font.render(f"Action: {ACTION_NAMES[action_id]}", True, WHITE), (24, 75))
    screen.blit(small_font.render(f"AI: {'ON' if ai_enabled else 'OFF'}  [I]", True,
                                  (80, 245, 180) if ai_enabled else WHITE), (24, 99))

    # Level progress bar.
    progress = max(0, min(1, player.centerx / WORLD_WIDTH))
    pygame.draw.rect(screen, (30, 45, 65), (300, 18, 270, 12), border_radius=5)
    pygame.draw.rect(screen, (76, 220, 143), (300, 18, int(270 * progress), 12), border_radius=5)
    screen.blit(tiny_font.render("START", True, WHITE), (300, 34))
    screen.blit(tiny_font.render("FLAG", True, WHITE), (540, 34))
    screen.blit(small_font.render("MERIO  |  GREEN HILLS", True, WHITE), (300, 52))
    screen.blit(tiny_font.render("A/D or arrows: move   W/SPACE: jump   I: AI   R: restart   ESC: quit",
                                 True, WHITE), (18, HEIGHT - 22))

    draw_network_panel(network_view)

    if game_won or game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 12, 25, 185))
        screen.blit(overlay, (0, 0))
        message = "LEVEL COMPLETE!" if game_won else "GAME OVER"
        message_color = GOLD if game_won else RED
        message_image = font.render(message, True, message_color)
        screen.blit(message_image, message_image.get_rect(center=(WIDTH // 2, 145)))
        button_color = (65, 195, 135) if restart_button.collidepoint(mouse_position) else (50, 160, 110)
        pygame.draw.rect(screen, button_color, restart_button, border_radius=10)
        button_text = font.render("PLAY AGAIN", True, WHITE)
        screen.blit(button_text, button_text.get_rect(center=restart_button.center))
        hint = small_font.render("Press R or click Play Again", True, WHITE)
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, 275)))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
