import pygame
import pygame_gui


class GameMenu(pygame_gui.UIManager):

    # TODO: menu design
    # TODO: move all button text into constants
    #       make simple stylesheet for buttons
    #       center menu
    #       no textures, just a black screen (may be??)
    def __init__(self, game):
        super().__init__((game.width, game.height))
        self.game = game
        self.exit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, 200), (300, 100)),
            text="Exit",
            manager=self
        )
        self.reset_level_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, 100), (300, 100)),
            text="Reset level",
            manager=self
        )
        self.next_level_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((10, 0), (300, 100)),
            text="Next level",
            manager=self
        )
        # self.reset_level_button.hide()
        # self.reset_level_button.show()

    def process_events(self, event: pygame.event.Event):
        super().process_events(event)

        if event.type != pygame.USEREVENT or event.user_type != pygame_gui.UI_BUTTON_PRESSED:
            return

        if event.ui_element == self.exit_button:
            self.game.exit_game()
        elif event.ui_element == self.reset_level_button:
            if self.game.current_level is not None:
                self.game.start_level()
                self.game.is_paused = False
        elif event.ui_element == self.next_level_button:
            self.game.is_paused = False
            self.game.next_level()
