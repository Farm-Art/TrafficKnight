from assets import *
from settings import *
vec = pg.math.Vector2


class Entity(pg.sprite.Sprite):
    def __init__(self, game, x, y, health, damage, speed):
        super().__init__(game.all_sprites)
        self.game = game

        # Direction is used by animations to flip the image if necessary
        self.direction = 'right'

        # Postion, acceleration and velocity vectors
        self.pos = vec(x, y)
        self.acc = vec(0, 0)
        self.vel = vec(0, 0)

        # Health and damage
        self.health = health
        self.damage = damage

        # Speed (acceleration value to use in .update())
        self.speed = speed

        # Variables for animation playback
        # .animations stores animation sequences
        self.animations = {}
        # .accumulator stores difference in ms between animation frame switches
        self.accumulator = 0
        # .frame stores current animation frame
        self.frame = 0
        # .prev_anim stores last played animation to prevent animations from cancelling themselves
        self.prev_anim = None

    def move(self):
        # If not midair, apply friction
        if not self.is_midair():
            self.acc.x += self.vel.x * -FRICTION
        # Apply acceleration and velocity
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        self.rect.midbottom = self.pos

    def manage_collisions(self):
        # Get collisions
        collisions = pg.sprite.spritecollide(self, self.game.platforms, False,
                                             pg.sprite.collide_mask)
        if collisions:
            # If falling
            if self.vel.y > 0:
                # Get top platform
                top = max(collisions, key=lambda x: x.rect.top)

                # Snap to top and reset Y velocity if own center is above platform top
                if self.rect.centery <= top.rect.top:
                    self.pos.y = top.rect.top
                    self.rect.midbottom = self.pos
                    self.vel.y = 0

            # Else if jumping
            elif self.vel.y < 0:
                # Get bottom platform
                bot = min(collisions, key=lambda x: x.rect.top)

                # If own top is below bottom top, snap to bottom and reset Y velocity
                if self.rect.top > bot.rect.top:
                    self.rect.top = bot.rect.bottom
                    self.pos = vec(self.rect.midbottom)
                    self.vel.y = 0

            # Reset collisions to avoid snapping to floor's side
            collisions = pg.sprite.spritecollide(self, self.game.platforms, False,
                                                 pg.sprite.collide_mask)
            if collisions:
                # If moving right, we presume the wall is to the right of us
                if self.vel.x > 0:
                    # Get bounding rect (basically, simplified mask alignment)
                    brect = self.image.get_bounding_rect()
                    brect.midbottom = self.rect.midbottom

                    # Get the farthest left wall
                    wall = max(collisions, key=lambda x: x.rect.left)

                    # Double-checking that it is to the right of us to prevent teleporting outside
                    if wall.rect.centerx > self.rect.centerx:
                        # Snapping bounding rectangle to the left border
                        brect.right = wall.rect.left

                        # Snapping image to bounding rect and resetting X velocity
                        self.rect.midbottom = brect.midbottom
                        self.pos = vec(self.rect.midbottom)
                        self.vel.x = 0

                # If moving left, we presume the wall is to the left of us
                elif self.vel.x < 0:
                    # Get bounding rect (basically, simplified mask alignment)
                    brect = self.image.get_bounding_rect()
                    brect.midbottom = self.rect.midbottom

                    # Get the farthest right wall
                    wall = min(collisions, key=lambda x: x.rect.right)

                    # Double-checking that it is to the left of us to prevent teleporting outside
                    if wall.rect.centerx < self.rect.centerx:
                        # Snapping bounding rectangle to the right border
                        brect.left = wall.rect.right

                        # Snapping image to bounding rect and resetting X velocity
                        self.rect.midbottom = brect.midbottom
                        self.pos = vec(self.rect.midbottom)
                        self.vel.x = 0

    def animate(self, name):
        # Animation self-cancel prevention
        if self.prev_anim != name:
            # If previous animation is not current animation, reset current frame
            # And set current animation as previous
            self.prev_anim = name
            self.frame = 0

        # Increase frame index and reset accumulator using delta time
        self.frame += self.accumulator // FRAME_DUR
        self.accumulator %= FRAME_DUR

        # Set up looping
        self.frame %= len(self.animations[name])

        # If no mask is present, generate mask
        if len(self.animations[name][self.frame]) == 1:
            # Convert image to alpha
            self.animations[name][self.frame][0] = self.animations[name][self.frame][0].convert()

            # Set colorkey (thank you, blender, for not rendering transparency in the run anim)
            self.animations[name][self.frame][0].set_colorkey((0, 0, 0))

            # Set current frame
            self.image = self.animations[name][self.frame][0]

            # Add right mask
            self.animations[name][self.frame] += [pg.mask.from_surface(self.image)]
            self.mask = self.animations[name][self.frame][1]

        # Simply request mask otherwise
        else:
            self.image, self.mask = self.animations[name][self.frame][0:2]

        # If Easter Egg was triggered, flip left and right animations
        if self.game.ee:
            invert = 'right'
        else:
            invert = 'left'
        if self.direction == invert:
            # Flip image
            self.image = pg.transform.flip(self.image, True, False)
            # Add mask to list if not present (because generation is expensive)
            if len(self.animations[name][self.frame]) < 3:
                self.mask = pg.mask.from_surface(self.image)
                self.animations[name][self.frame] += [self.mask]

            # Simply request inverted mask otherwise
            else:
                self.mask = self.animations[name][self.frame][2]

        # Set new rect
        self.rect = self.image.get_rect()
        self.rect.midbottom = self.pos

    def jump(self):
        # Self-explanatory
        if not self.is_midair():
            JUMP_SND.play()
            self.vel.y = -PLAYER_JUMP_STR

    def is_midair(self):
        if self.rect is None:
            return False
        # Set a temporary sprite for feet to prevent unnatural snapping
        feet = pg.sprite.Sprite()
        feet.rect = pg.Rect(0, 0, self.rect.w // 1.75, 10)
        feet.rect.midbottom = self.rect.midbottom
        # Move the sprite down 1 pixel
        feet.rect.y += 1
        # Return True if feet collide with a platform, otherwise False
        return not pg.sprite.spritecollideany(feet, self.game.platforms, False)


class Player(Entity):
    def __init__(self, game, x, y):
        super().__init__(game, x, y, 100, [10, 15, 30], PLAYER_ACC)
        game.players.add(self)

        self.animations = PLAYER_ANIMATIONS

        self.rect = None

    def manage_collisions(self):
        super().manage_collisions()
        # Check for collisions with enemies
        collision = pg.sprite.spritecollideany(self, self.game.enemies, pg.sprite.collide_mask)
        if collision:
            # If falling and own bottom above enemy center, kill enemy
            if self.vel.y > 0 and self.rect.bottom < collision.rect.centery:
                collision.kill()
                self.vel.y = -PLAYER_JUMP_STR
            # Take damage otherwise
            else:
                self.take_damage(collision)

    def manage_animations(self):
        # Set direction for animation, keep intact if not moving
        if self.vel.x > 0:
            self.direction = 'right'
        elif self.vel.x < 0:
            self.direction = 'left'

        # Update accumulator
        self.accumulator += self.game.dt

        # Animate self with animation according to movement
        if not self.is_midair():
            # Idle margin is used because X velocity rarely reaches 0, usually
            # Stays at low values such as 0.001342...
            if abs(self.vel.x) <= IDLE_ACC_MARGIN:
                self.animate('idle')
            else:
                self.animate('run')
        elif self.vel.y < 0:
            self.animate('jump')
        elif self.vel.y > 0:
            self.animate('fall')

    def update(self):
        # Manage animations first to update the image
        self.manage_animations()

        # Introduce gravity
        self.acc = vec(0, GRAVITY)

        # Manage input
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

        # Move self and manage collisions
        self.move()
        self.manage_collisions()

    def take_damage(self, enemy):
        # Self-explanatory
        self.health = max(0, self.health - enemy.damage)
        if self.health == 0:
            self.die()
        else:
            self.vel.x = KNOCKBACK if self.pos.x > enemy.pos.x else -KNOCKBACK

    def die(self):
        # Self-explanatory
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
        self.x -= self.dx
        self.y -= self.dy

    def apply(self, object):
        if isinstance(object, Entity):
            object.pos.x += self.dx
            object.pos.y += self.dy
        object.rect.x += self.dx
        object.rect.y += self.dy
