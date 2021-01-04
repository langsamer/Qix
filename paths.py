import pygame


def point_is_on_line(point, line):
    """Determine if given point lies on the given line

    This function works for horizontal and vertical lines only!"""
    x0, y0 = line[0]
    x1, y1 = line[1]
    if y0 == y1:  # horizontal
        return point[1] == y0 and min(x0, x1) <= point[0] <= max(x0, x1)
    elif x0 == x1:  # vertical
        return point[0] == x0 and min(y0, y1) <= point[1] <= max(y0, y1)
    else:
        raise ValueError("point_is_on_line can only check horizontal and vertical lines")


def lines_with_point(lines, point):
    result = [
        line for line in lines
        if point_is_on_line(point, line)
    ]
    return result


def split_line_at_point(line, point):
    if not point_is_on_line(point, line):
        raise ValueError(f"Point {point} is not on line {line}")
    # Make sure we get the directions of the resulting line(s) correct
    if point == line[0]:
        return [line]
    elif point == line[1]:
        return [(line[1], line[0])]
    else:
        return [(point, line[0]), (point, line[1])]


def orientation(line_from, line_to):
    """Coming along `line_from`, which way do we have to turn?

    Left turn:

             ^
             |  line_from
             |
      +----->+
      line_to

    -1: turn right
     0: straight on
    +1: turn left
    """
    if line_from[1] not in line_to:
        raise ValueError(f"Lines {line_from} and {line_to} do not connect")
    f0 = pygame.Vector2(line_from[0])
    f1 = pygame.Vector2(line_from[1])
    t0 = pygame.Vector2(line_to[0])
    t1 = pygame.Vector2(line_to[1])
    turn = (f1 - f0).cross(t1 - t0)
    # The sign is inverted because screen coordinates are upside down
    # (Y axis increases downwards, ie. we are calculating with the mirror image)
    if turn < 0:
        return 1
    elif turn > 0:
        return -1
    else:
        return 0


def find_path(all_paths, open_loop):
    # start with final line segment in open loop
    finish_point = open_loop[0][0]
    finish_line = (open_loop[0][1], open_loop[0][0])
    starting_line = open_loop[-1]
    starting_point = starting_line[1]
    lines_at_start = []
    lwps = lines_with_point(all_paths, starting_point)
    for full_line in lwps:
        splits = split_line_at_point(full_line, starting_point)
        for line in splits:
            # walk in counter-clockwise direction
            if orientation(starting_line, line) < 0:
                lines_at_start.append(line)
    lwps = lines_with_point(lines_at_start, finish_point)
    for full_line in lwps:
        splits = split_line_at_point(full_line, finish_point)
        for line in splits:
            if orientation(finish_line, line) > 0:
                lines_at_start.append(line)
    return lines_at_start, finish_line
