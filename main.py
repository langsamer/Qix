from collections import deque, defaultdict
from random import randint, random

import pygame
from acrylic import Color

WIDTH = 800
HEIGHT = 600
LEFTMARGIN = 5
RIGHTMARGIN = 5
TOPMARGIN = 5
BOTTOMMARGIN = 5
TRAIL_LENGTH = 40
PLAYER_SPEED = 0.08

key_map = {
    pygame.K_RIGHT: 'right',
    pygame.K_LEFT: 'left',
    pygame.K_DOWN: 'down',
    pygame.K_UP: 'up',
}
directions = {
    'standstill': pygame.math.Vector2(0, 0),
    'right': pygame.math.Vector2(1, 0),
    'left': pygame.math.Vector2(-1, 0),
    'down': pygame.math.Vector2(0, 1),
    'up': pygame.math.Vector2(0, -1),
}

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


def simplify_one_coord(coords):
    """
    Merge all overlapping line segments in a list of line segments on the same horizontal or vertical line.

    The line segments are given only by their start and end coordinates in one coordinate direction because
    they are assumed to share the other cooordinate. (Otherwise they could not overlap, since we are only
    considering horizontal and vertical lines.)

    :param coords: list of pairs (start, end) in one coordinate direction
    :return: list of (start, end) of maximal contiguous line segments
    """
    result = []
    lines = sorted(coords)
    # Lexicographic ordering implies that the lines are sorted by their starting points,
    # so at a given y coordinate, we get the line segments from left to right. (Top to bottom for verticals)
    # We merge overlapping line segments, so that we create (left to right) one maximal contiguous segment.
    # If - after this operation - two consecutive line segments do not overlap, there is a true gap.
    line_old = lines[0]  # get first element
    for line in lines:
        if line_old[1] < line[0]:  # disjoint ==> save line_old and continue with current line segment
            result.append(line_old)
            line_old = line
        else:  # overlapping ==> join lines and continue with merged line segment
            line_old = (line_old[0], line[1])
    else:
        result.append(line_old)  # save the last segment
    return result


def decompose_rects(*rects: pygame.Rect):
    # We collect horizontals and verticals separately,
    # and we collect them in dictionaries indexed by their position:
    # horizontals by y coordinate (because horizontals at different y coordinates can never intersect or overlap),
    # and verticals by x coordinate
    # We store only the 'other' coordinate, so for horizontals we have a map  y -> (x0,x1)
    # Finally, we only have to check each dictionary entry for overlaps.
    horizontals = defaultdict(list)
    verticals = defaultdict(list)
    for r in rects:
        # We insert each side so that it runs from left to right or top to bottom
        # (x_start <= x_end && y_start <= y_end)
        horizontals[r.y].append((r.left, r.right))
        horizontals[r.y].append((r.left, r.right))
        verticals[r.x].append((r.top, r.bottom))
        verticals[r.x].append((r.top, r.bottom))

    # Clean up lines so that we keep only the union of overlapping lines
    result_h = {}
    for y, hori in horizontals.items():
        result_h[y] = [((line[0], y), (line[1], y))
                       for line in simplify_one_coord(hori)]
    result_v = {}
    for x, verti in verticals.items():
        result_v[x] = [((x, line[0]), (x, line[1]))
                       for line in simplify_one_coord(verti)]

    return result_h, result_v


class Player(pygame.sprite.Sprite):
    def __init__(self, border, boxes, stix):
        super().__init__()
        self.image = pygame.surface.Surface((10, 10))
        self.rect = self.image.get_rect()
        pygame.draw.rect(self.image, (100, 100, 100), self.rect, width=1)
        self.rect.center = border.midbottom
        print(type(self.rect.center))
        self.speed = PLAYER_SPEED
        self.direction = directions['standstill']
        self.boundary = border
        self.paths = boxes
        self.stix = stix
        self._safe_lines_h, self._safe_lines_v = decompose_rects(border, *boxes)
        print(f"Safe Horizontals: {self._safe_lines_h}")
        print(f"Safe Verticals: {self._safe_lines_v}")

    def move(self, dt):
        new_rect = self.rect.move(dt * self.speed * self.direction)
        # Keep player inside screen
        center = pygame.math.Vector2(new_rect.center)
        if center.x < self.boundary.left:
            center.x = self.boundary.left
        if center.x > self.boundary.right:
            center.x = self.boundary.right
        if center.y < self.boundary.top:
            center.y = self.boundary.top
        if center.y > self.boundary.bottom:
            center.y = self.boundary.bottom
        self.rect.center = center
        print(self.rect.center)
        # TODO: prevent illegal moves (backing up, returning on unfinished 'stix')

    def update(self, dt, direction) -> None:
        self.move(dt)
        self.direction = direction
        # TODO: draw 'stix'
        # TODO: close box when a 'stix' meets a safe line


class QixGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.border = self.screen.get_rect()
        self.border.x += LEFTMARGIN
        self.border.y += TOPMARGIN
        self.border.width -= LEFTMARGIN + RIGHTMARGIN
        self.border.height -= TOPMARGIN + BOTTOMMARGIN
        self.boxes = []  # keep track of surrounded areas
        self.stix = []  # keep track of unfinished player track
        self.qix = Qix(self.screen)
        self.player = pygame.sprite.Group(Player(self.border, self.boxes, self.stix))

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
            print(player_dir)
            dt = clock.tick(20)
            self.qix.move(dt)
            self.player.update(dt, directions[player_dir])

    def draw_screen(self):
        self.screen.fill((0, 0, 0))
        pygame.draw.rect(self.screen, (150, 100, 10), self.border, width=1)
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
