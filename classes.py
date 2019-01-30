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

    def manage_collisions(self):
        super().manage_collisions()
        collision = pg.sprite.spritecollideany(self, self.game.enemies)
        if collision:
            if self.vel.y > 0 and self.rect.bottom < collision.rect.centery:
                collision.kill()
            else:
                self.take_damage(collision)

    def take_damage(self, enemy):
        self.health = max(0, self.health - enemy.damage)
        if self.health == 0:
            self.die()
        else:
            self.vel = vec(self.rect.centerx - enemy.rect.centerx,
                           enemy.rect.centery - self.rect.centery)

    def die(self):
        self.game.show_go_screen()
        self.kill()


class Enemy(Entity):
    def __init__(self, game, pos, range, atk_range):
        super().__init__(game, pos, 30, 10, BASE_ENEMY_SPEED, pg.Surface((64, 64)))
        game.enemies.add(self)

        self.image.fill(pg.Color('blue'))

        self.attack_range = atk_range

        self.range = range

    def update(self):
        self.acc = vec(0, GRAVITY)
        if self.player_in_range():
            distance = self.game.player.pos.x - self.pos.x
            if distance < 0:
                self.acc.x = -self.speed
            else:
                self.acc.x = self.speed
        self.move()
        self.manage_collisions()

    def player_in_range(self):
        px, py = self.game.player.pos.x, self.game.player.pos.y
        sx, sy = self.pos.x, self.pos.y
        return (px - sx) ** 2 + (py - sy) ** 2 <= self.range ** 2

    def player_in_attack_range(self):
        px, py = self.game.player.pos.x, self.game.player.pos.y
        sx, sy = self.pos.x, self.pos.y
        distance = ((px - sx) ** 2 + (py - sy) ** 2) ** 0.5
        if self.attack_range - ATTACK_MARGIN <= distance <= self.attack_range + ATTACK_MARGIN:
            return True
        return False

class Platform(pg.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pg.Surface((w, h))
        self.image.fill(pg.Color('green'))
        self.rect = self.image.get_rect()
        self.rect.topleft = x, y