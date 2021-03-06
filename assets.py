import pygame as pg
from settings import *

def load_animation(name, length, scale, animations):
    key = name.split('/')[-1]
    animations[key] = []
    for i in range(1, length + 1):
        file = 'data/animations/' + name + '/' + (str(i) + '.png').rjust(8, '0')
        image = pg.transform.scale(pg.image.load(file), scale)
        animations[key] += [[image]]


healthbar = pg.image.load('data/images/ui/healthbar.png')
HEALTHBAR = {}
for i in range(10):
    img = pg.Surface((72, 72))
    img.blit(healthbar, (-i * 72, 0))
    HEALTHBAR[(i + 1) * 10] = img

tileset = pg.image.load('data/images/static/tiles.png')
SPLASH_SCREEN = pg.image.load('data/images/screens/start.png')
GAMEOVER_IMG = pg.image.load('data/images/screens/go.png')
GAMEOVER_CS = pg.image.load('data/images/screens/gocs.png')
WIN_IMG = pg.image.load('data/images/screens/win.png')
WIN_CS = pg.image.load('data/images/screens/wincs.png')

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

finish_pole = pg.image.load('data/images/static/finish.png')
finish_pole = pg.transform.scale(finish_pole, (64, 164))

TILES = {'grass': grass,
         'dirt': dirt,
         'rock': rock,
         'wood': wood,
         'pspawn': p_spawn,
         'espawn': e_spawn,
         'finish': finish_pole}

pg.mixer.init()
JUMP_SND = pg.mixer.Sound('data/music/jump.ogg')
JUMP_SND.set_volume(0.5)
GO_SND = pg.mixer.Sound('data/music/gameover.ogg')
WIN_SND = pg.mixer.Sound('data/music/win.ogg')
WIN_SND.set_volume(0.5)
pg.mixer.quit()

del grass, dirt, rock, wood, p_spawn, e_spawn, finish_pole
