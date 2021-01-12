import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
            sys.exit()

    clock.tick(60)
    pygame.display.flip()
