from main import *


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.left = 0
        self.top = 0
        self.cell_size = 64

        self.coll_check = pg.sprite.Sprite()
        self.coll_check.image = pg.Surface((64, 64))
        self.coll_check.rect = self.coll_check.image.get_rect()
        self.coll_check.rect.x, self.coll_check.rect.y = -100, -100

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self):
        for i in range(self.width):
            for j in range(self.height):
                cell = (
                self.left + i * self.cell_size, self.top + j * self.cell_size,
                self.cell_size, self.cell_size)
                pg.draw.rect(screen, (255, 255, 255), cell, 1)

    def get_click(self, pos):
        x, y = pos
        if x in range(self.left, self.cell_size * self.width + self.left):
            if y in range(self.top, self.cell_size * self.height + self.top):
                for i in range(self.height):
                    for j in range(self.width):
                        if x in range(self.left + self.cell_size * j,
                                      self.left + self.cell_size * (j + 1)):
                            cell_x = j
                        if y in range(self.top + self.cell_size * i,
                                      self.top + self.cell_size * (i + 1)):
                            cell_y = i
                return cell_x, cell_y
        return None, None

    def set_tile(self, pos):
        x, y = self.get_click(pos)
        if x is None:
            return
        pl = Platform(None, x * self.cell_size, y * self.cell_size, current_tile)
        if not pg.sprite.spritecollideany(pl, platforms):
            platforms.add(pl)
        else:
            pl.kill()

    def erase_tile(self, pos):
        x, y = self.get_click(pos)
        if x is None:
            return
        self.coll_check.rect.topleft = x * self.cell_size, y * self.cell_size
        collision = pg.sprite.spritecollideany(self.coll_check, platforms)
        if collision:
            collision.kill()

    def save_level(self):
        camera.dx, camera.dy = -camera.x, -camera.y
        for sprite in platforms:
            camera.apply(sprite)
        with open('customlevel.py', mode='w') as file:
            for platform in platforms:
                print(platform.get_init(), file=file)

    def load_level(self):
        try:
            with open('data/levels/customlevel.py') as file:
                for line in file:
                    eval(line.replace('self', 'None'))
        except FileNotFoundError:
            pass


pg.init()
screen = pg.display.set_mode(SIZE)
current_tile = 'grass'
platforms = pg.sprite.Group()
UI = TILES[current_tile]

board = Board(WIDTH // 64, HEIGHT // 64)
camera = Camera()

erasing = False
drawing = False
running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                erasing = False
                drawing = True
                board.set_tile(event.pos)
            elif event.button == 3:
                erasing = True
                drawing = False
                board.erase_tile(event.pos)
        elif event.type == pg.MOUSEMOTION:
            if drawing:
                board.set_tile(event.pos)
            elif erasing:
                board.erase_tile(event.pos)
        elif event.type == pg.MOUSEBUTTONUP:
            drawing, erasing = False, False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_LEFT:
                camera.x -= 64
                camera.dx += 64
            elif event.key == pg.K_RIGHT:
                camera.x += 64
                camera.dx -= 64
            elif event.key == pg.K_UP:
                camera.y -= 64
                camera.dy += 64
            elif event.key == pg.K_DOWN:
                camera.y += 64
                camera.dy -= 64
            elif event.key == pg.K_s:
                board.save_level()
            elif event.key == pg.K_l:
                board.load_level()
    keys = pg.key.get_pressed()
    if keys[pg.K_1]:
        current_tile = 'grass'
    elif keys[pg.K_2]:
        current_tile = 'dirt'
    elif keys[pg.K_3]:
        current_tile = 'rock'
    elif keys[pg.K_4]:
        current_tile = 'wood'
    elif keys[pg.K_5]:
        current_tile = 'pspawn'
    elif keys[pg.K_6]:
        current_tile = 'espawn'
    elif keys[pg.K_7]:
        current_tile = 'finish'
    for sprite in platforms:
        camera.apply(sprite)
    camera.dx, camera.dy = 0, 0
    screen.fill((0, 0, 0))
    board.render()
    platforms.draw(screen)
    pg.display.flip()
pg.quit()