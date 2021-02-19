import sys
import pygame

from . import game_objects, sprite_groups, constants
from .game_menu import GameMenu


class NextList(list):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_next_index = 0

    def __next__(self):
        try:
            element = self[self.current_next_index]
            self.current_next_index += 1
            return element
        except IndexError:
            self.current_next_index = 0


class Game:

    def __init__(self, screen):
        self.levels = NextList()
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.x_tiles = self.width // constants.TILE_SIZE
        self.y_tiles = self.height // constants.TILE_SIZE
        self.menu = GameMenu(self)
        self.is_paused = True
        self.current_level = None
        self.clock = pygame.time.Clock()
        self.player = None
        self.left_border = game_objects.Border(0, 0, 0, self.height)
        self.right_border = game_objects.Border(self.width, 0, self.width, self.height)
        self.up_border = game_objects.Border(0, 0, self.width, 0)
        self.down_border = game_objects.Border(0, self.height, self.width, self.height)

    def add_level(self, level):
        self.levels.append(level)

    def start_level(self):
        if self.player is not None and self.player.alive:
            self.player.kill()

        self.player = game_objects.Player()
        self.current_level.kill()
        self.current_level.player = self.player
        self.player.rect.x, self.player.rect.y = self.current_level.start_point()
        self.current_level.create()

    def next_level(self):
        if self.current_level is not None:
            self.current_level.kill()

        self.current_level = next(self.levels)

        if self.current_level is None:
            self.is_paused = True
        else:
            self.start_level()

    def toggle_pause(self):
        self.is_paused = not self.is_paused

    def exit_game(self):
        sys.exit()

    def start_game(self):
        while True:
            time_delta = self.clock.tick(constants.GAME_FPS) / 1000
            keys = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_game()

                if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                    if self.current_level is None:
                        self.next_level()

                    self.toggle_pause()

                if self.is_paused:
                    self.menu.process_events(event)
                else:
                    if event.type in (pygame.KEYUP, pygame.KEYDOWN):
                        self.player.on_keyboard(event=event)

            if self.is_paused:
                self.menu.update(time_delta)
                self.menu.draw_ui(self.screen)
            else:
                if not self.player.alive:
                    self.is_paused = True
                    continue

                self.player.on_keyboard(keys=keys)
                self.current_level.draw(self.screen)
                self.current_level.update(self.screen)
                sprite_groups.PLAYERS.draw(self.screen)
                sprite_groups.PLAYERS.update(self.screen)

            pygame.display.flip()
            self.screen.fill((0, 0, 0))
