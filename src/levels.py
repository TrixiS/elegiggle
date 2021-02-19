import random
import pygame
import abc

from . import game_objects, utils, constants


class Level(pygame.sprite.Group, abc.ABC):

    def __init__(self, game):
        super().__init__()
        self.game = game
        self.x_tiles = game.x_tiles
        self.y_tiles = game.y_tiles
        self.player = None

    @property
    def start_tile(self):
        return 1, self.y_tiles - 2

    @abc.abstractmethod
    def schema(self):
        """
        Схема каждого уровня должна возвращать:
        1. List[List[game_objects.GameObject]]
        2. List[Tuple[game_objects.GameObject, Tuple[int, int]]]
        """
        raise NotImplementedError()

    def start_point(self):
        return utils.tile_point(*self.start_tile)

    def create(self):
        tiles = []
        schema, objects = self.schema()

        for row in schema:
            sprites_row = []

            for sprite_cls in row:
                sprite = sprite_cls()
                self.add(sprite)
                sprites_row.append(sprite)

            tiles.append(sprites_row)

        for x in range(self.x_tiles):
            for y in range(self.y_tiles):
                sprite = tiles[y][x]
                sprite.mass = 0
                sprite.rect.move_ip(*utils.tile_point(x, y))

        for sprite_object, pos in objects:
            self.add(sprite_object)
            sprite_object.rect.x, sprite_object.rect.y = pos

        return tiles, objects

    def kill(self):
        for sprite in self:
            sprite.kill()


class FirstLevel(Level):

    def schema(self):
        schema = [
            [game_objects.GroundTile] * (self.x_tiles // 2) + [game_objects.BackgroundTile] * (self.x_tiles // 2),
            *([game_objects.BackgroundTile] * self.x_tiles
              for _ in range(5)),
            [game_objects.BackgroundTile] * (self.x_tiles // 2) + [game_objects.GroundTile] * (self.x_tiles // 2),
            *([game_objects.BackgroundTile] * self.x_tiles
              for _ in range(5)),
            [game_objects.GroundTile] * self.x_tiles
        ]

        schema = [
            *([game_objects.BackgroundTile] * self.x_tiles
              for _ in range(self.y_tiles - len(schema)))
        ] + schema

        objects = [
            (game_objects.Box(), utils.tile_point(5, self.y_tiles - 5)),
            (game_objects.Box(), utils.tile_point(10, self.y_tiles - 5)),
            (game_objects.Box(), utils.tile_point(self.x_tiles - 4, self.y_tiles - 13)),
            (game_objects.EnemyFrog(), utils.tile_point(self.x_tiles - 6, self.y_tiles - 13)),
            (game_objects.LevelPointer(), utils.tile_point(4, self.y_tiles - 18))
        ]

        return schema, objects


class SecondLevel(Level):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.star_boss = None
        self.star_stones = []
        self.stone_streak = 0
        self.finished = False
        self.sf_font = pygame.font.Font(utils.ASSETS_PATH / "fonts/joysix.ttf", 40)

    @property
    def start_tile(self):
        return self.x_tiles // 2, self.y_tiles - 2

    def kill(self):
        super().kill()
        self.star_boss = None
        self.finished = False
        self.star_stones.clear()

    def schema(self):
        third_level = self.x_tiles // 3

        schema = [
            *([game_objects.BackgroundBrick] * self.x_tiles for _ in range(self.y_tiles - 16)),
            ([game_objects.BackgroundBrick] * third_level + [game_objects.Brick] * third_level +
             [game_objects.BackgroundBrick] * third_level),
            *([game_objects.BackgroundBrick] * self.x_tiles for _ in range(4)),
            ([game_objects.Brick] * (third_level - 1) + [game_objects.BackgroundBrick] * (third_level + 2) +
             [game_objects.Brick] * (third_level - 1)),
            *([game_objects.BackgroundBrick] * self.x_tiles for _ in range(4)),
            ([game_objects.Brick] * third_level + [game_objects.BackgroundBrick] * third_level +
             [game_objects.Brick] * third_level),
            *([game_objects.BackgroundBrick] * self.x_tiles for _ in range(4)),
            [game_objects.Brick] * self.x_tiles
        ]

        self.star_boss = star = game_objects.StarBoss()
        star_pos = utils.tile_point(self.x_tiles // 2, self.y_tiles // 2)
        star_pos[0] -= star.rect.w // 2
        star_pos[1] -= star.rect.h // 2

        objects = [
            (star, star_pos),
            (game_objects.StarStone(), utils.tile_point(4, self.y_tiles - 7)),
            (game_objects.StarStone(), utils.tile_point(self.x_tiles - 6, self.y_tiles - 7)),
            (game_objects.StarStone(), utils.tile_point(7, self.y_tiles - 2)),
            (game_objects.StarStone(), utils.tile_point(self.x_tiles - 9, self.y_tiles - 2)),
            (game_objects.StarStone(), utils.tile_point(6, self.y_tiles - 12)),
            (game_objects.StarStone(), utils.tile_point(self.x_tiles - 8, self.y_tiles - 12)),
            (game_objects.StarStone(), utils.tile_point(self.x_tiles // 2 - 1, self.y_tiles - 17)),
        ]

        return schema, objects

    def activate_stone(self):
        if not self.star_stones:
            return

        stone = random.choice(self.star_stones)
        stone.toggle_activated()

    def create(self):
        _, objects = super().create()

        for object, _ in filter(lambda o: isinstance(o[0], game_objects.StarStone), objects):
            self.star_stones.append(object)

        self.activate_stone()

    def finish(self):
        for stone in self.star_stones:
            if stone.activated:
                stone.toggle_activated()

        self.finished = True

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)

        if self.finished:
            text_surface = self.sf_font.render(constants.WIN_TEXT, True, (255, 255, 255))
            text_pos = utils.tile_point(self.x_tiles // 2, self.y_tiles // 2)
            text_pos[0] -= text_surface.get_width() // 2
            args[0].blit(text_surface, text_pos)
