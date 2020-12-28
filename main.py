from collections import deque
from random import randint

import pygame

WIDTH = 800
HEIGHT = 600
TRAIL_LENGTH = 20

clock = pygame.time.Clock()


def randvec2(max_x, max_y=None, min_x=None, min_y=None):
    if max_y is None:
        max_y = max_x
    if max_y is None:
        max_y = max_x
    if min_x is None:
        min_x = max_x
    if min_y is None:
        min_y = max_y
    x = randint(-min_x, max_x)
    y = randint(-min_y, max_y)
    return pygame.math.Vector2(x, y)


class Qix:
    def __init__(self, screen):
        self.screen = screen
        self.a_s = deque([randvec2(min_x=0, max_x=WIDTH, min_y=0, max_y=HEIGHT)],
                         maxlen=TRAIL_LENGTH)
        self.b_s = deque([randvec2(min_x=0, max_x=WIDTH, min_y=0, max_y=HEIGHT)],
                         maxlen=TRAIL_LENGTH)
        self.da = randvec2(10)
        self.db = randvec2(10)

    def move(self, dt):
        abs_dt = dt / 10
        new_a = self.a_s[-1] + abs_dt * self.da
        if new_a.x < 0:
            new_a.x = -new_a.x
            self.da.x = -self.da.x
        if new_a.x > WIDTH:
            new_a.x = 2*WIDTH - new_a.x
            self.da.x = -self.da.x
        if new_a.y < 0:
            new_a.y = -new_a.y
            self.da.y = -self.da.y
        if new_a.y > HEIGHT:
            new_a.y = 2*HEIGHT - new_a.y
            self.da.y = -self.da.y
        new_b = self.b_s[-1] + abs_dt * self.db
        if new_b.x < 0:
            new_b.x = -new_b.x
            self.db.x = -self.db.x
        if new_b.x > WIDTH:
            new_b.x = 2*WIDTH - new_b.x
            self.db.x = -self.db.x
        if new_b.y < 0:
            new_b.y = -new_b.y
            self.db.y = -self.db.y
        if new_b.y > HEIGHT:
            new_b.y = 2*HEIGHT - new_b.y
            self.db.y = -self.db.y
        self.a_s.append(new_a)
        self.b_s.append(new_b)

    def show(self):
        for v1, v2 in zip(self.a_s, self.b_s):
            pygame.draw.line(self.screen, (200, 200, 200), v1, v2)


class QixGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.qix = Qix(self.screen)

    def run(self):
        self.start()
        self.mainloop()
        self.stop()

    def start(self):
        pass

    def stop(self):
        pass

    def mainloop(self):
        done = False
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
            self.draw_screen()
            self.qix.show()
            pygame.display.flip()
            dt = clock.tick(60)
            self.qix.move(dt)

    def draw_screen(self):
        self.screen.fill((0, 0, 0))


def run_game():
    pygame.init()
    pygame.display.set_caption("QiX")
    pygame.key.set_repeat(200, 50)
    game = QixGame()
    game.run()
    pygame.quit()


if __name__ == '__main__':
    run_game()
