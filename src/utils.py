import pygame

from pathlib import Path
from . import constants

ASSETS_PATH = Path(__file__).parent / "../assets"


def load_image_from_path(path):
    return pygame.image.load(str(path.resolve()))


def load_image(filename):
    asset_path = ASSETS_PATH / "sprites" / filename
    return load_image_from_path(asset_path)


def find(predicate, seq):
    for item in seq:
        if predicate(seq):
            return item


def tile_point(x, y):
    return [x * constants.TILE_SIZE, y * constants.TILE_SIZE]
