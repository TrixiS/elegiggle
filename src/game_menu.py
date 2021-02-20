import pygame
import pygame_gui

from . import constants


class GameMenu(pygame_gui.UIManager):

    def __init__(self, game):
        super().__init__((game.width, game.height))
        self.game = game
        button_width = 300
        button_height = 100
        center_x = game.width // 2
        center_y = game.width // 2

        self.return_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                (center_x - button_width // 2, center_y - button_height // 2 - 300),
                (button_width, button_height)),
            text=constants.RETURN_TO_GAME,
            manager=self
        )
        self.reset_level_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                (center_x - button_width // 2, center_y - button_height // 2 - 200),
                (button_width, button_height)),
            text=constants.RESET_LEVEL,
            manager=self
        )
        self.exit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                (center_x - button_width // 2, center_y - button_height // 2 - 100),
                (button_width, button_height)),
            text=constants.EXIT_GAME,
            manager=self
        )

    def process_events(self, event: pygame.event.Event):
        super().process_events(event)

        if event.type != pygame.USEREVENT or event.user_type != pygame_gui.UI_BUTTON_PRESSED:
            return

        if event.ui_element == self.exit_button:
            self.game.exit_game()
        elif event.ui_element == self.reset_level_button:
            if self.game.current_level is not None:
                self.game.start_level()
                self.game.toggle_pause()
        elif event.ui_element == self.return_button:
            self.game.toggle_pause()

    def draw_ui(self, window_surface: pygame.surface.Surface):
        super().draw_ui(window_surface)

        if self.game.player.alive:
            self.return_button.show()
        else:
            self.return_button.hide()
