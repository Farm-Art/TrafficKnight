from assets import *
from settings import *
vec = pg.math.Vector2

class Entity(pg.sprite.Sprite):
    def __init__(self, game, x, y, health, damage, speed):
        super().__init__(game.all_sprites)
        self.game = game

        self.direction = 'right'

        self.pos = vec(x, y)
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
            top = max(collisions, key=lambda x: x.rect.top)
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
        self.image, self.mask = self.animations[name][self.frame]
        if self.direction == 'left':
            self.image = pg.transform.flip(self.image, True, False)
            self.mask = self.mask.scale((-self.image.get_width(), self.image.get_height()))
        self.rect = self.image.get_rect()
        self.rect.midbottom = self.pos


class Player(Entity):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 100, [10, 15, 30], PLAYER_ACC)
        game.players.add(self)

        self.animations = PLAYER_ANIMATIONS

        self.rect = None

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
        collision = pg.sprite.spritecollideany(self, self.game.enemies)
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
        self.kill()
        self.game.show_go_screen()


class Enemy(Entity):
    def __init__(self, game, x, y,
                 range=BASE_ENEMY_DETECT_RANGE,
                 atk_range=BASE_ENEMY_ATTACK_RANGE):
        super().__init__(game, x, y, 30, 10, BASE_ENEMY_SPEED)
        game.enemies.add(self)
        self.animations = COOKIENEG_ANIMATIONS

        self.image = self.animations['idle'][0][0]
        self.mask = self.animations['idle'][0][1]
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


class Platform(pg.sprite.Sprite):
    def __init__(self, game, x, y, type):
        super().__init__()
        if game is not None:
            game.platforms.add(self)
            game.all_sprites.add(self)
        self.type = type
        self.image = TILES[type]
        self.mask = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.topleft = x, y

    def get_init(self):
        if self.type == 'pspawn':
            return 'Player(self, {}, {})'.format(*self.rect.midbottom)
        elif self.type == 'espawn':
            return 'Enemy(self, {}, {})'.format(*self.rect.midbottom)
        return 'Platform(self, {}, {}, \'{}\')'.format(self.rect.x, self.rect.y, self.type)


class Camera:
    def __init__(self):
        self.dx, self.dy, self.x, self.y = 0, 0, 0, 0

    def adjust(self, target):
        self.dx = -(target.rect.centerx - WIDTH // 2)
        self.dy = -(target.rect.centery - HEIGHT // 2)
        self.x += self.dx
        self.y += self.dy

    def apply(self, object):
        if isinstance(object, Entity):
            object.pos.x += self.dx
            object.pos.y += self.dy
        object.rect.x += self.dx
        object.rect.y += self.dy
