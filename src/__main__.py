import pygame
import sys

from . import sprite_groups, constants, sprites, levels

# TODO!: create menu
# TODO!: create ico
# TODO: star boss

pygame.init()
screen = pygame.display.set_mode((1200, 800))
width, height = screen.get_size()
x_tiles = width // constants.TILE_SIZE
y_tiles = height // constants.TILE_SIZE

clock = pygame.time.Clock()

left_border = sprites.Border(0, 0, 0, height)
right_border = sprites.Border(width, 0, width, height)
up_border = sprites.Border(0, 0, width, 0)
down_border = sprites.Border(0, height, width, height)

level = levels.FirstLevel(x_tiles, y_tiles)
level_sprites = level.create()

player = sprites.Player()
player.rect.move_ip(*level.start_point())
level.player = player

brick = sprites.GroundTile(level)
brick.rect.move_ip(200, height - 300)
brick.speed.y = 2

brick2 = sprites.GroundTile(level)
brick2.rect.move_ip(width - 200, height - 600)
brick2.speed.y = 2

brick3 = sprites.GroundTile(level)
brick3.rect.move_ip(400, height - 300)
brick3.speed.y = 2


while True:
    for event in pygame.event.get():
        if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
            sys.exit()
        elif event.type == pygame.QUIT:
            sys.exit()
        elif event.type in (pygame.KEYUP, pygame.KEYDOWN):
            player.on_keyboard(event)

    sprite_groups.TILES.draw(screen)
    sprite_groups.TILES.update()

    sprite_groups.WALLS.draw(screen)
    sprite_groups.WALLS.update()

    sprite_groups.CHARACTERS.draw(screen)
    sprite_groups.CHARACTERS.update(level)

    clock.tick(60)
    pygame.display.flip()
    screen.fill((0, 0, 0))
