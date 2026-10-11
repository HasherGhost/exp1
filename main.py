
import pygame
from ai_controller import choose_action, inspect_network

pygame.init()

# --------------------------------------------------
# 1. WINDOW
# --------------------------------------------------

WIDTH, HEIGHT = 900, 500

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Merio - AI Training Project")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# --------------------------------------------------
# 2. COLOURS
# --------------------------------------------------

BACKGROUND = (25, 30, 45)
PLAYER_COLOR = (15, 200, 160)
GROUND_COLOR = (100, 110, 130)
PLATFORM_COLOR = (130, 150, 230)
COIN_COLOR = (255, 215, 0)
GOAL_COLOR = (255, 100, 100)
SPIKE_COLOR = (240, 75, 85)
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (50, 160, 110)
BUTTON_HOVER_COLOR = (65, 195, 135)

# --------------------------------------------------
# 3. GAME CONSTANTS
# --------------------------------------------------

PLAYER_START_X = 100
PLAYER_START_Y = 350

GRAVITY = 0.5
JUMP_STRENGTH = -12
PLAYER_SPEED = 5

# AI action IDs
NO_ACTION = 0
MOVE_LEFT = 1
MOVE_RIGHT = 2
JUMP = 3
LEFT_JUMP = 4
RIGHT_JUMP = 5

ACTION_NAMES = {
    NO_ACTION: "Nothing",
    MOVE_LEFT: "Left",
    MOVE_RIGHT: "Right",
    JUMP: "Jump",
    LEFT_JUMP: "Left + Jump",
    RIGHT_JUMP: "Right + Jump",
}

# --------------------------------------------------
# 4. LEVEL DESIGN
# --------------------------------------------------

ground = pygame.Rect(0, 430, WIDTH, 70)

platforms = [
    pygame.Rect(200, 350, 130, 20),
    pygame.Rect(360, 290, 130, 20),
    pygame.Rect(520, 230, 130, 20),
    pygame.Rect(680, 300, 120, 20),
    pygame.Rect(760, 380, 130, 20),
]

solid_surfaces = platforms + [ground]

goal = pygame.Rect(850, 370, 25, 60)

# Each coin has its own position and collection status.
coin_positions = [
    (100, 395),
    (250, 315),
    (410, 255),
    (570, 195),
    (720, 265),
    (810, 345),
]

coins = [
    pygame.Rect(x, y, 20, 20)
    for x, y in coin_positions
]

coin_collected = [False] * len(coins)

# Hazards are rectangles that damage the player.
# Ground spikes and spikes on a platform.
spikes = [
    pygame.Rect(440, 405, 55, 25),
]

restart_button = pygame.Rect(350, 180, 200, 50)

# --------------------------------------------------
# 5. GAME VARIABLES
# --------------------------------------------------

player = pygame.Rect(
    PLAYER_START_X, PLAYER_START_Y, 40, 40
)

velocity_y = 0.0
on_surface = False

score = 0
lives = 3

game_won = False
game_over = False
running = True

action_id = NO_ACTION
ai_enabled = False

# --------------------------------------------------
# 6. RESTART
# --------------------------------------------------

def restart_game():
    global player, velocity_y, on_surface
    global score, lives, game_won, game_over
    global action_id, coin_collected

    player = pygame.Rect(
        PLAYER_START_X, PLAYER_START_Y, 40, 40
    )

    velocity_y = 0.0
    on_surface = False

    score = 0
    lives = 3

    game_won = False
    game_over = False

    action_id = NO_ACTION
    coin_collected = [False] * len(coins)


def respawn_player():
    global player, velocity_y, on_surface
    global lives, game_over, action_id

    lives -= 1

    player.x = PLAYER_START_X
    player.y = PLAYER_START_Y

    velocity_y = 0.0
    on_surface = False
    action_id = NO_ACTION

    if lives <= 0:
        game_over = True


# --------------------------------------------------
# 7. MAIN GAME LOOP
# --------------------------------------------------

while running:

    jump_requested = False
    mouse_position = pygame.mouse.get_pos()

    # --------------------------------------------------
    # 8. EVENTS
    # --------------------------------------------------

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

            elif event.key in (
                pygame.K_SPACE,
                pygame.K_UP,
                pygame.K_w,
            ):
                jump_requested = True

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1 and (
                game_won or game_over
            ):
                if restart_button.collidepoint(event.pos):
                    restart_game()

    # --------------------------------------------------
    # Build the current observation for the AI controller
    # --------------------------------------------------

    state = [
        player.x,
        player.y,
        velocity_y,
        coins[0].x,
        coins[0].y,
        goal.x,
        goal.y,
        int(coin_collected[0]),
        int(on_surface),
        int(game_won),
        lives,
        int(game_over),
        score,
    ]

    # Append each coin's position and collected flag.
    for i, coin in enumerate(coins):
        state.extend([
            coin.x,
            coin.y,
            int(coin_collected[i]),
        ])

    # Append hazard positions for future AI input.
    for spike in spikes:
        state.extend([spike.x, spike.y])

    # --------------------------------------------------
    # 9. INPUT AND AI ACTION
    # --------------------------------------------------

    action_id = NO_ACTION

    if ai_enabled and not game_won and not game_over:
        action_id = choose_action(state)

    else:
        keys = pygame.key.get_pressed()

        moving_left = (
            keys[pygame.K_LEFT] or keys[pygame.K_a]
        )

        moving_right = (
            keys[pygame.K_RIGHT] or keys[pygame.K_d]
        )

        if moving_left and not moving_right:
            action_id = MOVE_LEFT

        elif moving_right and not moving_left:
            action_id = MOVE_RIGHT

        if jump_requested:
            if action_id == MOVE_LEFT:
                action_id = LEFT_JUMP
            elif action_id == MOVE_RIGHT:
                action_id = RIGHT_JUMP
            else:
                action_id = JUMP

    action = 0

    if action_id in (MOVE_LEFT, LEFT_JUMP):
        action = -1
    elif action_id in (MOVE_RIGHT, RIGHT_JUMP):
        action = 1

    jump_requested = action_id in (
        JUMP, LEFT_JUMP, RIGHT_JUMP
    )

    # --------------------------------------------------
    # 10. GAME PHYSICS
    # --------------------------------------------------

    if not game_won and not game_over:

        # Horizontal movement
        dx = action * PLAYER_SPEED
        player.x += dx

        # Keep player inside the window
        player.left = max(player.left, 0)
        player.right = min(player.right, WIDTH)

        # Horizontal platform collisions
        for platform in solid_surfaces:
            if player.colliderect(platform):
                if dx > 0:
                    player.right = platform.left
                elif dx < 0:
                    player.left = platform.right

        # Vertical movement
        previous_top = player.top
        previous_bottom = player.bottom

        velocity_y += GRAVITY
        player.y += int(velocity_y)

        on_surface = False

        for platform in solid_surfaces:

            horizontal_overlap = (
                player.right > platform.left
                and player.left < platform.right
            )

            if not horizontal_overlap:
                continue

            # Landing
            if (
                velocity_y > 0
                and previous_bottom <= platform.top
                and player.bottom >= platform.top
            ):
                player.bottom = platform.top
                velocity_y = 0.0
                on_surface = True

            # Hitting platform from underneath
            elif (
                velocity_y < 0
                and previous_top >= platform.bottom
                and player.top <= platform.bottom
            ):
                player.top = platform.bottom
                velocity_y = 0.0

        # Jumping
        if jump_requested and on_surface:
            velocity_y = JUMP_STRENGTH
            on_surface = False

        # --------------------------------------------------
        # 11. COLLECT COINS
        # --------------------------------------------------

        for i, coin in enumerate(coins):

            if (
                not coin_collected[i]
                and player.colliderect(coin)
            ):
                coin_collected[i] = True
                score += 1
                print("Score:", score)

        # --------------------------------------------------
        # 12. SPIKE COLLISIONS
        # --------------------------------------------------

        for spike in spikes:
            if player.colliderect(spike):
                respawn_player()
                break

        # --------------------------------------------------
        # 13. WIN CONDITION
        # --------------------------------------------------

        if player.colliderect(goal):
            game_won = True
            print("You win!")

    # --------------------------------------------------
    # 14. AI STATE
    # --------------------------------------------------
    # The current observation is built before action selection,
    # so the controller always receives a valid, current state.

    network_view = inspect_network(state)

    # --------------------------------------------------
    # 15. DRAW THE LEVEL
    # --------------------------------------------------

    screen.fill(BACKGROUND)

    pygame.draw.rect(
        screen, GROUND_COLOR, ground
    )

    for platform in platforms:
        pygame.draw.rect(
            screen, PLATFORM_COLOR, platform
        )

    # Draw uncollected coins
    for i, coin in enumerate(coins):
        if not coin_collected[i]:
            pygame.draw.circle(
                screen,
                COIN_COLOR,
                coin.center,
                10,
            )
            pygame.draw.circle(
                screen,
                (255, 245, 180),
                coin.center,
                4,
            )

    # Draw spikes
    for spike in spikes:
        points = [
            (spike.left, spike.bottom),
            (spike.centerx, spike.top),
            (spike.right, spike.bottom),
        ]

        pygame.draw.polygon(
            screen, SPIKE_COLOR, points
        )

    # Draw goal and player
    pygame.draw.rect(
        screen, GOAL_COLOR, goal
    )

    pygame.draw.rect(
        screen, PLAYER_COLOR, player,
        border_radius=6,
    )

    # --------------------------------------------------
    # 16. HUD
    # --------------------------------------------------

    screen.blit(
        font.render(
            f"Coins: {score}/{len(coins)}",
            True,
            TEXT_COLOR,
        ),
        (20, 15),
    )

    screen.blit(
        font.render(
            f"Lives: {lives}",
            True,
            TEXT_COLOR,
        ),
        (20, 48),
    )

    screen.blit(
        small_font.render(
            f"Action: {action_id} - "
            f"{ACTION_NAMES[action_id]}",
            True,
            TEXT_COLOR,
        ),
        (20, 82),
    )

    screen.blit(
        small_font.render(
            f"AI: {'ON' if ai_enabled else 'OFF'} (press I to toggle)",
            True,
            COIN_COLOR if ai_enabled else TEXT_COLOR,
        ),
        (20, 105),
    )

    screen.blit(
        small_font.render(
            "Move: A/D or arrows | Jump: W/Space | AI: I | Restart: R",
            True,
            TEXT_COLOR,
        ),
        (20, HEIGHT - 28),
    )


    # --------------------------------------------------
    # LIVE NEURAL NETWORK PREVIEW (top-right corner)
    # --------------------------------------------------

    panel = pygame.Rect(610, 12, 278, 205)
    pygame.draw.rect(screen, (17, 22, 35), panel, border_radius=8)
    pygame.draw.rect(screen, (70, 90, 120), panel, 1, border_radius=8)

    screen.blit(
        small_font.render("NEURAL NETWORK", True, (100, 220, 200)),
        (panel.x + 10, panel.y + 7),
    )
    screen.blit(
        pygame.font.Font(None, 18).render(
            "LIVE FORWARD PASS | UNTRAINED",
            True, (220, 180, 100)
        ),
        (panel.x + 10, panel.y + 29),
    )

    # Three layers: 8 inputs, 6 hidden neurons, 6 action outputs.
    layer_x = [panel.x + 24, panel.x + 137, panel.x + 250]
    layer_y = [
        [panel.y + 64 + i * 16 for i in range(8)],
        [panel.y + 75 + i * 23 for i in range(6)],
        [panel.y + 75 + i * 23 for i in range(6)],
    ]

    # Connections glow more strongly as the connected activation grows.
    for left_layer in range(2):
        left_values = (
            network_view["inputs"] if left_layer == 0
            else network_view["hidden"]
        )
        right_values = (
            network_view["hidden"] if left_layer == 0
            else network_view["outputs"]
        )
        for i, y1 in enumerate(layer_y[left_layer]):
            for j, y2 in enumerate(layer_y[left_layer + 1]):
                strength = abs(left_values[i] * right_values[j])
                shade = int(45 + min(1.0, strength) * 110)
                pygame.draw.line(
                    screen, (shade // 2, shade, shade),
                    (layer_x[left_layer], y1),
                    (layer_x[left_layer + 1], y2), 1
                )

    for layer_index, values in enumerate((
        network_view["inputs"], network_view["hidden"], network_view["outputs"]
    )):
        for i, value in enumerate(values):
            x = layer_x[layer_index]
            y = layer_y[layer_index][i]
            strength = int(80 + abs(value) * 175)
            if layer_index == 2 and i == network_view["predicted_action"]:
                color = (255, 205, 80)
            elif value >= 0:
                color = (30, strength, 150)
            else:
                color = (180, 70, strength)
            pygame.draw.circle(screen, color, (x, y), 5)
            pygame.draw.circle(screen, (210, 220, 235), (x, y), 5, 1)

    # Tiny layer labels and current output prediction.
    mini_font = pygame.font.Font(None, 16)
    screen.blit(mini_font.render("IN", True, TEXT_COLOR), (panel.x + 8, panel.y + 48))
    screen.blit(mini_font.render("HIDDEN", True, TEXT_COLOR), (panel.x + 111, panel.y + 48))
    screen.blit(mini_font.render("ACTIONS", True, TEXT_COLOR), (panel.x + 220, panel.y + 48))
    predicted_name = ACTION_NAMES[network_view["predicted_action"]]
    screen.blit(
        mini_font.render(f"NN guess: {predicted_name}", True, (255, 205, 80)),
        (panel.x + 10, panel.y + 185),
    )

    # --------------------------------------------------
    # 17. WIN / GAME OVER SCREEN
    # --------------------------------------------------

    if game_won or game_over:

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA,
        )

        overlay.fill((0, 0, 0, 175))
        screen.blit(overlay, (0, 0))

        if game_won:
            message = "YOU WIN!"
            message_color = COIN_COLOR
        else:
            message = "GAME OVER"
            message_color = SPIKE_COLOR

        message_text = font.render(
            message, True, message_color
        )

        screen.blit(
            message_text,
            message_text.get_rect(
                center=(WIDTH // 2, 130)
            ),
        )

        if restart_button.collidepoint(mouse_position):
            button_color = BUTTON_HOVER_COLOR
        else:
            button_color = BUTTON_COLOR

        pygame.draw.rect(
            screen,
            button_color,
            restart_button,
            border_radius=10,
        )

        button_text = font.render(
            "RESTART", True, TEXT_COLOR
        )

        screen.blit(
            button_text,
            button_text.get_rect(
                center=restart_button.center
            ),
        )

        hint = small_font.render(
            "Click Restart or press R",
            True,
            TEXT_COLOR,
        )

        screen.blit(
            hint,
            hint.get_rect(
                center=(WIDTH // 2, 250)
            ),
        )

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
