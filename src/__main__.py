import pygame

from . import levels
from .game import Game

# TODO!: create menu
# TODO!: create ico
# TODO: star boss

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((1200, 800))

game = Game(screen)
game.add_level(levels.FirstLevel(game))
game.add_level(levels.SecondLevel(game))
game.start_game()
