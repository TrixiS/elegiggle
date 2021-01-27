import pygame
import itertools

from . import sprite_groups, constants, utils
from . import levels


class Border(pygame.sprite.Sprite):

    def __init__(self, x1, y1, x2, y2):
        super().__init__(sprite_groups.ALL)

        if x1 == x2:
            self.add(sprite_groups.X_BORDERS)
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:
            self.add(sprite_groups.Y_BORDERS)
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


class Animation:

    def __init__(self, images, frame_delay):
        self.images = images
        self.frame_delay = frame_delay
        self.frames = itertools.cycle(images)
        self._frame = next(self.frames)
        self.current_delay = 0

    @classmethod
    def from_dir(cls, path, *args):
        images = [
            utils.load_image_from_path(filepath)
            for filepath in path.glob("*.png")
            if filepath.is_file()
        ]
        return cls(images, *args)

    @property
    def frame(self):
        if self.current_delay >= self.frame_delay:
            self.current_delay = 0
            self._frame = next(self.frames)
        else:
            self.current_delay += 1

        return self._frame


class GameObject(pygame.sprite.Sprite):

    additional_groups = []
    MASS = 0

    __object_id = 0

    def __init__(self, *groups, **kwargs):
        super().__init__(*groups, *self.additional_groups, sprite_groups.ALL)
        self.object_id = self.__object_id
        self.__object_id += 1
        self.speed = kwargs.get("speed", pygame.Vector2(0, 0))
        self.base_image = utils.load_image(kwargs.get("image", f"{self.__class__.__name__.lower()}.png"))
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect()
        self.mass = self.MASS

    @property
    def level(self):
        for group in self.groups():
            if isinstance(group, levels.Level):
                return group

    @property
    def solid(self):
        return self in sprite_groups.SOLID

    def _gravity(self, v):
        return (v ** 2) * 0.5

    def collide_up(self, sprites):
        if sprites:
            self.speed.y = self._gravity(self.mass)
        else:
            self.speed.y = 0

    def collide_down(self, sprites):
        if sprites:
            self.speed.y = 0
        else:
            if self.speed.y == 0:
                self.speed.y = self._gravity(self.mass)

    def collide_left(self, sprites):
        pass

    def collide_right(self, sprites):
        pass

    def update(self, *args, **kwargs):
        if self.speed.y == 0:
            self.speed.y = self._gravity(self.mass)

        collided_left = []
        collided_right = []
        collided_up = []
        collided_down = []

        self.rect = self.rect.move(self.speed.x, 0)
        for sprite in pygame.sprite.spritecollide(self, sprite_groups.SOLID, False):
            if sprite == self:
                continue

            if self.speed.x > 0:
                self.rect.right = sprite.rect.left
                collided_right.append(sprite)
            elif self.speed.x < 0:
                self.rect.left = sprite.rect.right
                collided_left.append(sprite)

        self.rect = self.rect.move(0, self.speed.y)
        for sprite in pygame.sprite.spritecollide(self, sprite_groups.SOLID, False):
            if sprite == self:
                continue

            if self.speed.y > 0:
                self.rect.bottom = sprite.rect.top
                collided_down.append(sprite)
            elif self.speed.y < 0:
                self.rect.top = sprite.rect.bottom
                collided_up.append(sprite)

        if collided_left:
            self.collide_left(collided_left)

        if collided_right:
            self.collide_right(collided_right)

        if collided_down:
            self.collide_down(collided_down)

        if collided_up:
            self.collide_up(collided_up)


class BackgroundTile(GameObject):

    additional_groups = [sprite_groups.TILES]


class GroundTile(GameObject):

    MASS = 5
    additional_groups = [sprite_groups.WALLS, sprite_groups.SOLID]

    def collide_right(self, sprites):
        super().collide_right(sprites)

        if self.level.player in sprites and self.mass:
            self.speed.x = -2

    def collide_left(self, sprites):
        super().collide_left(sprites)

        if self.level.player in sprites and self.mass:
            self.speed.x = 2

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.speed.x = 0


class Character(GameObject):

    additional_groups = [sprite_groups.SOLID, sprite_groups.CHARACTERS]

    JUMP_SPEED = 0
    JUMP_TILES = 0
    WALK_SPEED = 0

    def __init__(self, *args, **kwargs):
        kwargs["image"] = f"{self.__class__.__name__.lower()}/{self.__class__.__name__.lower()}.png"
        super().__init__(*args, **kwargs)
        self.is_jumping = False
        self.x_direction = True
        self.jump_pos = None
        self.jump_speed = self.JUMP_SPEED
        self.jump_tiles = self.JUMP_TILES
        self.walk_speed = self.WALK_SPEED
        self.health = 100
        self.walk_animat = Animation.from_dir(
            utils.ASSETS_PATH / f"sprites/{self.__class__.__name__.lower()}/walk", 2)
        self.idle_animat = Animation.from_dir(
            utils.ASSETS_PATH / f"sprites/{self.__class__.__name__.lower()}/idle", 2)

    def jump(self):
        self.is_jumping = True
        self.speed.y = self._gravity(self.jump_speed) * -1
        self.jump_pos = self.rect.copy()

    def collide_down(self, sprites):
        super().collide_down(sprites)

        for sprite in sprites:
            sprite.collide_up([self])

        if sprites:
            self.is_jumping = False

    def collide_up(self, sprites):
        super().collide_up(sprites)

        for sprite in sprites:
            sprite.collide_down([self])

    def collide_right(self, sprites):
        super().collide_right(sprites)

        for sprite in sprites:
            sprite.collide_left([self])

    def collide_left(self, sprites):
        super().collide_left(sprites)

        for sprite in sprites:
            sprite.collide_right([self])

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)

        if (self.is_jumping and
                self.jump_pos.y - self.rect.y >= self.jump_tiles * constants.TILE_SIZE):
            self.speed.y = self._gravity(self.jump_speed)

        if self.speed.x > 0:
            self.image = self.walk_animat.frame
            self.x_direction = True
        elif self.speed.x < 0:
            self.image = pygame.transform.flip(self.walk_animat.frame, True, False)
            self.x_direction = False

        if self.speed.x == 0 and self.speed.y == 0:
            self.image = pygame.transform.flip(self.idle_animat.frame, not self.x_direction, False)


class Player(Character):

    MASS = 5
    JUMP_SPEED = 5
    JUMP_TILES = 5
    WALK_SPEED = 5

    def on_keyboard(self, event):
        if event.key == pygame.K_SPACE and event.type == pygame.KEYUP and not self.is_jumping and self.speed.y == 0:
            self.jump()

        if event.key == pygame.K_d:
            if event.type == pygame.KEYDOWN:
                self.speed.x = self.walk_speed
            elif event.type == pygame.KEYUP and self.speed.x > 0:
                self.speed.x = 0
        elif event.key == pygame.K_a:
            if event.type == pygame.KEYDOWN:
                self.speed.x = -self.walk_speed
            elif event.type == pygame.KEYUP and self.speed.x < 0:
                self.speed.x = 0

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)

        if pygame.sprite.spritecollideany(self, sprite_groups.X_BORDERS):
            self.speed.x = 0
