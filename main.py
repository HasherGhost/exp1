
import pygame

pygame.init()

# --------------------------------------------------
# 1. GAME WINDOW
# --------------------------------------------------

WIDTH = 900
HEIGHT = 500

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Experiment 1 - Merio")

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
TEXT_COLOR = (255, 255, 255)

BUTTON_COLOR = (50, 160, 110)
BUTTON_HOVER_COLOR = (65, 195, 135)
BUTTON_TEXT_COLOR = (255, 255, 255)

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
# 4. GAME OBJECTS
# --------------------------------------------------

player = pygame.Rect(
    PLAYER_START_X, PLAYER_START_Y, 40, 40
)

ground = pygame.Rect(0, 430, WIDTH, 70)

coin = pygame.Rect(400, 390, 20, 20)

goal = pygame.Rect(850, 370, 25, 60)

platforms = [
    pygame.Rect(230, 340, 150, 20),
    pygame.Rect(460, 270, 150, 20),
    pygame.Rect(700, 340, 130, 20),
]

solid_surfaces = platforms + [ground]

# Restart button
restart_button = pygame.Rect(350, 160, 200, 50)

# --------------------------------------------------
# 5. GAME VARIABLES
# --------------------------------------------------

velocity_y = 0.0

on_surface = False
game_won = False

score = 0
coin_collected = False

running = True
action_id = NO_ACTION

# --------------------------------------------------
# 6. RESTART FUNCTION
# --------------------------------------------------

def restart_game():
    global player, velocity_y, on_surface
    global game_won, score, coin_collected, action_id

    player = pygame.Rect(
        PLAYER_START_X, PLAYER_START_Y, 40, 40
    )

    velocity_y = 0.0
    on_surface = False

    game_won = False
    score = 0
    coin_collected = False

    action_id = NO_ACTION

    print("Game restarted!")


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

        # Keyboard events
        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key == pygame.K_r:
                restart_game()

            elif event.key in (
                pygame.K_w,
                pygame.K_UP,
                pygame.K_SPACE,
            ):
                jump_requested = True

        # Mouse events
        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1 and game_won:

                if restart_button.collidepoint(event.pos):
                    restart_game()

    # --------------------------------------------------
    # 9. SELECT AN ACTION
    # --------------------------------------------------

    keys = pygame.key.get_pressed()

    moving_left = (
        keys[pygame.K_LEFT] or keys[pygame.K_a]
    )

    moving_right = (
        keys[pygame.K_RIGHT] or keys[pygame.K_d]
    )

    action_id = NO_ACTION

    if moving_left and not moving_right:
        action_id = MOVE_LEFT

    elif moving_right and not moving_left:
        action_id = MOVE_RIGHT

    # Combine horizontal movement with jumping
    if jump_requested:

        if action_id == MOVE_LEFT:
            action_id = LEFT_JUMP

        elif action_id == MOVE_RIGHT:
            action_id = RIGHT_JUMP

        else:
            action_id = JUMP

    # Convert the action ID into physics controls
    action = 0

    if action_id in (MOVE_LEFT, LEFT_JUMP):
        action = -1

    elif action_id in (MOVE_RIGHT, RIGHT_JUMP):
        action = 1

    jump_requested = action_id in (
        JUMP,
        LEFT_JUMP,
        RIGHT_JUMP,
    )

    # Stop movement after winning
    if game_won:
        action = 0
        jump_requested = False

    dx = action * PLAYER_SPEED

    # --------------------------------------------------
    # 10. HORIZONTAL MOVEMENT
    # --------------------------------------------------

    player.x += dx

    # Keep the player inside the window
    if player.left < 0:
        player.left = 0

    if player.right > WIDTH:
        player.right = WIDTH

    # Resolve horizontal collisions
    for platform in solid_surfaces:

        if player.colliderect(platform):

            if dx > 0:
                player.right = platform.left

            elif dx < 0:
                player.left = platform.right

    # --------------------------------------------------
    # 11. VERTICAL MOVEMENT AND COLLISIONS
    # --------------------------------------------------

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

        # Landing on a platform
        if (
            velocity_y > 0
            and previous_bottom <= platform.top
            and player.bottom >= platform.top
        ):
            player.bottom = platform.top
            velocity_y = 0.0
            on_surface = True

        # Hitting the underside of a platform
        elif (
            velocity_y < 0
            and previous_top >= platform.bottom
            and player.top <= platform.bottom
        ):
            player.top = platform.bottom
            velocity_y = 0.0

    # --------------------------------------------------
    # 12. JUMPING
    # --------------------------------------------------

    if jump_requested and on_surface and not game_won:
        velocity_y = JUMP_STRENGTH
        on_surface = False

    # --------------------------------------------------
    # 13. COIN COLLECTION
    # --------------------------------------------------

    if (
        player.colliderect(coin)
        and not coin_collected
    ):
        coin_collected = True
        score += 1

        print("Score:", score)

    # --------------------------------------------------
    # 14. GOAL DETECTION
    # --------------------------------------------------

    if player.colliderect(goal) and not game_won:
        game_won = True
        print("You win!")

    # --------------------------------------------------
    # 15. GAME STATE FOR FUTURE AI
    # --------------------------------------------------

    # Original seven state values are preserved.
    # Three additional flags describe the game situation.

    state = [
        player.x,
        player.y,
        velocity_y,
        coin.x,
        coin.y,
        goal.x,
        goal.y,
        int(coin_collected),
        int(on_surface),
        int(game_won),
    ]

    # action_id represents the action chosen this frame.
    # Later, an AI controller can choose this ID.

    # --------------------------------------------------
    # 16. DRAW THE GAME
    # --------------------------------------------------

    screen.fill(BACKGROUND)

    # Ground and platforms
    pygame.draw.rect(
        screen, GROUND_COLOR, ground
    )

    for platform in platforms:
        pygame.draw.rect(
            screen, PLATFORM_COLOR, platform
        )

    # Coin
    if not coin_collected:
        pygame.draw.circle(
            screen, COIN_COLOR, coin.center, 10
        )

    # Goal and player
    pygame.draw.rect(
        screen, GOAL_COLOR, goal
    )

    pygame.draw.rect(
        screen, PLAYER_COLOR, player
    )

    # Score display
    score_text = font.render(
        f"Coins: {score}",
        True,
        TEXT_COLOR,
    )

    screen.blit(score_text, (20, 20))

    # Debug information for future AI development
    action_text = small_font.render(
        f"Action: {action_id} - {ACTION_NAMES[action_id]}",
        True,
        TEXT_COLOR,
    )

    screen.blit(action_text, (20, 55))

    # --------------------------------------------------
    # 17. WIN SCREEN AND RESTART BUTTON
    # --------------------------------------------------

    if game_won:

        # Dark overlay
        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA,
        )

        overlay.fill((0, 0, 0, 110))
        screen.blit(overlay, (0, 0))

        win_text = font.render(
            "YOU WIN!",
            True,
            COIN_COLOR,
        )

        screen.blit(
            win_text,
            win_text.get_rect(
                center=(WIDTH // 2, 125)
            ),
        )

        # Button hover effect
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
            "RESTART",
            True,
            BUTTON_TEXT_COLOR,
        )

        screen.blit(
            button_text,
            button_text.get_rect(
                center=restart_button.center
            ),
        )

        hint_text = small_font.render(
            "Click Restart or press R",
            True,
            TEXT_COLOR,
        )

        screen.blit(
            hint_text,
            hint_text.get_rect(
                center=(WIDTH // 2, 230)
            ),
        )

    pygame.display.flip()
    clock.tick(60)

# --------------------------------------------------
# 18. EXIT
# --------------------------------------------------

pygame.quit()
