import pygame

from . import levels, constants, utils
from .game import Game

pygame.init()
pygame.font.init()
pygame.display.set_caption(constants.WINDOW_TITLE)
pygame.display.set_icon(utils.load_image("../icon.png"))
screen = pygame.display.set_mode((1200, 800))

game = Game(screen)
game.add_level(levels.FirstLevel(game))
game.add_level(levels.SecondLevel(game))
game.start_game()
