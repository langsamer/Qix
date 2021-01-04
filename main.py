from collections import deque
from random import randint, random

import pygame
from acrylic import Color

from common import WIDTH, HEIGHT, LEFTMARGIN, RIGHTMARGIN, TOPMARGIN, BOTTOMMARGIN, TRAIL_LENGTH, \
    PLAYER_SPEED, key_map, directions
from linestore import LineStore, decompose_rects, line_intersect, decompose_polyline

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
        self.color_s = deque([Color(hsv=[random() * 360.0, 100.0, 100.0])],
                             maxlen=TRAIL_LENGTH)
        self.va = randvec2(10)
        self.vb = randvec2(10)
        self.omega = randint(5, 20)  # angular velocity on the colour wheel

    def move(self, dt):
        abs_dt = dt / 30
        c = self.color_s[-1].hsv
        new_hue = (c.h + abs_dt * self.omega) % 360.0
        new_color = Color(hsv=[new_hue, c.s, c.v])
        self.color_s.append(new_color)

        new_a = self.a_s[-1] + abs_dt * self.va
        if new_a.x < 0:
            new_a.x = -new_a.x
            self.va.x = -self.va.x
        if new_a.x > WIDTH:
            new_a.x = 2 * WIDTH - new_a.x
            self.va.x = -self.va.x
        if new_a.y < 0:
            new_a.y = -new_a.y
            self.va.y = -self.va.y
        if new_a.y > HEIGHT:
            new_a.y = 2 * HEIGHT - new_a.y
            self.va.y = -self.va.y
        self.a_s.append(new_a)

        new_b = self.b_s[-1] + abs_dt * self.vb
        if new_b.x < 0:
            new_b.x = -new_b.x
            self.vb.x = -self.vb.x
        if new_b.x > WIDTH:
            new_b.x = 2 * WIDTH - new_b.x
            self.vb.x = -self.vb.x
        if new_b.y < 0:
            new_b.y = -new_b.y
            self.vb.y = -self.vb.y
        if new_b.y > HEIGHT:
            new_b.y = 2 * HEIGHT - new_b.y
            self.vb.y = -self.vb.y
        self.b_s.append(new_b)

    def show(self):
        width = 3
        for v1, v2, c in reversed(list(zip(self.a_s, self.b_s, self.color_s))):
            pygame.draw.line(self.screen, c.hex, v1, v2, width=width)
            if width > 1:
                width = 1


class Player(pygame.sprite.Sprite):
    def __init__(self, border, safe_paths, stix):
        super().__init__()
        self.image = pygame.surface.Surface((10, 10))
        self.rect = self.image.get_rect()
        pygame.draw.rect(self.image, (100, 100, 100), self.rect, width=1)
        self.rect.center = border.midbottom
        # print(type(self.rect.center))
        self.speed = PLAYER_SPEED
        self.direction = 'standstill'
        self.standstill = True
        self.boundary = border
        self.paths = safe_paths
        self.stix = stix
        self.safe = True

    def move(self, dt):
        print(self.rect.center)
        current_direction = directions[self.direction]
        new_rect = self.rect.move(dt * self.speed * current_direction)
        # Keep player inside screen
        center_x, center_y = new_rect.center
        center_x = int(center_x)
        center_y = int(center_y)
        if center_x < self.boundary.left:
            center_x = self.boundary.left
        if center_x > self.boundary.right-1:
            center_x = self.boundary.right-1
        if center_y < self.boundary.top:
            center_y = self.boundary.top
        if center_y > self.boundary.bottom-1:
            center_y = self.boundary.bottom-1
        # TODO: prevent illegal moves (backing up, returning on unfinished 'stix')
        movement = (self.rect.center, (center_x, center_y))
        print(f"Intended movement: {self.direction}: {movement}")
        # Check if movement intersects with any other path
        # check against stix
        if len(self.stix) > 1:
            stix_h, stix_v = decompose_polyline(self.stix)
            intersection = line_intersect(movement, stix_v, ignore=self.rect.center)
            if intersection:
                print(f"Intersection (v) at {intersection}")
                # don't move!
                return False
            intersection = line_intersect(movement, stix_h, ignore=self.rect.center)
            if intersection:
                print(f"Intersection (h) at {intersection}")
                # don't move!
                return False

        self.rect.center = (center_x, center_y)
        return True

    def update(self, dt, direction) -> None:
        # if direction changes:
        # b) check if safe line
        #    - allowed if near branching of safe line
        #    - allowed if turning into free space ==> new stix
        # a) check if allowed
        #    - almost always allowed for stix (not on safe line)
        # c) or if new stix
        #
        # if old direction is 'up' or 'down':
        #     check horizontal safe lines near current position
        # if old direction is 'left' or 'right':
        #     check vertical safe lines near current position
        self.standstill = direction == 'standstill'
        if not self.standstill:
            dir_changed = self.direction != direction
            self.direction = direction
            if not self.stix:
                self.stix.append(self.rect.center)
            if self.move(dt):
                print("Move executed\n")
                if dir_changed:
                    self.stix.append(self.rect.center)
                else:
                    self.stix[-1] = self.rect.center
                print(self.stix)
            else:
                print("Move not allowed\n")
            # TODO: close box when a 'stix' meets a safe line


class QixGame:
    def __init__(self):
        """
        All lines (paths) drawn by the player are stored
        in dictionaries separated into verticals and horizontals:
        + safe: lines around closed areas
        + unsafe: line segments of the shape the player is currently drawing

        """
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.border = self.screen.get_rect()
        self.border.x += LEFTMARGIN
        self.border.y += TOPMARGIN
        self.border.width -= LEFTMARGIN + RIGHTMARGIN + 1
        self.border.height -= TOPMARGIN + BOTTOMMARGIN + 1
        self.safe_horizontals = LineStore('horizontal')
        self.safe_verticals = LineStore('vertical')
        self.unsafe_horizontals = LineStore('horizontal')
        self.unsafe_verticals = LineStore('vertical')
        self.paths = {
            'safe_horizontals': self.safe_horizontals,
            'safe_verticals': self.safe_verticals,
            'unsafe_horizontals': self.unsafe_horizontals,
            'unsafe_verticals': self.unsafe_verticals,
        }
        # stix is a polyline (pygame.draw.lines()) where all segments are
        # either horizontal or vertical.
        # Only one Stix polyline can exist at any one time
        self.stix = []  # keep track of unfinished player track
        self.qix = Qix(self.screen)
        self.player = pygame.sprite.Group(Player(self.border, self.paths, self.stix))

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
        player_dir = 'standstill'
        while not done:
            self.draw_screen()
            self.qix.show()
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                if event.type == pygame.KEYUP and player_dir == key_map.get(event.key, 'standstill'):
                    # If the player is not pressing the key for the current direction, we have to stop
                    player_dir = 'standstill'
                    # TODO: Start timer for fuse
                if event.type == pygame.KEYDOWN:
                    player_dir = key_map.get(event.key, 'standstill')
            # print(player_dir)
            dt = clock.tick(20)
            self.qix.move(dt)
            self.player.update(dt, player_dir)

    def draw_stix(self):
        if len(self.stix) < 2:
            return
        pygame.draw.lines(self.screen, (250, 200, 20), False, self.stix)

    def draw_screen(self):
        self.screen.fill((0, 0, 0))
        pygame.draw.rect(self.screen, (150, 100, 10), self.border, width=1)
        self.draw_stix()
        self.player.draw(self.screen)


def run_game():
    pygame.init()
    pygame.display.set_caption("QiX")
    pygame.key.set_repeat(100, 25)
    game = QixGame()
    game.run()
    pygame.quit()


if __name__ == '__main__':
    run_game()
