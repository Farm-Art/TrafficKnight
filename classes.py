import pygame as pg
from settings import *
vec = pg.math.Vector2

class Player(pg.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game

        self.acc = vec(0, 0)
        self.vel = vec(0, 0)
        self.pos = vec(WIDTH / 2, HEIGHT / 2)

        self.image = pg.Surface((64, 128))
        self.image.fill(pg.Color('red'))
        self.rect = self.image.get_rect()
        self.rect.midbottom = vec(WIDTH // 2, HEIGHT // 2)

    def update(self):
        self.acc = vec(0, GRAVITY)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACC
        if keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACC
        self.move()

    def move(self):
        self.acc.x += self.vel.x * -FRICTION
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        self.rect.midbottom = self.pos

    def jump(self):
        self.rect.y += 1
        if pg.sprite.spritecollideany(self, self.game.platforms, False):
            self.vel.y = -PLAYER_JUMP_STR
        self.rect.y -= 1


class Platform(pg.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pg.Surface((w, h))
        self.image.fill(pg.Color('green'))
        self.rect = self.image.get_rect()
        self.rect.topleft = x, y