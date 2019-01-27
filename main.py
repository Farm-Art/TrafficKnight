from classes import *
import os

class Game:
    def __init__(self):
        pg.init()
        pg.mixer.init()

        self.screen = pg.display.set_mode(SIZE)
        pg.display.set_caption(TITLE)

        self.playing = False

        self.clock = pg.time.Clock()
        pass

    def show_title_screen(self):
        pass

    def show_go_screen(self):
        pass

    def new(self):
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.players = pg.sprite.Group()
        self.enemies = pg.sprite.Group()

        self.player = Player(self)
        Enemy(self, vec(WIDTH * 3 / 4, HEIGHT / 2), BASE_ENEMY_DETECT_RANGE, BASE_ENEMY_ATTACK_RANGE)

        platform = Platform(0, HEIGHT - 100, WIDTH, 20)
        self.all_sprites.add(platform)
        self.platforms.add(platform)
        self.run()

    def run(self):
        self.clock.tick(FPS)
        self.playing = True
        while self.playing:
            dt = self.clock.tick(FPS)
            self.update()
            self.events()
        pass

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.terminate()
                return
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                      self.player.jump()
        self.render()
        pass

    def update(self):
        self.all_sprites.update()

    def load_img(self, name):
        pass

    def load_animation(self, name):
        pass

    def render(self):
        self.screen.fill([0] * 3)
        self.all_sprites.draw(self.screen)
        pg.display.flip()

    def terminate(self):
        self.playing = False
        pg.quit()
        pg.mixer.quit()


game = Game()
game.new()
game.terminate()
