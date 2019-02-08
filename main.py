from classes import *

class Game:
    def __init__(self):
        pg.init()
        pg.mixer.init()

        self.screen = pg.display.set_mode(SIZE)
        pg.display.set_caption(TITLE)

        self.playing = False

        self.clock = pg.time.Clock()
        pass

    def load_level(self):
        for line in open('customlevel.py').readlines():
            eval(line)

    def show_title_screen(self):
        pass

    def show_go_screen(self):
        del self.camera


    def new(self):
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.players = pg.sprite.Group()
        self.enemies = pg.sprite.Group()

        self.load_level()
        self.player = self.players.sprites()[0]
        self.camera = Camera()
        self.run()

    def run(self):
        self.clock.tick(FPS)
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS)
            self.update()
            self.events()
        pass

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.terminate()
                return
        self.render()
        pass

    def update(self):
        self.all_sprites.update()

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
    game.new()
    game.terminate()
