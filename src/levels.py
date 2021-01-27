import pygame

from . import sprites, constants


class Level(pygame.sprite.Group):

    def __init__(self, x_tiles, y_tiles):
        super().__init__()
        self.x_tiles = x_tiles
        self.y_tiles = y_tiles
        self.start_tile = (0, 0)
        self.player = None

    def schema(self):
        raise NotImplementedError()

    def create(self):
        raise NotImplementedError()

    def kill(self):
        raise NotImplementedError()


class FirstLevel(Level):

    def __init__(self, *args):
        super().__init__(*args)
        self.start_tile = (1, self.y_tiles - 2)

    def start_point(self):
        return (self.start_tile[0] * constants.TILE_SIZE, self.start_tile[1] * constants.TILE_SIZE)

    def schema(self):
        schema = [
            [sprites.GroundTile] * (self.x_tiles // 2) + [sprites.BackgroundTile] * (self.x_tiles // 2),

            *([sprites.BackgroundTile] * self.x_tiles
              for _ in range(5)),

            [sprites.BackgroundTile] * (self.x_tiles // 2) + [sprites.GroundTile] * (self.x_tiles // 2),

            *([sprites.BackgroundTile] * self.x_tiles
              for _ in range(5)),

            [sprites.GroundTile] * self.x_tiles
        ]

        return [
            *([sprites.BackgroundTile] * self.x_tiles
              for _ in range(self.y_tiles - len(schema)))
        ] + schema

    def create(self):
        sprites = []
        schema = self.schema()

        for row in schema:
            sprites_row = []

            for sprite_cls in row:
                sprite = sprite_cls()
                self.add(sprite)
                sprites_row.append(sprite)

            sprites.append(sprites_row)

        for x in range(self.x_tiles):
            for y in range(self.y_tiles):
                sprite = sprites[y][x]
                sprite.mass = 0
                sprite.rect.move_ip(x * constants.TILE_SIZE, y * constants.TILE_SIZE)

        return sprites

    def kill(self):
        for sprite in self:
            sprite.kill()
