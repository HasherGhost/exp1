import pygame
pygame.init()

#i am starting with creating a game window here
WIDTH = 900
HEIGHT = 500
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("AI Platformer - Experiment 1")

BACKGROUND = (25,30,45)
PLAYER_COLOR = (15,200,160)

player = pygame.Rect(100,350,40,40)
ground = pygame.Rect(0,430,WIDTH,70)

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player.x -= 5
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player.x += 5
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        player.y -= 5
    if keys[pygame.K_DOWN] or keys[pygame.K_s]: 
        player.y += 5

    screen.fill (BACKGROUND)
    pygame.draw.rect(screen, PLAYER_COLOR ,player)

    pygame.display.flip()
    clock.tick(60)
pygame.quit()  