from random import randint
import pygame


class SceneBase:
    def __init__(self):
        self.next = self

    def ProcessInput(self, events, pressed_keys):
        print("uh-oh, you didn't override this in the child class")

    def Update(self):
        print("uh-oh, you didn't override this in the child class")

    def Render(self, screen):
        print("uh-oh, you didn't override this in the child class")

    def SwitchToScene(self, next_scene):
        self.next = next_scene

    def Terminate(self):
        self.SwitchToScene(None)


def run_game(width, height, fps, starting_scene):
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    active_scene = starting_scene

    while active_scene != None:
        pressed_keys = pygame.key.get_pressed()

        # Event filtering
        filtered_events = []
        for event in pygame.event.get():
            quit_attempt = False
            if event.type == pygame.QUIT:
                quit_attempt = True
            elif event.type == pygame.KEYDOWN:
                alt_pressed = pressed_keys[pygame.K_LALT] or \
                    pressed_keys[pygame.K_RALT]
                if event.key == pygame.K_ESCAPE:
                    quit_attempt = True
                elif event.key == pygame.K_F4 and alt_pressed:
                    quit_attempt = True

            if quit_attempt:
                active_scene.Terminate()
            else:
                filtered_events.append(event)

        active_scene.ProcessInput(filtered_events, pressed_keys)
        active_scene.Update()
        active_scene.Render(screen)

        active_scene = active_scene.next

        pygame.display.flip()
        clock.tick(fps)


# The rest is code where you implement your game using the Scenes model
class Timer:
    def __init__(self, starting_time, on_finish, restart=False):
        self.starting_time = starting_time
        self.time_left = starting_time
        self.on_finish = on_finish
        self.restart = restart

    def tick(self):
        self.time_left -= 1
        if self.time_left < 1:
            self.on_finish()
            if self.restart:
                self.time_left = self.starting_time


class Game(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)

        self.depth = 0

        self.prices = {
            "new miner": 50,
            "increase miner speed": 1000,
            "upgrade player pickaxe": 25
        }

        self.gold = 50000

        self.miners = 0
        self.miners_speed = 5 * FRAME_RATE

        def add_gold():
            self.gold += self.miners

        self.miners_timer = Timer(self.miners_speed, add_gold, restart=True)

        self.gold_chance = 9

        self.player_pickaxe_level = 1

        self.miner_images = load_frames()
        self.miner_anim = 0
        self.miner_anim_one_time = 15
        self.is_digging = False

        self.rock_image = pygame.image.load("rock.png")
        self.rock_image = pygame.transform.scale(self.rock_image, (50, 50))

    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    self.is_digging = True
                    self.miner_anim_one_time = 15
                    if randint(1, 10) > self.gold_chance - self.player_pickaxe_level:
                        self.gold += 1

                def add_miner(): self.miners += 1
                self.buy(
                    event,
                    pygame.K_1,
                    "new miner",
                    add_miner,
                    10 * self.miners
                )

                def upgrade_ppa(): self.player_pickaxe_level += 1
                self.buy(
                    event,
                    pygame.K_2,
                    "upgrade player pickaxe",
                    upgrade_ppa,
                    self.player_pickaxe_level ** 2
                )

                def faster_miners(): self.miners_timer.starting_time -= 1 * FRAME_RATE
                self.buy(
                    event,
                    pygame.K_3,
                    "increase miner speed",
                    faster_miners,
                    self.miners_timer.starting_time ** 2
                )

    def Update(self):
        self.miners_timer.tick()

        if self.miner_anim < 14:
            self.miner_anim += 1
        else:
            self.miner_anim = 0

    def Render(self, screen):
        screen.fill((0, 0, 0))

        screen.blit(
            self.rock_image,
            (160, 85)
        )

        if self.is_digging:
            miner_image = self.miner_images[self.miner_anim]
            self.miner_anim_one_time -= 1
        else:
            miner_image = self.miner_images[0]

        if self.miner_anim_one_time == 0:
            self.is_digging = False
            self.miner_anim = 0

        screen.blit(
            miner_image,
            (50, -50)
        )

        write(
            screen,
            f"Gold: {self.gold}, Miners: {self.miners}",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
            24
        )

        counter = 1
        for key, value in self.prices.items():
            text = f"{counter}. {key}: {value} gold"
            place = (SCREEN_WIDTH // 2, (SCREEN_HEIGHT // 2) + counter * 25)
            write(screen, text, place, 24)
            counter += 1

    def buy(self, event, key, item, effect, price_change):
        if event.key == key and self.gold >= self.prices[item]:
            self.gold = self.gold - self.prices[item]
            self.prices[item] += price_change
            effect()


def write(screen, message, place, size):
    font = pygame.font.SysFont(None, size)
    text = font.render(message, False, (255, 255, 255))
    screen.blit(
        text,
        (
            place[0] - (text.get_width() // 2),
            place[1] - (text.get_height() // 2)
        )
    )


def load_frames():
    frames = []

    for x in range(1, 16):
        new_frame = pygame.image.load(f"images/miner/frame ({x}).gif")
        frames.append(new_frame)

    return frames


SCREEN_WIDTH = 300
SCREEN_HEIGHT = 300
FRAME_RATE = 20
run_game(SCREEN_WIDTH, SCREEN_HEIGHT, FRAME_RATE, Game())
