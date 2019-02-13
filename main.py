from classes import *


# Main class for game session
class Game:
    def __init__(self):
        # Initializing pygame modules
        pg.init()
        pg.mixer.init()

        # Setting up game window
        self.screen = pg.display.set_mode(SIZE)
        pg.display.set_caption(TITLE)

        # Set flags for main cycle and easter egg activation
        self.playing = False
        self.ee = False

        # Set up clock and current level variable
        self.clock = pg.time.Clock()
        self.level = 1

    def load_level(self):
        # Try to open current level file,
        try:
            with open('data/levels/level{}.py'.format(self.level)) as file:
                # If file loads successfully, evaluate each line
                for line in file.readlines():
                    eval(line)
        except FileNotFoundError:
            # If no such file is found, we assume that was the last level
            # Thus, the game terminates and function returns False
            self.terminate()
            return False
        # Return True otherwise
        return True

    def show_title_screen(self):
        # Set up local bool variables for:

        # Easter egg key activation
        m, j = False, False

        # Main cycle
        running = True

        # Whether or not we should start the level
        start = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    start = False
                elif event.type == pg.KEYDOWN:
                    # Easter egg activation
                    if event.key == pg.K_m and not m:
                        m = True
                    elif event.key == pg.K_j and m and not j:
                        j = True
                    else:
                        # If the button is neither M nor J, quit title screen and
                        # Launch level
                        running = False
            if m and j:
                # Setting the flag for Easter Egg mode
                self.ee = True

            # Draw splash screen and flip frame
            self.screen.fill((0, 0, 0))
            self.screen.blit(SPLASH_SCREEN, (0, 0))
            pg.display.flip()
        # If the game did not terminate, start a new session
        if start:
            self.new()
        # Terminate otherwise
        else:
            self.terminate()

    def show_go_screen(self):
        # Break the main cycle
        self.playing = False

        # Stop the music and play game over sound
        pg.mixer.music.stop()
        GO_SND.play()

        # If Easter Egg was activated, replace default screen with comic sans
        if self.ee:
            image = GAMEOVER_CS
        # Use default otherwise
        else:
            image = GAMEOVER_IMG

        # Set up local flags for run cycle
        running = True
        new = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    new = False
                    break
                elif event.type == pg.KEYDOWN:
                    # Quit screen if a key was pressed
                    running = False
            # Render gameover screen and flip frame
            self.screen.blit(image, (0, 0))
            pg.display.flip()

        # If game was not quit, start new session on the same level
        if new:
            self.new()
        # Terminate otherwise
        else:
            self.terminate()

    def new(self):
        # Set up sprite groups
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.players = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.ui = pg.sprite.Group()

        # Set up finish object
        self.finish = None

        # Try loading current level, if successful - continue initiation
        if self.load_level():
            # Set up player and camera
            self.player = self.players.sprites()[0]
            self.camera = Camera()
            self.ui.add(Healthbar())

            # If Easter Egg was triggered, load Smooth Criminal
            if self.ee:
                pg.mixer.music.load('data/music/ee.ogg')
            # Default soundtrack otherwise
            else:
                pg.mixer.music.load('data/music/music.ogg')
            # Start main cycle
            self.run()

    def run(self):
        # Start music
        pg.mixer.music.play(loops=-1)

        # Reset clock
        self.clock.tick(FPS)

        # Main cycle
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS)
            self.update()
            # Try-except introduced to prevent errors when quitting properly
            try:
                # Manage events (currently only checks for game termination)
                self.events()
                # Render and flip frame
                self.render()
            except Exception:
                pass

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.playing = False
                return

    def update(self):
        # Update all sprites
        self.all_sprites.update()
        self.ui.update(self.player)
        # Check for finish condition (if present)
        if self.finish is not None:
            if pg.sprite.collide_mask(self.player, self.finish):
                # If True, try to advance to next level and set up a new session
                if self.show_win_screen():
                    self.level += 1
                    self.new()
                # Terminate if game was quit
                else:
                    self.terminate()

    def show_win_screen(self):
        # Break main cycle
        self.playing = False

        # Stop music
        pg.mixer.music.stop()

        # Play win sound
        WIN_SND.play()

        # If Easter Egg was triggered, replace screen with comic sans
        if self.ee:
            img = WIN_CS
        # Use default otherwise
        else:
            img = WIN_IMG

        # Run cycle
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    # Quit game
                    return
                elif event.type == pg.KEYDOWN:
                    # Quit screen if key pressed
                    return True
            # Render and flip frame
            self.screen.fill((0, 0, 0))
            self.screen.blit(img, (0, 0))
            pg.display.flip()

    def render(self):
        # Fill screen with black
        self.screen.fill([0] * 3)

        # Center camera on player
        self.camera.adjust(self.player)

        # Apply delta to all sprites
        for sprite in self.all_sprites:
            self.camera.apply(sprite)

        # Draw all sprites and flip frame
        self.all_sprites.draw(self.screen)
        self.ui.draw(self.screen)
        pg.display.flip()

    def terminate(self):
        # Break main cycle, quit pygame modules
        self.playing = False
        pg.quit()
        pg.mixer.quit()


if __name__ == '__main__':
    game = Game()
    game.show_title_screen()
    game.terminate()
