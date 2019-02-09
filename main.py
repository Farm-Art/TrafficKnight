from classes import *

class Game:
    def __init__(self):
        pg.init()
        pg.mixer.init()

        self.screen = pg.display.set_mode(SIZE)
        pg.display.set_caption(TITLE)

        self.playing = False

        self.clock = pg.time.Clock()
        self.level = 1

    def load_level(self):
        try:
            with open('level{}.py'.format(self.level)):
                pass
        except FileNotFoundError:
            self.terminate()
            return False
        for line in open('level{}.py'.format(self.level)).readlines():
            eval(line)
        return True

    def show_title_screen(self):
        m, j = False, False
        running = True
        start = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    start = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_m and not m:
                        m = True
                    elif event.key == pg.K_j and m and not j:
                        j = True
                    else:
                        running = False
            if m and j:
                self.ee = True
            self.screen.fill((0, 0, 0))
            self.screen.blit(pg.image.load('data/images/screens/start.png'), (0, 0))
            pg.display.flip()
        if start:
            self.new()
        else:
            self.terminate()


    def show_go_screen(self):
        self.playing = False
        pg.mixer.music.stop()

    def new(self):
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.players = pg.sprite.Group()
        self.enemies = pg.sprite.Group()

        if self.load_level():
            self.player = self.players.sprites()[0]
            self.camera = Camera()
            if self.ee:
                pg.mixer.music.load('data/music/ee.ogg')
            else:
                pg.mixer.music.load('data/music/music.ogg')
            self.run()

    def run(self):
        pg.mixer.music.play(loops=-1)
        self.clock.tick(FPS)
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS)
            self.update()
            if self.playing:
                self.events()


    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.terminate()
                return
        self.render()

    def update(self):
        self.all_sprites.update()
        if pg.sprite.collide_mask(self.player, self.finish):
            if self.show_win_screen():
                self.level += 1
                self.new()
            else:
                self.terminate()


    def show_win_screen(self):
        self.playing = False
        pg.mixer.music.stop()
        snd = pg.mixer.Sound('data/music/win.ogg')
        snd.set_volume(0.5)
        snd.play()

        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    return
            self.screen.fill((0, 0, 0))
            self.screen.blit(pg.image.load('data/images/screens/win.png'), (0, 0))
            pg.display.flip()

    def render(self):
        self.screen.fill([0] * 3)
        self.camera.adjust(self.player)
        for sprite in self.all_sprites:
            self.camera.apply(sprite)
        self.all_sprites.draw(self.screen)
        pg.display.flip()

    def terminate(self):
        self.playing = False
        pg.quit()
        pg.mixer.quit()


if __name__ == '__main__':
    game = Game()
    game.show_title_screen()
    game.terminate()
