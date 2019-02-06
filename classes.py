import pygame as pg
from settings import *
vec = pg.math.Vector2

class Entity(pg.sprite.Sprite):
    def __init__(self, game, pos, health, damage, speed):
        super().__init__(game.all_sprites)
        self.game = game

        self.direction = 'right'

        self.pos = pos
        self.acc = vec(0, 0)
        self.vel = vec(0, 0)

        self.health = health
        self.damage = damage

        self.speed = speed

        self.animations = {}
        self.accumulator = 0
        self.frame = 0
        self.prev_anim = None

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
        if self.rect is None:
            return False
        self.rect.y += 1
        answer = not pg.sprite.spritecollideany(self, self.game.platforms, False)
        self.rect.y -= 1
        return answer

    def jump(self):
        if not self.is_midair():
            self.vel.y = -PLAYER_JUMP_STR

    def animate(self, name):
        if self.prev_anim != name:
            self.prev_anim = name
            self.frame = 0
        self.frame += self.accumulator // FRAME_DUR
        self.accumulator %= FRAME_DUR
        self.frame %= len(self.animations[name])
        self.image = self.animations[name][self.frame].convert_alpha()
        if self.direction == 'left':
            self.image = pg.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()
        self.rect.midbottom = self.pos


class Player(Entity):
    def __init__(self, game, pos):
        super().__init__(game, vec(pos), 100, [10, 15, 30], PLAYER_ACC)
        game.players.add(self)

        self.rect = None

        self.load_animation('run', 40)
        self.load_animation('idle', 60)
        self.load_animation('fall', 1)
        self.load_animation('jump', 1)

    def update(self):
        self.manage_animations()
        self.acc = vec(0, GRAVITY)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            if not self.is_midair():
                self.acc.x = -self.speed
        if keys[pg.K_RIGHT]:
            if not self.is_midair():
                self.acc.x = self.speed
        if keys[pg.K_SPACE]:
            if not self.is_midair():
                self.jump()
        self.move()
        self.manage_collisions()

    def manage_collisions(self):
        super().manage_collisions()
        collision = pg.sprite.spritecollideany(self, self.game.enemies, collided=pg.sprite.collide_mask)
        if collision:
            if self.vel.y > 0 and self.rect.bottom < collision.rect.centery:
                collision.kill()
                self.vel.y = -PLAYER_JUMP_STR
            else:
                self.take_damage(collision)

    def take_damage(self, enemy):
        self.health = max(0, self.health - enemy.damage)
        if self.health == 0:
            self.die()
        else:
            self.vel.x = KNOCKBACK if self.pos.x > enemy.pos.x else -KNOCKBACK

    def load_animation(self, name, length):
        if name in self.animations:
            self.animations[name].clear()
        else:
            self.animations[name] = []
        for i in range(1, length + 1):
            image = pg.image.load('data/animations/player/' + name + '/' + (str(i) + '.png').rjust(8, '0'))
            self.animations[name] += [image]

    def manage_animations(self):
        if self.vel.x > 0:
            self.direction = 'right'
        elif self.vel.x < 0:
            self.direction = 'left'
        self.accumulator += self.game.dt
        if not self.is_midair():
            if abs(self.vel.x) <= IDLE_ACC_MARGIN:
                self.animate('idle')
            elif self.vel.x != 0:
                self.animate('run')
        elif self.vel.y < 0:
            self.animate('jump')
        elif self.vel.y > 0:
            self.animate('fall')

    def die(self):
        self.game.show_go_screen()
        self.kill()


class Enemy(Entity):
    def __init__(self, game, pos, range, atk_range):
        super().__init__(game, pos, 30, 10, BASE_ENEMY_SPEED,)
        game.enemies.add(self)
        self.load_animation('run', 80)
        self.load_animation('idle', 80)
        self.load_animation('jump', 1)
        self.load_animation('fall', 1)

        self.image = self.animations['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.midbottom = self.pos

        self.attack_range = atk_range

        self.range = range

    def update(self):
        self.manage_animations()
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

    def manage_animations(self):
        self.accumulator += self.game.dt
        if not self.is_midair():
            if abs(self.vel.x) <= IDLE_ACC_MARGIN:
                self.animate('idle')
            elif self.vel.x != 0:
                self.animate('run')
        elif self.vel.y < 0:
            self.animate('jump')
        elif self.vel.y > 0:
            self.animate('fall')

    def load_animation(self, name, length):
        if name in self.animations:
            self.animations[name].clear()
        else:
            self.animations[name] = []
        for i in range(1, length + 1):
            file = 'data/animations/cookieneg/{}/{}'.format(name, (str(i) + '.png').rjust(8, '0'))
            image = pg.image.load(file).convert_alpha()
            image = pg.transform.scale(image, (192, 192))
            self.animations[name] += [image]


class Platform(pg.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pg.Surface((w, h))
        self.image.fill(pg.Color('green'))
        self.rect = self.image.get_rect()
        self.rect.topleft = x, y