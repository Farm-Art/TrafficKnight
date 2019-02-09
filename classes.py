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
        collisions = pg.sprite.spritecollide(self, self.game.platforms, False,
                                             pg.sprite.collide_mask)
        if collisions:
            if any(i.type == 'wood' for i in collisions):
                pass
            if self.vel.y > 0:
                top = max(collisions, key=lambda x: x.rect.top)
                if self.rect.centery <= top.rect.top:
                    self.pos.y = top.rect.top
                    self.rect.midbottom = self.pos
                    self.vel.y = 0
            elif self.vel.y < 0:
                top = min(collisions, key=lambda x: x.rect.top)
                if self.rect.top > top.rect.top:
                    self.rect.top = top.rect.bottom
                    self.pos = vec(self.rect.midbottom)
                    self.vel.y = 0
            collisions = pg.sprite.spritecollide(self, self.game.platforms, False,
                                                 pg.sprite.collide_mask)
            if collisions:
                if self.vel.x > 0:
                    brect = self.image.get_bounding_rect()
                    brect.midbottom = self.rect.midbottom
                    wall = max(collisions, key=lambda x: x.rect.left)
                    if wall.rect.centerx > self.rect.centerx:
                        brect.right = wall.rect.left
                        self.rect.midbottom = brect.midbottom
                        self.pos = vec(self.rect.midbottom)
                        self.vel.x = 0
                elif self.vel.x < 0:
                    brect = self.image.get_bounding_rect()
                    brect.midbottom = self.rect.midbottom
                    wall = min(collisions, key=lambda x: x.rect.right)
                    if wall.rect.centerx < self.rect.centerx:
                        brect.left = wall.rect.right
                        self.rect.midbottom = brect.midbottom
                        self.pos = vec(self.rect.midbottom)
                        self.vel.x = 0


    def is_midair(self):
        if self.rect is None:
            return False
        feet = pg.sprite.Sprite()
        feet.rect = pg.Rect(0, 0, self.rect.w // 1.75, 10)
        feet.rect.midbottom = self.rect.midbottom
        feet.rect.y += 1
        return not pg.sprite.spritecollideany(feet, self.game.platforms, False)


    def jump(self):
        if not self.is_midair():
            JUMP_SND.play()
            self.vel.y = -PLAYER_JUMP_STR

    def animate(self, name):
        if self.prev_anim != name:
            self.prev_anim = name
            self.frame = 0
        self.frame += self.accumulator // FRAME_DUR
        self.accumulator %= FRAME_DUR
        self.frame %= len(self.animations[name])
        if len(self.animations[name][self.frame]) == 1:
            self.animations[name][self.frame][0] = self.animations[name][self.frame][0].convert()
            self.animations[name][self.frame][0].set_colorkey((0, 0, 0))
            self.image = self.animations[name][self.frame][0]
            self.animations[name][self.frame] += [pg.mask.from_surface(self.image)]
            self.mask = self.animations[name][self.frame][1]
        else:
            self.image, self.mask = self.animations[name][self.frame]
        if self.game.ee:
            invert = 'right'
        else:
            invert = 'left'
        if self.direction == invert:
            self.image = pg.transform.flip(self.image, True, False)
            self.mask = pg.mask.from_surface(self.image)
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
                self.vel.y = -PLAYER_JUMP_STR
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
        self.mask = pg.mask.from_surface(self.animations['idle'][0][0])
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
                if not self.is_midair():
                    self.acc.x = -self.speed
            else:
                if not self.is_midair():
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
        self.type = type
        if game is not None:
            if type == 'finish':
                game.finish = self
            else:
                game.platforms.add(self)
            game.all_sprites.add(self)
        self.image = TILES[type].convert_alpha()
        self.mask = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        if game is None and type == 'finish':
            self.rect.midbottom = x + 32, y + 64
        else:
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
