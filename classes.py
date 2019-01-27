import pygame as pg
from settings import *
vec = pg.math.Vector2

class Entity(pg.sprite.Sprite):
    def __init__(self, game, pos, health, damage, speed, image):
        super().__init__(game.all_sprites)
        self.game = game

        self.pos = pos
        self.acc = vec(0, 0)
        self.vel = vec(0, 0)

        self.health = health
        self.damage = damage

        self.speed = speed

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.midbottom = self.pos

    def move(self):
        if not self.is_midair():
            self.acc.x += self.vel.x * -FRICTION
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        self.rect.midbottom = self.pos

    def manage_collisions(self):
        collisions = pg.sprite.spritecollide(self, self.game.platforms, False)
        if collisions:
            top = min(collisions, key=lambda x: x.rect.top)
            if self.vel.y > 0:
                if self.rect.centery < top.rect.top:
                    self.pos.y = top.rect.top
                    self.vel.y = 0

    def is_midair(self):
        self.rect.y += 1
        answer = not pg.sprite.spritecollideany(self, self.game.platforms, False)
        self.rect.y -= 1
        return answer

    def jump(self):
        if not self.is_midair():
            self.vel.y = -PLAYER_JUMP_STR


class Player(Entity):
    def __init__(self, game):
        super().__init__(game, vec(0, 0), 100, [10, 15, 30], PLAYER_ACC, pg.Surface((64, 128)))
        game.players.add(self)
        self.image.fill(pg.Color('red'))

    def update(self):
        self.acc = vec(0, GRAVITY)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            if not self.is_midair():
                self.acc.x = -self.speed
        if keys[pg.K_RIGHT]:
            if not self.is_midair():
                self.acc.x = self.speed
        self.move()
        self.manage_collisions()


class Enemy(Entity):
    def __init__(self, game, pos, range, atk_range):
        super().__init__(game, pos, 30, 10, BASE_ENEMY_SPEED, pg.Surface((64, 64)))
        game.enemies.add(self)

        self.attack_range = pg.sprite.Sprite()
        self.attack_range.image = pg.Surface((atk_range * 2, atk_range * 2))
        self.attack_range.rect = self.attack_range.image.get_rect()
        self.attack_range.rect.center = self.rect.center

        self.image.fill(pg.Color('blue'))

        self.range = pg.sprite.Sprite()
        self.range.image = pg.Surface((range * 2, range * 2))
        self.range.rect = self.range.image.get_rect()
        self.range.rect.center = self.rect.center
        self.range.center = self.rect.center

    def update(self):
        self.acc = vec(0, GRAVITY)
        if self.player_in_range():
            if not self.player_in_attack_range():
                distance = self.game.player.pos.x - self.pos.x
                if distance < 0:
                    self.acc.x = -self.speed
                else:
                    self.acc.x = self.speed
        # if self.player_in_range():
        #     if self.game.player
        #     if self.game.player.pos.x < self.pos.x:
        #         self.acc.x = -self.speed
        #     elif self.game.player.pos.x > self.pos.x:
        #         self.acc.x = self.speed
        #     else:
        #         self.acc.x = 0
        self.move()
        self.manage_collisions()
        self.range.rect.center = self.rect.center
        self.attack_range.rect.center = self.rect.center

    def player_in_range(self):
        return pg.sprite.spritecollideany(self.range, self.game.players)

    def player_in_attack_range(self):
        return pg.sprite.spritecollideany(self.attack_range, self.game.players)


class Platform(pg.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pg.Surface((w, h))
        self.image.fill(pg.Color('green'))
        self.rect = self.image.get_rect()
        self.rect.topleft = x, y