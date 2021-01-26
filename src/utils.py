import pygame
from pathlib import Path

ASSETS_PATH = Path(__file__).parent / "../assets"


def load_image_from_path(path):
    return pygame.image.load(str(path.resolve()))


def load_image(filename):
    asset_path = ASSETS_PATH / "sprites" / filename
    return load_image_from_path(asset_path)

