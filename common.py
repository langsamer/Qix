import pygame

WIDTH = 800
HEIGHT = 600
LEFTMARGIN = 5
RIGHTMARGIN = 5
TOPMARGIN = 5
BOTTOMMARGIN = 5
TRAIL_LENGTH = 40
PLAYER_SPEED = 0.08
QIX_SPEED = 1/30
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

CLOSE_AREA = pygame.event.custom_type()


def rect2poly(rect: pygame.Rect):
    return [rect.topleft, rect.topright, rect.bottomright, rect.bottomleft]