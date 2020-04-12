from random import randint

import pygame

from boilerplate import SceneBase, run_game


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
            "upgrade player pickaxe": 25,
            "increase miner speed": 1000
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

        self.rock_image = pygame.image.load("images/rock.png")
        self.rock_image = pygame.transform.scale(self.rock_image, (50, 50))

        self.gold_image = pygame.image.load("images/gold.png")
        self.gold_showing = False

        self.goblin_image = pygame.image.load("images/goblin.png")

    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    self.is_digging = True
                    self.miner_anim_one_time = 15

                    if found_gold(self.gold_chance, self.player_pickaxe_level):
                        self.gold += 1
                        self.gold_showing = True
                    else:
                        self.gold_showing = False

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

        if goblin_comes(self.gold):
            # Let player choose whether to fight or let the goblin take gold.
            pass

    def Render(self, screen):
        screen.fill((0, 0, 0))

        screen.blit(
            self.rock_image,
            (160, 85)
        )

        screen.blit(
            self.draw_player(),
            (50, -50)
        )

        if self.gold_showing:
            screen.blit(
                self.gold_image,
                (160, 100)
            )

        if self.miners > 0:
            screen.blit(
                self.draw_miner(),
                (150, -25)
            )

        screen.blit(
            self.goblin_image,
            (150, 50)
        )

        write(
            screen,
            f"Gold: {self.gold}, Miners: {self.miners}",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
            24
        )

        counter = 1
        for item, price in self.prices.items():
            text = f"{counter}. {item}: {price} gold"
            place = (SCREEN_WIDTH // 2, (SCREEN_HEIGHT // 2) + counter * 25)
            write(screen, text, place, 24)
            counter += 1

    def buy(self, event, key, item, effect, price_change):
        if event.key == key and self.gold >= self.prices[item]:
            self.gold = self.gold - self.prices[item]
            self.prices[item] += price_change
            effect()

    def draw_miner(self):
        m = pygame.transform.scale(
            self.miner_images[self.miner_anim],
            (175, 175)
        )
        m = pygame.transform.flip(m, True, False)
        return m

    def draw_player(self):
        if self.is_digging:
            miner_image = self.miner_images[self.miner_anim]
            self.miner_anim_one_time -= 1
        else:
            miner_image = self.miner_images[0]

        if self.miner_anim_one_time == 0:
            self.is_digging = False
            self.miner_anim = 0

        return miner_image


def found_gold(chance, pickaxe_level):
    return randint(1, 10) > chance - pickaxe_level


def goblin_comes(player_gold):
    return randint(1, 10) == 10


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
