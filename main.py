import pygame
pygame.init()

#i am starting with creating a game window here
WIDTH = 900
HEIGHT = 500
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Experiment 1 - Merio")

BACKGROUND = (25,30,45)
PLAYER_COLOR = (15,200,160)

# i am defining the varibales here ~ this is a human made comment not AI XD

player = pygame.Rect(100,350,40,40)
ground = pygame.Rect(0,430,WIDTH,70)
coin = pygame.Rect(400, 390, 20, 20)

goal = pygame.Rect(850, 370, 25, 60)
game_won = False

score = 0
coin_collected = False

platforms = [
    pygame.Rect(230, 340, 150, 20),
    pygame.Rect(460, 270, 150, 20),
    pygame.Rect(700, 340, 130, 20)
]


clock = pygame.time.Clock()
gravity = 0.5
jump_strength = -12
velocity_y = 0
running = True

font = pygame.font.Font(None, 36)

while running:
    jump_requested = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_UP, pygame.K_SPACE):
                jump_requested = True

    # i am defining the keys here _ meow 
    keys = pygame.key.get_pressed()
    
    # Horizontal movement
    action = 0

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        action = -1

    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        action = 1

    dx = action * 5

    if game_won:
        dx = 0


    player.x += dx

    for platform in platforms + [ground]:
        if player.colliderect(platform):
            if dx > 0:
                player.right = platform.left
            elif dx < 0:
                player.left = platform.right

    # Vertical movement
    previous_top = player.top
    previous_bottom = player.bottom

    velocity_y += gravity
    player.y += int(velocity_y)

    on_surface = False

    for platform in platforms + [ground]:

        # Landing on a platform
        if (player.right > platform.left and
            player.left < platform.right and
            previous_bottom <= platform.top and
            player.bottom >= platform.top and
            velocity_y > 0):

            player.bottom = platform.top
            velocity_y = 0
            on_surface = True

        # Hitting the underside
        elif (player.right > platform.left and
              player.left < platform.right and
              previous_top >= platform.bottom and
              player.top <= platform.bottom and
              velocity_y < 0):

            player.top = platform.bottom
            velocity_y = 0

        if player.colliderect(goal) and not game_won:
            game_won = True
            print("You win!")

    # Jumping
    if jump_requested and on_surface:
        velocity_y = jump_strength
        
    # Game state for AI
    state = [ player.x, player.y, velocity_y ]
 
    # defining colour and all for already declared elements
    screen.fill (BACKGROUND)
    pygame.draw.rect(screen, PLAYER_COLOR ,player)
    pygame.draw.rect(screen , (100,110,130), ground)

    if player.colliderect(coin) and not coin_collected:
        score += 1
        coin_collected = True
        print("Score:", score)
    
    if not coin_collected:
        pygame.draw.circle(screen, (255, 215, 0), coin.center, 10)
    
    for platform in platforms:
        pygame.draw.rect(screen, (130,150,230), platform)

    score_text = font.render(f"Coins: {score}", True, (255, 255, 255))
    screen.blit(score_text, (20, 20))

    if game_won:
        win_text = font.render("YOU WIN!", True, (255, 215, 0))
        screen.blit(win_text, (350, 100))

    pygame.draw.rect(screen, (255, 100, 100), goal)

    pygame.display.flip()
    clock.tick(60)
pygame.quit()  