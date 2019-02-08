import pygame as pg


def load_animation(name, length, scale, animations):
    key = name.split('/')[-1]
    animations[key] = []
    for i in range(1, length + 1):
        file = 'data/animations/' + name + '/' + (str(i) + '.png').rjust(8, '0')
        image = pg.transform.scale(pg.image.load(file), scale)
        image.convert()
        image.set_colorkey((0, 0, 0))
        animations[key] += [(image, pg.mask.from_surface(image))]

pg.display.init()
pg.display.set_mode((0, 0))

tileset = pg.image.load('data/images/static/tiles.png')


PLAYER_ANIMATIONS = {}
load_animation('player/run', 40, (192, 192), PLAYER_ANIMATIONS)
load_animation('player/idle', 60, (192, 192), PLAYER_ANIMATIONS)
load_animation('player/fall', 1, (192, 192), PLAYER_ANIMATIONS)
load_animation('player/jump', 1, (192, 192), PLAYER_ANIMATIONS)
COOKIENEG_ANIMATIONS = {}
load_animation('cookieneg/run', 80, (160, 160), COOKIENEG_ANIMATIONS)
load_animation('cookieneg/idle', 80, (160, 160), COOKIENEG_ANIMATIONS)
load_animation('cookieneg/fall', 1, (160, 160), COOKIENEG_ANIMATIONS)
load_animation('cookieneg/jump', 1, (160, 160), COOKIENEG_ANIMATIONS)
pg.display.quit()

grass = pg.Surface((16, 16))
dirt = pg.Surface((16, 16))
wood = pg.Surface((16, 16))
rock = pg.Surface((16, 16))

grass.blit(tileset, (0, 0))
dirt.blit(tileset, (0, -16))
rock.blit(tileset, (-16, 0))
wood.blit(tileset, (-16, -16))

grass = pg.transform.scale(grass, (64, 64))
dirt = pg.transform.scale(dirt, (64, 64))
rock = pg.transform.scale(rock, (64, 64))
wood = pg.transform.scale(wood, (64, 64))

p_spawn = pg.Surface((64, 64))
p_spawn.fill((255, 0, 0))

e_spawn = pg.Surface((64, 64))
e_spawn.fill((0, 255, 0))

TILES = {'grass': grass,
         'dirt': dirt,
         'rock': rock,
         'wood': wood,
         'pspawn': p_spawn,
         'espawn': e_spawn}

del grass, dirt, rock, wood, p_spawn, e_spawn
