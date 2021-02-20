import pygame
import itertools
import abc

from enum import Enum
from cached_property import cached_property

from . import sprite_groups, constants, utils, levels


class WalkState(Enum):

    idle = 0
    walk_right = 1
    walk_left = 2


class Collidable(abc.ABC):

    def collide_left(self, sprites):
        pass

    def collide_right(self, sprites):
        pass

    def collide_up(self, sprites):
        pass

    def collide_down(self, sprites):
        pass


class Border(pygame.sprite.Sprite, Collidable):

    def __init__(self, x1, y1, x2, y2):
        super().__init__(sprite_groups.SOLID)

        if x1 == x2:
            self.add(sprite_groups.X_BORDERS)
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:
            self.add(sprite_groups.Y_BORDERS)
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


class Animation:

    def __init__(self, images, frame_delay, cycled=True):
        self.images = images
        self.frame_delay = frame_delay
        self.cycled = cycled
        self.frames = None
        self._frame = None
        self.current_delay = 0
        self.reset()

    @classmethod
    def from_dir(cls, path, *args):
        images = [
            utils.load_image_from_path(filepath)
            for filepath in path.glob("*.png")
            if filepath.is_file()
        ]
        return cls(images, *args)

    def reset(self):
        if self.cycled:
            self.frames = itertools.cycle(self.images)
        else:
            self.frames = itertools.chain(self.images, itertools.cycle((None, )))

        self._frame = next(self.frames)
        self.current_delay = 0

    @property
    def frame(self):
        if self.current_delay >= self.frame_delay:
            self.current_delay = 0
            self._frame = next(self.frames)
        else:
            self.current_delay += 1

        return self._frame


class GameObject(pygame.sprite.Sprite, Collidable):

    ADDITIONAL_GROUPS = []
    MASS = 0

    __object_id = 0

    def __init__(self, *groups, **kwargs):
        super().__init__(*groups, *self.ADDITIONAL_GROUPS)
        self.object_id = self.__object_id
        self.__object_id += 1
        self.speed = kwargs.get("speed", pygame.Vector2(0, 0))
        self.base_image = utils.load_image(kwargs.get("image", f"{self.__class__.__name__.lower()}.png"))
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect()
        self.mass = self.MASS

    @cached_property
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
    pass


class BackgroundBrick(GameObject):
    pass


class GroundTile(GameObject):

    ADDITIONAL_GROUPS = [sprite_groups.SOLID]


class Brick(GameObject):

    ADDITIONAL_GROUPS = [sprite_groups.SOLID]


class LevelPointer(GameObject):

    ADDITIONAL_GROUPS = [sprite_groups.SOLID]
    MASS = 5

    def collide_right(self, sprites):
        super().collide_right(sprites)

        if self.level.player in sprites:
            self.level.game.next_level()


class Box(GameObject):

    MASS = 5
    ADDITIONAL_GROUPS = [sprite_groups.SOLID]

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

    ADDITIONAL_GROUPS = [sprite_groups.SOLID, sprite_groups.CHARACTERS]

    JUMP_SPEED = 0
    JUMP_TILES = 0
    WALK_SPEED = 0

    def __init__(self, *args, **kwargs):
        kwargs["image"] = f"{self.__class__.__name__.lower()}/{self.__class__.__name__.lower()}.png"
        super().__init__(*args, **kwargs)
        self.is_jumping = False
        self.x_direction = True
        self.is_damaged = False
        self.jump_pos = None
        self.jump_speed = self.JUMP_SPEED
        self.jump_tiles = self.JUMP_TILES
        self.walk_speed = self.WALK_SPEED
        self.health = 100
        self.walk_animat = Animation.from_dir(
            utils.ASSETS_PATH / f"sprites/{self.__class__.__name__.lower()}/walk", 2)
        self.idle_animat = Animation.from_dir(
            utils.ASSETS_PATH / f"sprites/{self.__class__.__name__.lower()}/idle", 2)
        self.hit_animat = Animation.from_dir(
            utils.ASSETS_PATH / f"sprites/{self.__class__.__name__.lower()}/hit", 5, False)

    def draw_health_bar(self, screen):
        pass

    @property
    def alive(self):
        return self.health > 0

    def kill(self):
        self.health = 0
        self.remove(sprite_groups.SOLID)
        super().kill()

    def jump(self, tiles=None):
        self.is_jumping = True
        self.speed.y = self._gravity(self.jump_speed) * -1
        self.jump_pos = self.rect.copy()
        self.jump_tiles = tiles if tiles is not None else self.JUMP_TILES

    def damage(self, damage):
        self.health = max(0, self.health - damage)
        self.is_damaged = True

    def push(self, x, tiles=None, *, side=None):
        if side is None:
            side = not self.x_direction

        self.jump(tiles)
        speed = max(abs(self.speed.x) * 2, 1)

        if side:
            self.speed.x = speed + x
        else:
            self.speed.x = -(speed + x)

    def collide_down(self, sprites, auto=False):
        if not self.is_jumping:
            super().collide_down(sprites)

        if not auto:

            for sprite in sprites:
                if isinstance(sprite, Character):
                    sprite.collide_up([self], True)
                else:
                    sprite.collide_up([self])

        if sprites:
            if not any(isinstance(s, Character) for s in sprites):
                self.is_jumping = False

    def collide_up(self, sprites, auto=False):
        super().collide_up(sprites)

        if not auto:
            for sprite in sprites:
                if isinstance(sprite, Character):
                    sprite.collide_down([self], True)
                else:
                    sprite.collide_down([self])

    def collide_right(self, sprites, auto=False):
        super().collide_right(sprites)

        if not auto:
            for sprite in sprites:
                if isinstance(sprite, Character):
                    sprite.collide_left([self], True)
                else:
                    sprite.collide_left([self])

    def collide_left(self, sprites, auto=False):
        super().collide_left(sprites)

        if not auto:
            for sprite in sprites:
                if isinstance(sprite, Character):
                    sprite.collide_right([self], True)
                else:
                    sprite.collide_right([self])

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)

        if self.health <= 0:
            self.kill()

        if (self.is_jumping and
                self.jump_pos.y - self.rect.y >= self.jump_tiles * constants.TILE_SIZE):
            self.speed.y = self._gravity(self.jump_speed)
            self.jump_tiles = self.JUMP_TILES

        if self.is_damaged:
            frame = self.hit_animat.frame

            if frame is None:
                self.is_damaged = False
                self.hit_animat.reset()
            else:
                self.image = pygame.transform.flip(frame, not self.x_direction, False)

        if self.speed.x > 0:
            if not self.is_damaged:
                self.image = self.walk_animat.frame

            self.x_direction = True
        elif self.speed.x < 0:
            if not self.is_damaged:
                self.image = pygame.transform.flip(self.walk_animat.frame, True, False)

            self.x_direction = False

        if self.speed.x == 0 and self.speed.y == 0 and not self.is_damaged:
            self.image = pygame.transform.flip(self.idle_animat.frame, not self.x_direction, False)

        self.draw_health_bar(args[0])


class Player(Character):

    MASS = 5
    JUMP_SPEED = 5
    JUMP_TILES = 5
    WALK_SPEED = 5

    def __init__(self, *args,  **kwargs):
        super().__init__(*args, sprite_groups.PLAYERS, **kwargs)
        self.idle_animat.frame_delay = 5
        self.walk_animat.frame_delay = 3
        self.walk_state = WalkState.idle

    def draw_health_bar(self, screen):
        if self.health >= 70:
            bar_color = constants.GREEN_COLOR
        elif self.health >= 40:
            bar_color = constants.ORANGE_COLOR
        else:
            bar_color = constants.RED_COLOR

        pygame.draw.rect(
            screen, bar_color,
            (self.rect.x, self.rect.y - 12, self.rect.width / 100 * self.health, 4)
        )

    def push(self, *args, **kwargs):
        super().push(*args, **kwargs)

        if self.walk_state == WalkState.walk_right:
            self.walk_state = WalkState.walk_left
        elif self.walk_state == WalkState.walk_left:
            self.walk_state = WalkState.walk_right

    def collide_down(self, sprites, auto=False):
        if self.is_jumping and sprites:
            self.speed.x = 0
            self.walk_state = WalkState.idle

        super().collide_down(sprites, auto=auto)

    def on_keyboard(self, *, event=None, keys=None):
        if event is not None:
            if (event.key == pygame.K_SPACE and
                event.type == pygame.KEYUP and
                not self.is_jumping and
                    self.speed.y == 0):
                self.jump()

        if keys is not None:
            if keys[pygame.K_d] and self.walk_state != WalkState.walk_right:
                if self.walk_state == WalkState.walk_left:
                    self.speed.x = min(0, self.speed.x + self.walk_speed)

                self.speed.x += self.walk_speed
                self.walk_state = WalkState.walk_right
            elif not keys[pygame.K_d] and self.walk_state == WalkState.walk_right:
                self.speed.x = max(0, self.speed.x - self.walk_speed)
                self.walk_state = WalkState.idle

            if keys[pygame.K_a] and self.walk_state != WalkState.walk_left:
                if self.walk_state == WalkState.walk_right:
                    self.speed.x = max(0, self.speed.x - self.walk_speed)

                self.speed.x -= self.walk_speed
                self.walk_state = WalkState.walk_left
            elif not keys[pygame.K_a] and self.walk_state == WalkState.walk_left:
                self.speed.x = min(self.walk_speed, self.speed.x + self.walk_speed)
                self.walk_state = WalkState.idle


class EnemyFrog(Character):

    ADDITIONAL_GROUPS = [sprite_groups.CHARACTERS, sprite_groups.SOLID]

    MASS = 5
    JUMP_SPEED = 5
    JUMP_TILES = 5
    WALK_SPEED = 5

    def __init__(self, *args,  **kwargs):
        super().__init__(*args, **kwargs)
        self.idle_animat.frame_delay = 5
        self.walk_animat.frame_delay = 3
        self.aggroed = False

    @property
    def aggro_rect(self):
        rect = self.rect.copy()
        rect.x -= constants.TILE_SIZE * 5
        rect.width += constants.TILE_SIZE * 10
        rect.y -= constants.TILE_SIZE * 5
        rect.height += constants.TILE_SIZE * 8
        return rect

    def collide_up(self, sprites, *args):
        super().collide_up(sprites, *args)

        if self.level is None:
            return

        player = self.level.player

        if player is not None and player in sprites:
            player.push(5, 3)
            self.kill()

    def collide_left(self, sprites, auto=False):
        super().collide_left(sprites, auto=auto)

        if self.level is None:
            return

        player = self.level.player

        if player is not None and player in sprites:
            player.push(10, 2, side=False)
            player.damage(constants.ENEMY_DAMAGE)

        if self.aggroed and not self.is_jumping and player not in sprites:
            self.push(5, 5, side=self.x_direction)

    def collide_right(self, sprites, auto=False):
        super().collide_right(sprites, auto=auto)

        if self.level is None:
            return

        player = self.level.player

        if player is not None and player in sprites:
            player.push(10, 2, side=True)
            player.damage(constants.ENEMY_DAMAGE)

        if self.aggroed and not self.is_jumping and player not in sprites:
            self.push(5, 5, side=self.x_direction)

    def collide_down(self, sprites, auto=False):
        super().collide_down(sprites, auto=auto)

        if self.level is None:
            return

        player = self.level.player

        if player is not None and player in sprites:
            player.kill()

    def go_to(self, x, y):
        if self.rect.x < x:
            self.speed.x = max(self.speed.x, 1)
        elif self.rect.x > x:
            self.speed.x = min(self.speed.x, -1)
        elif not self.is_jumping:
            self.speed.x = 0

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)

        if self.level is None:
            return

        if self.level.player.alive and self.aggro_rect.colliderect(self.level.player.rect):
            self.go_to(self.level.player.rect.x, self.level.player.rect.y)
            self.aggroed = True
        else:
            self.speed.x = 0
            self.aggroed = False


class StarBoss(Character):

    ADDITIONAL_GROUPS = [sprite_groups.CHARACTERS]

    def kill(self):
        self.level.finish()
        super().kill()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)

        if self.health == 100:
            self.idle_animat.frame_delay = 4
        elif self.health >= 50:
            self.idle_animat.frame_delay = 3
        else:
            self.idle_animat.frame_delay = 2


class StarStone(GameObject):

    MASS = 10

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.activated = False
        self.regular_image = self.image.copy()
        self.activated_image = utils.load_image(f"{self.__class__.__name__.lower()}_activated.png")

    def toggle_activated(self):
        if self.activated:
            self.image = self.regular_image
            self.activated = False
        else:
            self.image = self.activated_image
            self.activated = True

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)

        if self.level is None or not self.level.star_boss.alive:
            return

        if pygame.sprite.collide_rect(self, self.level.player):
            if self.activated:
                self.level.star_boss.damage(14.5)
                self.toggle_activated()
                self.level.activate_stone()
            else:
                self.level.player.damage(1)
