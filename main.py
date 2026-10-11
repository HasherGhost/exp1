import math
from pathlib import Path

import pygame
from dqn_agent import DQNAgent
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
 "player": "player.png",
        "coin": "coin.png", "pipe": "pipe.png", "enemy": "enemy.png",
        "spike": "spike.png", "flag": "flag.png", "hill": "hill.png",
    }.items()
}

# --------------------------------------------------
# GAME CONSTANTS
# --------------------------------------------------
WORLD_WIDTH = 7200
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
    pygame.Rect(465, 315, 100, 24),
    pygame.Rect(710, 355, 90, 24),
    pygame.Rect(930, 285, 150, 24),
    pygame.Rect(1170, 355, 150, 24),
    pygame.Rect(1410, 300, 160, 24),
    pygame.Rect(1665, 350, 150, 24),
    pygame.Rect(1900, 280, 150, 24),
    pygame.Rect(2130, 350, 160, 24),
    pygame.Rect(2380, 300, 160, 24),
    pygame.Rect(2630, 355, 160, 24),
    pygame.Rect(2880, 285, 160, 24),
    pygame.Rect(3135, 345, 120, 24),
    pygame.Rect(3375, 295, 160, 24),
    pygame.Rect(3620, 350, 155, 24),
    # Extended section: broad, spaced platforms with manageable height changes.
    pygame.Rect(3970, 350, 140, 24),
    pygame.Rect(4200, 300, 140, 24),
    pygame.Rect(4440, 345, 150, 24),
    pygame.Rect(4690, 275, 150, 24),
    pygame.Rect(4940, 330, 160, 24),
    pygame.Rect(5195, 285, 150, 24),
    pygame.Rect(5440, 350, 160, 24),
    pygame.Rect(5690, 295, 160, 24),
    pygame.Rect(5950, 340, 160, 24),
    pygame.Rect(6200, 280, 160, 24),
    pygame.Rect(6450, 330, 160, 24),
    pygame.Rect(6700, 350, 130, 24),
]
# Blocks can be landed on and bumped from below.
blocks = [
    pygame.Rect(570, 300, 32, 32), pygame.Rect(602, 300, 32, 32),
    pygame.Rect(1060, 225, 32, 32), pygame.Rect(1092, 225, 32, 32),
    pygame.Rect(1560, 240, 32, 32), pygame.Rect(1592, 240, 32, 32),
    pygame.Rect(2290, 275, 32, 32), pygame.Rect(2322, 275, 32, 32),
    pygame.Rect(3060, 240, 32, 32), pygame.Rect(3092, 240, 32, 32),
    pygame.Rect(4310, 255, 32, 32), pygame.Rect(4342, 255, 32, 32),
    pygame.Rect(4800, 230, 32, 32), pygame.Rect(4832, 230, 32, 32),
    pygame.Rect(5270, 240, 32, 32), pygame.Rect(5302, 240, 32, 32),
    pygame.Rect(6210, 235, 32, 32), pygame.Rect(6242, 235, 32, 32),
]
pipes = [
    pygame.Rect(810, 362, 64, 88), pygame.Rect(1325, 386, 64, 64),
    pygame.Rect(1815, 362, 64, 88), pygame.Rect(2510, 386, 64, 64),
    pygame.Rect(3260, 362, 64, 88), pygame.Rect(3785, 386, 64, 64),
    pygame.Rect(3990, 386, 64, 64), pygame.Rect(4460, 362, 64, 88),
    pygame.Rect(4930, 386, 64, 64), pygame.Rect(5400, 362, 64, 88),
    pygame.Rect(5870, 386, 64, 64), pygame.Rect(6340, 362, 64, 88),
    pygame.Rect(6760, 386, 64, 64),
]
solid_surfaces = platforms + blocks + pipes + [ground]

# Six main collectible coins are deliberately spread along the level.
coin_positions = [
    (300, 325), (740, 305), (1000, 235),
    (1730, 300), (2460, 250), (3450, 245),
    (4070, 315), (4350, 270), (4800, 220), (5270, 230),
    (5740, 260), (6210, 225), (6630, 250), (6900, 370),
]
coins = [pygame.Rect(x, y, 24, 24) for x, y in coin_positions]
coin_collected = [False] * len(coins)

spikes = [
    pygame.Rect(390, 426, 64, 24), pygame.Rect(875, 426, 64, 24),
    pygame.Rect(1395, 426, 64, 24), pygame.Rect(2040, 426, 64, 24),
    pygame.Rect(2575, 426, 64, 24), pygame.Rect(3330, 426, 64, 24),
    pygame.Rect(3710, 426, 64, 24),
    pygame.Rect(4100, 426, 64, 24), pygame.Rect(4570, 426, 64, 24),
    pygame.Rect(5100, 426, 64, 24), pygame.Rect(5580, 426, 64, 24),
    pygame.Rect(6050, 426, 64, 24), pygame.Rect(6520, 426, 64, 24),
]

# Patrol enemies move back and forth within their own short lanes.
enemies = [
    {"rect": pygame.Rect(520, 422, 32, 28), "left": 490, "right": 640, "speed": 1.6},
    {"rect": pygame.Rect(1220, 422, 32, 28), "left": 1150, "right": 1360, "speed": 1.8},
    {"rect": pygame.Rect(1960, 422, 32, 28), "left": 1870, "right": 2070, "speed": 2.0},
    {"rect": pygame.Rect(2780, 422, 32, 28), "left": 2700, "right": 2860, "speed": 1.7},
    {"rect": pygame.Rect(3500, 422, 32, 28), "left": 3420, "right": 3600, "speed": 2.0},
    {"rect": pygame.Rect(4250, 422, 32, 28), "left": 4180, "right": 4390, "speed": 1.7},
    {"rect": pygame.Rect(4720, 422, 32, 28), "left": 4660, "right": 4880, "speed": 1.8},
    {"rect": pygame.Rect(5200, 422, 32, 28), "left": 5140, "right": 5350, "speed": 1.6},
    {"rect": pygame.Rect(5670, 422, 32, 28), "left": 5610, "right": 5820, "speed": 1.9},
    {"rect": pygame.Rect(6140, 422, 32, 28), "left": 6080, "right": 6290, "speed": 1.7},
    {"rect": pygame.Rect(6610, 422, 32, 28), "left": 6550, "right": 6740, "speed": 1.8},
]

goal = pygame.Rect(7040, 310, 32, 140)
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
agent = DQNAgent()
terminal_wait = 0


def restart_game():
    global player, velocity_y, on_surface, score, lives
    global game_won, game_over, action_id, coin_collected
    global camera_x, hurt_cooldown, terminal_wait
    player = pygame.Rect(PLAYER_START_X, PLAYER_START_Y, 32, 40)
    velocity_y = 0.0
    on_surface = False
    score, lives = 0, 3
    game_won = game_over = False
    action_id = NO_ACTION
    coin_collected = [False] * len(coins)
    camera_x = 0.0
    hurt_cooldown = 0
    terminal_wait = 0
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


def get_observation():
    """Compact, normalized features for the learning agent (not a scripted route)."""
    player_cx = player.centerx
    player_cy = player.centery
    remaining = [
        (coin.centerx, coin.centery)
        for i, coin in enumerate(coins) if not coin_collected[i]
    ]
    if remaining:
        target_x, target_y = min(
            remaining,
            key=lambda p: abs(p[0] - player_cx) + abs(p[1] - player_cy)
        )
    else:
        target_x, target_y = goal.centerx, goal.centery

    # Report the next obstacle ahead, not whichever hazard happens to be
    # closest behind the player. Include pipes because they physically block movement.
    hazards = [spike.centerx for spike in spikes]
    hazards += [enemy["rect"].centerx for enemy in enemies]
    hazards += [pipe.centerx for pipe in pipes]
    hazards_ahead = [x for x in hazards if x >= player_cx - 8]
    hazard_dx = (min(hazards_ahead) - player_cx) if hazards_ahead else 400

    return [
        player.x / WORLD_WIDTH * 2.0 - 1.0,
        player.y / HEIGHT * 2.0 - 1.0,
        max(-1.0, min(1.0, velocity_y / 15.0)),
        float(on_surface),
        max(-1.0, min(1.0, (goal.centerx - player_cx) / WORLD_WIDTH)),
        max(-1.0, min(1.0, (target_x - player_cx) / 700.0)),
        max(-1.0, min(1.0, (target_y - player_cy) / HEIGHT)),
        (sum(coin_collected) / max(1, len(coins))) * 2.0 - 1.0,
        max(-1.0, min(1.0, hazard_dx / 400.0)),
        (lives / 3.0) * 2.0 - 1.0,
    ]


def draw_tiled(image, rect, camera):
    view_rect = pygame.Rect(round(rect.x - camera), rect.y, rect.width, rect.height)
    if view_rect.right <= 0 or view_rect.left >= WIDTH:
        return
    tile_w = image.get_width()
    tile_h = image.get_height()

    # Clip the texture to the actual collision rectangle. Without this, the
    # final 64px tile can draw beyond a platform's right edge, making it look
    # solid where the player actually falls through.
    previous_clip = screen.get_clip()
    screen.set_clip(view_rect.clip(screen.get_rect()))
    for x in range(view_rect.left, view_rect.right, tile_w):
        for y in range(view_rect.top, view_rect.bottom, tile_h):
            screen.blit(image, (x, y))
    screen.set_clip(previous_clip)


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
    screen.blit(small_font.render("LEARNING DQN", True, (100, 220, 200)), (panel.x + 10, panel.y + 7))
    screen.blit(tiny_font.render(
        f"LIVE LEARNING | EP {network_view['episodes']} | EPS {network_view['epsilon']:.2f}",
        True, (220, 180, 100)), (panel.x + 10, panel.y + 29))

    input_values = network_view["inputs"]
    hidden_values = network_view["hidden"]
    output_values = network_view["outputs"]
    layer_x = [panel.x + 22, panel.x + 137, panel.x + 250]
    layer_y = [
        [panel.y + 62 + i * 12 for i in range(len(input_values))],
        [panel.y + 70 + i * 18 for i in range(len(hidden_values))],
        [panel.y + 70 + i * 18 for i in range(len(output_values))],
    ]
    layers = (input_values, hidden_values, output_values)
    for layer in range(2):
        left_values = layers[layer]
        right_values = layers[layer + 1]
        for i, y1 in enumerate(layer_y[layer]):
            for j, y2 in enumerate(layer_y[layer + 1]):
                strength = min(1.0, abs(left_values[i] * right_values[j]))
                shade = int(45 + strength * 110)
                pygame.draw.line(screen, (shade // 2, shade, shade),
                                 (layer_x[layer], y1), (layer_x[layer + 1], y2), 1)
    for layer_index, values in enumerate(layers):
        for i, value in enumerate(values):
            x, y = layer_x[layer_index], layer_y[layer_index][i]
            strength = int(80 + min(1.0, abs(float(value))) * 175)
            if layer_index == 2 and i == network_view["predicted_action"]:
                color = (255, 205, 80)
            elif value >= 0:
                color = (30, strength, 150)
            else:
                color = (180, 70, strength)
            pygame.draw.circle(screen, color, (x, y), 4 if layer_index == 0 else 5)
            pygame.draw.circle(screen, (210, 220, 235), (x, y), 4 if layer_index == 0 else 5, 1)

    screen.blit(tiny_font.render("STATE", True, WHITE), (panel.x + 5, panel.y + 48))
    screen.blit(tiny_font.render("HIDDEN", True, WHITE), (panel.x + 111, panel.y + 48))
    screen.blit(tiny_font.render("Q ACTIONS", True, WHITE), (panel.x + 208, panel.y + 48))
    predicted_name = ACTION_NAMES[network_view["predicted_action"]]
    screen.blit(tiny_font.render(
        f"Best: {predicted_name} | Loss: {network_view['loss']:.3f}",
        True, GOLD), (panel.x + 10, panel.y + 185))


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

    observation = get_observation()
    previous_observation = observation.copy()
    previous_center_x = player.centerx
    previous_score = score
    previous_lives = lives

    action_id = NO_ACTION
    if ai_enabled and not game_won and not game_over:
        action_id = agent.act(observation, explore=True)
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

        # Horizontal movement: resolve the nearest obstacle first so overlapping
        # collision checks cannot push the player through a second solid object.
        dx = int(horizontal * PLAYER_SPEED)
        old_left, old_right = player.left, player.right
        player.x += dx
        if dx > 0:
            for solid in sorted(solid_surfaces, key=lambda rect: rect.left):
                if player.colliderect(solid):
                    player.right = solid.left
        elif dx < 0:
            for solid in sorted(solid_surfaces, key=lambda rect: rect.right, reverse=True):
                if player.colliderect(solid):
                    player.left = solid.right
        player.left = max(0, player.left)
        player.right = min(WORLD_WIDTH, player.right)

        # Vertical movement: choose only the closest surface crossed this frame.
        # This prevents stacked/nearby solids from fighting over the player's position.
        previous_top, previous_bottom = player.top, player.bottom
        velocity_y += GRAVITY
        player.y += int(velocity_y)
        on_surface = False
        overlapping_x = [
            solid for solid in solid_surfaces
            if player.right > solid.left and player.left < solid.right
        ]

        if velocity_y > 0:
            landing_surfaces = [
                solid for solid in overlapping_x
                if previous_bottom <= solid.top and player.bottom >= solid.top
            ]
            if landing_surfaces:
                landing = min(landing_surfaces, key=lambda rect: rect.top)
                player.bottom = landing.top
                velocity_y = 0.0
                on_surface = True
        elif velocity_y < 0:
            ceiling_surfaces = [
                solid for solid in overlapping_x
                if previous_top >= solid.bottom and player.top <= solid.bottom
            ]
            if ceiling_surfaces:
                ceiling = max(ceiling_surfaces, key=lambda rect: rect.bottom)
                player.top = ceiling.bottom
                velocity_y = 0.0
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

        # Learn from the actual result of the action just taken.
        next_observation = get_observation()
        reward = -0.02  # Small time penalty: discourage doing nothing.

        if lives == previous_lives:
            # Make each useful step forward clearly better than reversing.
            old_goal_distance = abs(goal.centerx - previous_center_x)
            new_goal_distance = abs(goal.centerx - player.centerx)
            goal_progress = (old_goal_distance - new_goal_distance) / 5.0
            reward += max(-1.0, min(1.0, goal_progress)) * 0.25

            # Repeatedly walking into a wall/pipe gives no progress; teach the
            # agent that a blocked move is worse than trying a different action.
            if horizontal != 0 and player.centerx == previous_center_x:
                reward -= 0.12
        else:
            # Losing a life is much worse than a small movement reward.
            reward -= 18.0

        # Coins are worth a strong bonus, so a useful detour can beat
        # blindly rushing toward the flag.
        reward += (score - previous_score) * 15.0

        if game_won:
            reward += 100.0
        done = game_won or game_over
        if ai_enabled:
            agent.remember(previous_observation, action_id, reward, next_observation, done)
            if agent.steps % 4 == 0:
                agent.train_step()
            if done:
                agent.end_episode()
                terminal_wait = 0

    # In AI mode, automatically begin another episode after showing the result.
    # This lets training continue without a manual restart after every failure.
    if ai_enabled and (game_won or game_over):
        terminal_wait += 1
        if terminal_wait >= 120:
            restart_game()


    # Camera follows the player, with a little space ahead to see obstacles.
    camera_x = int(max(0, min(WORLD_WIDTH - WIDTH, player.centerx - WIDTH * 0.38)))
    network_view = agent.inspect(get_observation())

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
    screen.blit(tiny_font.render(f"Episodes: {agent.episodes}  Steps: {agent.steps}", True, WHITE), (150, 104))
    screen.blit(small_font.render(f"AI: {'LEARNING' if ai_enabled else 'OFF'}  [I]", True,
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
