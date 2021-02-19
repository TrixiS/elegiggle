import pygame
import pygame_gui


class GameMenu(pygame_gui.UIManager):

    # TODO: menu design
    # TODO: move all button text into constants
    #       make simple stylesheet for buttons
    #       center menu
    #       no textures, just a black screen (may be??)
    def __init__(self, size):
        super().__init__(size)
        self.width, self.height = size
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
