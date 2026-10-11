"""Generate Merio's original pixel-art PNG assets with Pygame.

Run automatically from main.py if assets are missing, or manually with:
    python -m assets.generate_assets
"""
from pathlib import Path
import pygame

ASSET_DIR = Path(__file__).resolve().parent


def surface(size, color=(0, 0, 0, 0)):
    image = pygame.Surface(size, pygame.SRCALPHA)
    image.fill(color)
    return image


def save(image, name):
    pygame.image.save(image, ASSET_DIR / name)


def make_assets():
    pygame.init()

    # Sky tile with subtle pixel clouds; main.py paints a sky gradient too.
    sky = surface((160, 100), (119, 205, 255, 255))
    pygame.draw.rect(sky, (170, 225, 255), (0, 0, 160, 20))
    pygame.draw.rect(sky, (105, 190, 250), (0, 78, 160, 22))
    save(sky, "sky.png")

    cloud = surface((96, 44))
    for rect in [(18, 17, 30, 19), (34, 7, 34, 28), (54, 15, 26, 21), (9, 22, 68, 15)]:
        pygame.draw.rect(cloud, (255, 255, 255), rect)
    pygame.draw.rect(cloud, (224, 244, 255), (15, 30, 56, 7))
    save(cloud, "cloud.png")

    # Seamless grass-and-soil tile.
    ground = surface((64, 48), (151, 91, 48))
    pygame.draw.rect(ground, (91, 190, 68), (0, 0, 64, 12))
    pygame.draw.rect(ground, (57, 151, 53), (0, 8, 64, 4))
    for x, y in [(5, 20), (23, 30), (45, 18), (56, 39), (13, 42), (35, 39)]:
        pygame.draw.rect(ground, (119, 67, 39), (x, y, 5, 4))
    for x, y in [(10, 15), (31, 22), (52, 28), (40, 10)]:
        pygame.draw.rect(ground, (181, 116, 61), (x, y, 4, 3))
    save(ground, "ground.png")

    platform = surface((64, 24), (157, 102, 55))
    pygame.draw.rect(platform, (96, 195, 67), (0, 0, 64, 8))
    pygame.draw.rect(platform, (56, 145, 48), (0, 6, 64, 4))
    pygame.draw.rect(platform, (190, 132, 74), (0, 10, 64, 2))
    pygame.draw.rect(platform, (116, 71, 43), (0, 21, 64, 3))
    save(platform, "platform.png")

    brick = surface((32, 32), (191, 78, 48))
    pygame.draw.rect(brick, (240, 139, 77), (1, 1, 30, 5))
    pygame.draw.rect(brick, (123, 52, 43), (0, 15, 32, 2))
    pygame.draw.rect(brick, (123, 52, 43), (15, 0, 2, 15))
    pygame.draw.rect(brick, (123, 52, 43), (7, 17, 2, 15))
    pygame.draw.rect(brick, (123, 52, 43), (24, 17, 2, 15))
    save(brick, "brick.png")

    question = surface((32, 32), (244, 174, 45))
    pygame.draw.rect(question, (255, 222, 91), (2, 2, 28, 28))
    pygame.draw.rect(question, (164, 94, 31), (0, 0, 32, 2))
    pygame.draw.rect(question, (164, 94, 31), (0, 30, 32, 2))
    pygame.draw.rect(question, (164, 94, 31), (0, 0, 2, 32))
    pygame.draw.rect(question, (164, 94, 31), (30, 0, 2, 32))
    pygame.draw.rect(question, (255, 255, 218), (12, 6, 8, 4))
    pygame.draw.rect(question, (255, 255, 218), (18, 10, 5, 5))
    pygame.draw.rect(question, (255, 255, 218), (13, 15, 6, 4))
    pygame.draw.rect(question, (255, 255, 218), (13, 23, 6, 4))
    save(question, "question_block.png")

    # Player: original red-cap adventurer, not a Mario sprite.
    player = surface((32, 40))
    pygame.draw.rect(player, (116, 66, 37), (7, 3, 19, 8))
    pygame.draw.rect(player, (218, 56, 52), (5, 2, 23, 8))
    pygame.draw.rect(player, (255, 104, 73), (9, 0, 15, 5))
    pygame.draw.rect(player, (245, 190, 135), (9, 10, 17, 13))
    pygame.draw.rect(player, (35, 42, 62), (20, 13, 3, 4))
    pygame.draw.rect(player, (53, 107, 214), (7, 23, 19, 11))
    pygame.draw.rect(player, (35, 67, 151), (7, 31, 19, 4))
    pygame.draw.rect(player, (96, 57, 43), (5, 35, 11, 5))
    pygame.draw.rect(player, (96, 57, 43), (19, 35, 11, 5))
    pygame.draw.rect(player, (255, 220, 164), (4, 13, 5, 10))
    pygame.draw.rect(player, (255, 220, 164), (25, 13, 4, 10))
    save(player, "player.png")

    coin = surface((24, 24))
    pygame.draw.ellipse(coin, (157, 95, 18), (3, 1, 18, 22))
    pygame.draw.ellipse(coin, (255, 204, 44), (5, 1, 14, 22))
    pygame.draw.rect(coin, (255, 240, 135), (8, 4, 4, 15))
    pygame.draw.rect(coin, (255, 240, 135), (12, 4, 3, 3))
    save(coin, "coin.png")

    # Pipe, enemy, spike, flag, and decorative hill.
    pipe = surface((64, 88), (41, 174, 70))
    pygame.draw.rect(pipe, (23, 116, 55), (7, 14, 50, 74))
    pygame.draw.rect(pipe, (77, 220, 92), (14, 17, 11, 68))
    pygame.draw.rect(pipe, (19, 128, 59), (0, 7, 64, 22))
    pygame.draw.rect(pipe, (94, 234, 107), (5, 10, 12, 15))
    pygame.draw.rect(pipe, (18, 98, 50), (54, 11, 6, 14))
    save(pipe, "pipe.png")

    enemy = surface((32, 28))
    pygame.draw.ellipse(enemy, (143, 75, 43), (1, 3, 30, 23))
    pygame.draw.rect(enemy, (105, 48, 36), (4, 20, 9, 6))
    pygame.draw.rect(enemy, (105, 48, 36), (20, 20, 9, 6))
    pygame.draw.rect(enemy, (255, 255, 255), (7, 8, 7, 8))
    pygame.draw.rect(enemy, (255, 255, 255), (19, 8, 7, 8))
    pygame.draw.rect(enemy, (35, 32, 42), (10, 10, 3, 5))
    pygame.draw.rect(enemy, (35, 32, 42), (21, 10, 3, 5))
    save(enemy, "enemy.png")

    spike = surface((32, 24))
    pygame.draw.polygon(spike, (205, 224, 235), [(0, 24), (9, 3), (15, 24)])
    pygame.draw.polygon(spike, (205, 224, 235), [(11, 24), (23, 0), (32, 24)])
    pygame.draw.polygon(spike, (103, 126, 148), [(9, 3), (12, 24), (15, 24)])
    pygame.draw.polygon(spike, (103, 126, 148), [(23, 0), (26, 24), (32, 24)])
    save(spike, "spike.png")

    flag = surface((48, 144))
    pygame.draw.rect(flag, (226, 235, 241), (8, 0, 5, 144))
    pygame.draw.rect(flag, (173, 187, 201), (5, 139, 13, 5))
    pygame.draw.polygon(flag, (239, 70, 82), [(13, 7), (44, 18), (13, 34)])
    pygame.draw.rect(flag, (255, 255, 255), (15, 15, 9, 5))
    save(flag, "flag.png")

    hill = surface((220, 110))
    pygame.draw.ellipse(hill, (84, 190, 109), (0, 10, 220, 100))
    pygame.draw.ellipse(hill, (113, 211, 124), (26, 32, 156, 75))
    save(hill, "hill.png")

    print("Generated Merio assets in:", ASSET_DIR)


def ensure_assets():
    required = [
        "sky.png", "cloud.png", "ground.png", "platform.png", "brick.png",
        "question_block.png", "player.png", "coin.png", "pipe.png",
        "enemy.png", "spike.png", "flag.png", "hill.png",
    ]
    if not all((ASSET_DIR / name).exists() for name in required):
        make_assets()


if __name__ == "__main__":
    make_assets()
