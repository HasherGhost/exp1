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

# --------------------------------------------------
# 3. GAME OBJECTS
# --------------------------------------------------

player = pygame.Rect(100, 350, 40, 40)

ground = pygame.Rect(0, 430, WIDTH, 70)

coin = pygame.Rect(400, 390, 20, 20)

goal = pygame.Rect(850, 370, 25, 60)

platforms = [
    pygame.Rect(230, 340, 150, 20),
    pygame.Rect(460, 270, 150, 20),
    pygame.Rect(700, 340, 130, 20)
]

# --------------------------------------------------
# 4. GAME VARIABLES
# --------------------------------------------------

gravity = 0.5
jump_strength = -12
velocity_y = 0.0
player_speed = 5

on_surface = False
game_won = False

score = 0
coin_collected = False

running = True

def restart_game():
    global player, velocity_y, on_surface
    global game_won, score, coin_collected

    player = pygame.Rect(100, 350, 40, 40)
    velocity_y = 0.0
    on_surface = False

    game_won = False
    score = 0
    coin_collected = False


# --------------------------------------------------
# 5. ACTION IDs FOR FUTURE AI
# --------------------------------------------------
#
# 0 = Do nothing
# 1 = Move left
# 2 = Move right
# 3 = Jump
# 4 = Move left + jump
# 5 = Move right + jump
#
# For now, the keyboard selects the action.
# Later, an AI agent can select action_id instead.
# --------------------------------------------------

NO_ACTION = 0
MOVE_LEFT = 1
MOVE_RIGHT = 2
JUMP = 3
LEFT_JUMP = 4
RIGHT_JUMP = 5

# --------------------------------------------------
# 6. MAIN GAME LOOP
# --------------------------------------------------

while running:

    jump_requested = False

    # Process events
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key in (
                pygame.K_w,
                pygame.K_UP,
                pygame.K_SPACE
            ):
                jump_requested = True

    # --------------------------------------------------
    # 7. SELECT AN ACTION USING THE KEYBOARD
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

    # Combine jumping with horizontal movement
    if jump_requested:

        if action_id == MOVE_LEFT:
            action_id = LEFT_JUMP

        elif action_id == MOVE_RIGHT:
            action_id = RIGHT_JUMP

        else:
            action_id = JUMP

    # --------------------------------------------------
    # 8. CONVERT ACTION ID INTO MOVEMENT
    # --------------------------------------------------

    action = 0

    if action_id in (MOVE_LEFT, LEFT_JUMP):
        action = -1

    elif action_id in (MOVE_RIGHT, RIGHT_JUMP):
        action = 1

    jump_requested = action_id in (
        JUMP,
        LEFT_JUMP,
        RIGHT_JUMP
    )

    # Stop movement after winning
    if game_won:
        action = 0
        jump_requested = False

    dx = action * player_speed

    # --------------------------------------------------
    # 9. HORIZONTAL MOVEMENT AND COLLISIONS
    # --------------------------------------------------

    player.x += dx

    # Keep the player inside the screen
    if player.left < 0:
        player.left = 0

    if player.right > WIDTH:
        player.right = WIDTH

    solid_surfaces = platforms + [ground]

    for platform in solid_surfaces:

        if player.colliderect(platform):

            if dx > 0:
                player.right = platform.left

            elif dx < 0:
                player.left = platform.right

    # --------------------------------------------------
    # 10. VERTICAL MOVEMENT AND GRAVITY
    # --------------------------------------------------

    previous_top = player.top
    previous_bottom = player.bottom

    velocity_y += gravity
    player.y += int(velocity_y)

    on_surface = False

    for platform in solid_surfaces:

        horizontal_overlap = (
            player.right > platform.left
            and player.left < platform.right
        )

        if not horizontal_overlap:
            continue

        # Landing on a platform while falling
        if (
            velocity_y > 0
            and previous_bottom <= platform.top
            and player.bottom >= platform.top
        ):
            player.bottom = platform.top
            velocity_y = 0
            on_surface = True

        # Hitting the underside while jumping
        elif (
            velocity_y < 0
            and previous_top >= platform.bottom
            and player.top <= platform.bottom
        ):
            player.top = platform.bottom
            velocity_y = 0

    # --------------------------------------------------
    # 11. JUMPING
    # --------------------------------------------------

    if jump_requested and on_surface and not game_won:
        velocity_y = jump_strength
        on_surface = False

    # --------------------------------------------------
    # 12. COIN COLLECTION
    # --------------------------------------------------

    if (
        player.colliderect(coin)
        and not coin_collected
    ):
        score += 1
        coin_collected = True
        print("Score:", score)

    # --------------------------------------------------
    # 13. GOAL DETECTION
    # --------------------------------------------------

    # This check is outside the platform collision loop.
    if player.colliderect(goal) and not game_won:
        game_won = True
        print("You win!")

    # --------------------------------------------------
    # 14. GAME STATE FOR FUTURE AI
    # --------------------------------------------------

    # The original seven values are preserved.
    # Three useful flags have been added at the end.

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
        int(game_won)
    ]

    # The action selected during this frame is action_id.
    # An AI will eventually choose this value automatically.

    # --------------------------------------------------
    # 15. DRAW THE GAME
    # --------------------------------------------------

    screen.fill(BACKGROUND)

    pygame.draw.rect(
        screen,
        GROUND_COLOR,
        ground
    )

    for platform in platforms:
        pygame.draw.rect(
            screen,
            PLATFORM_COLOR,
            platform
        )

    # Draw the coin until it is collected
    if not coin_collected:
        pygame.draw.circle(
            screen,
            COIN_COLOR,
            coin.center,
            10
        )

    pygame.draw.rect(
        screen,
        GOAL_COLOR,
        goal
    )

    pygame.draw.rect(
        screen,
        PLAYER_COLOR,
        player
    )

    # Display score
    score_text = font.render(
        f"Coins: {score}",
        True,
        TEXT_COLOR
    )

    screen.blit(score_text, (20, 20))

    # Display winning message
    if game_won:
        win_text = font.render(
            "YOU WIN!",
            True,
            COIN_COLOR
        )

        screen.blit(win_text, (350, 100))

    pygame.display.flip()
    clock.tick(60)

# --------------------------------------------------
# 16. EXIT
# --------------------------------------------------

pygame.quit()
