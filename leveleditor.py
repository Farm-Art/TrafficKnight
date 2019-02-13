from main import *


# ----- U S E R   M A N U A L -----
# LMB to draw current tiles
# RMB to erase drawn tiles
# 1-7 to select tiles
# S to save level to data/levels/customlevel.py
# L to load level from data/levels/customlevel.py


# Tile alignment grid class
class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.set_view(0, 0, TILE_SIZE)

        # Collision check sprite to easily check for present tiles
        self.coll_check = pg.sprite.Sprite()
        self.coll_check.image = pg.Surface((TILE_SIZE, TILE_SIZE))
        self.coll_check.rect = self.coll_check.image.get_rect()
        self.coll_check.rect.x, self.coll_check.rect.y = -100, -100

    def set_view(self, left, top, cell_size):
        # Set top left corner and cell size
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self):
        # Draw the grid
        for i in range(self.width):
            for j in range(self.height):
                cell = (
                self.left + i * self.cell_size, self.top + j * self.cell_size,
                self.cell_size, self.cell_size)
                pg.draw.rect(screen, (255, 255, 255), cell, 1)

    def get_click(self, pos):
        x, y = pos
        # If the position is in the grid, return cell position
        if x in range(self.left, self.cell_size * self.width + self.left):
            if y in range(self.top, self.cell_size * self.height + self.top):
                cell_x = (x - self.left) // self.cell_size
                cell_y = (y - self.top) // self.cell_size
                return cell_x, cell_y
        # Return None otherwise
        return None, None

    def set_tile(self, pos):
        x, y = self.get_click(pos)
        # Ignore call if cursor is outside the grid
        if x is None:
            return
        # Spawn a tile aligned to grid
        pl = Platform(None, x * self.cell_size, y * self.cell_size, current_tile)
        # If there's no tile present in said position, add platform to group
        if not pg.sprite.spritecollideany(pl, platforms):
            platforms.add(pl)
        # Kill the sprite otherwise to prevent drawing over existing tiles
        else:
            pl.kill()

    def erase_tile(self, pos):
        x, y = self.get_click(pos)
        # Ignore call if cursor is outside the grid
        if x is None:
            return
        # Move coll_check to position and kill all colliding tiles
        self.coll_check.rect.topleft = x * self.cell_size, y * self.cell_size
        pg.sprite.spritecollide(self.coll_check, platforms, True)

    def save_level(self):
        # Attempt to return camera to original view to preserve coordinates,
        # Apparently doesn't work properly :/
        camera.dx, camera.dy = -camera.x, -camera.y
        for sprite in platforms:
            camera.apply(sprite)
        # Open save file
        with open('data/levels/customlevel.py', mode='w') as file:
            # Save init for every tile in the file
            for platform in platforms:
                print(platform.get_init(), file=file)

    def load_level(self):
        # Evaluate each line in save file (if present)
        try:
            with open('data/levels/customlevel.py') as file:
                for line in file:
                    # Replace self with None because no Game object is present
                    eval(line.replace('self', 'None'))
        except FileNotFoundError:
            pass


# Set up window
pg.init()
screen = pg.display.set_mode(SIZE)
pg.display.set_caption('Level Editor')

# Set up group for tiles and default current tile
current_tile = 'grass'
platforms = pg.sprite.Group()

# Set up grid and camera
board = Board(WIDTH // TILE_SIZE, HEIGHT // TILE_SIZE)
camera = Camera()

# Set up flags for operations and main cycle
erasing = False
drawing = False
running = True
while running:
    for event in pg.event.get():
        # Break cycle if app was closed
        if event.type == pg.QUIT:
            running = False

        # If mouse button was pressed, set flag for according action
        elif event.type == pg.MOUSEBUTTONDOWN:
            # Draw on LMB
            if event.button == 1:
                erasing = False
                drawing = True
                board.set_tile(event.pos)
            # Erase on RMB
            elif event.button == 3:
                erasing = True
                drawing = False
                board.erase_tile(event.pos)

        # Perform active action if mouse is moved
        elif event.type == pg.MOUSEMOTION:
            if drawing:
                board.set_tile(event.pos)
            elif erasing:
                board.erase_tile(event.pos)

        # If mouse button is released, set both action flags to False
        elif event.type == pg.MOUSEBUTTONUP:
            drawing, erasing = False, False

        elif event.type == pg.KEYDOWN:
            # For each arrow on keyboard, move the camera in according direction
            if event.key == pg.K_LEFT:
                camera.x -= TILE_SIZE
                camera.dx += TILE_SIZE

            elif event.key == pg.K_RIGHT:
                camera.x += TILE_SIZE
                camera.dx -= TILE_SIZE

            elif event.key == pg.K_UP:
                camera.y -= TILE_SIZE
                camera.dy += TILE_SIZE

            elif event.key == pg.K_DOWN:
                camera.y += TILE_SIZE
                camera.dy -= TILE_SIZE

            # Saving and loading files
            elif event.key == pg.K_s:
                board.save_level()
            elif event.key == pg.K_l:
                board.load_level()

    # For numbers 1-7, assign according tile
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

    # Render and flip frame
    screen.fill((0, 0, 0))
    board.render()
    platforms.draw(screen)
    pg.display.flip()
pg.quit()