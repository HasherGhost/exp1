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

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # i am defining the keys here _ meow 

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player.x -= 5
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player.x += 5

    previous_bottom = player.bottom

    velocity_y += gravity
    player.y += int(velocity_y)

    on_surface = False

    for platform in platforms + [ground]:
        if (player.right > platform.left and
            player.left < platform.right and
            previous_bottom <= platform.top and
            player.bottom >= platform.top and
            velocity_y >= 0):
            platform.bottom = platform.top
            velocity_y = 0
            on_surface = True

    if (keys[pygame.K_w] or
         keys[pygame.K_UP] or
          keys[pygame.K_SPACE] ) and (on_surface == True):
        velocity_y = jump_strength
    
    # defining colour and all for already declared elements
    screen.fill (BACKGROUND)
    pygame.draw.rect(screen, PLAYER_COLOR ,player)
    pygame.draw.rect(screen , (100,110,130), ground)
    for platform in platforms:
        pygame.draw.rect(screen, (130,150,230), platform)

    pygame.display.flip()
    clock.tick(60)
pygame.quit()  