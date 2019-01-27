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

        self.player = Player(self)
        self.all_sprites.add(self.player)

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
            # self.render()
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
        self.player.update()
        collisions = pg.sprite.spritecollide(self.player, self.platforms, False)
        if collisions:
            top = min(collisions, key=lambda x: x.rect.top)
            if self.player.vel.y > 0:
                if self.player.rect.centery < top.rect.top:
                    self.player.pos.y = top.rect.top
                    self.player.vel.y = 0

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
