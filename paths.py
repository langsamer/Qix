import pygame


EPSILON = 0.00000001
Vector = pygame.Vector2


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
    f0 = Vector(line_from[0])
    f1 = Vector(line_from[1])
    t0 = Vector(line_to[0])
    t1 = Vector(line_to[1])
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


# Python implementation of an algorithm described in:
# http://www.geomalgorithms.com/a05-_intersect-1.html#intersect2D_2Segments()
# I only deal with 2d objects, though


def intersect_2d_segments(seg1, seg2):
    """Determine the intersection of two 2-dimensional line segments.

    Return None if they don't intersect, a Vector if they intersect in a single
    point, or a Line (segment) if they are colinear and overlap.
    """
    u = Vector(Vector(seg1[1]) - Vector(seg1[0]))  # direction of seg1
    v = Vector(Vector(seg2[1]) - Vector(seg2[0]))  # direction of seg2
    w = Vector(Vector(seg1[0]) - Vector(seg2[0]))  # from base of seg2 to base of seg1
    d = u.cross(v)  # proportional to sine of angle between seg1 and seg2

    if abs(d) < EPSILON:
        # seg1 and seg2 are parallel
        # w goes from seg1 to seg2; check if w is parallel to one of them
        if u.cross(w) != 0 or v.cross(w) != 0:
            # seg1 and seg2 are parallel but not colinear
            return None
        # they are colinear or degenerate
        # check if they are degenerate points
        du = u.dot(u)
        dv = v.dot(v)
        if du == 0 and dv == 0:
            # both segments are points
            if seg1[0] != seg2[0]:
                # they are distinct points
                return None
            else:
                # they are the same point
                return seg1[0]
        elif du == 0:
            # seg1 is a single point
            if in_segment(seg1[0], seg2):
                return seg1[0]
            else:
                return None
        elif dv == 0:
            # seg2 is a single point
            if in_segment(seg2[0], seg1):
                return seg2[0]
            else:
                return None
        # they are colinear segments: return overlap (if it exists)
        w2 = Vector(seg1[1] - seg2[0])
        if v.x != 0:
            t0 = w.x / v.x
            t1 = w2.x / v.x
        else:
            t0 = w.y / v.y
            t1 = w2.y / v.y
        if t0 > t1:  # swap
            t0, t1 = t1, t0
        if t0 > 1 or t1 < 0:
            return None  # no overlap
        t0 = max(0, t0)
        t1 = min(1, t1)
        if t0 == t1:  # intersection is a point
            pi = seg2[0] + t0 * v
            return pi
        # they overlap in a proper subsegment
        i0 = seg2[0] + t0 * v
        i1 = seg2[0] + t1 * v
        return i0, i1
    else:  # the segments are skew and may intersect in a point
        si = v.cross(w) / d
        if si < 0 or si > 1:  # no intersection with seg1
            return None
        # get the intersection parameter for seg2
        ti = u.cross(v) / d
        if ti < 0 or ti > 1:  # no intersection with seg2
            return None
        pi = seg1[0] + si * u
        return pi


def in_segment(point, line):
    """Determine if a point is inside a segment, if we already know that
    the point is on the infinite line defined by the segment.
    """
    if line[0].x != line[1].x:  # line is not vertical
        if line[0].x <= point.x <= line[1].x:
            return True
        if line[1].x <= point.x <= line[0].x:
            return True
    else:  # line is vertical, so test the y coordinate
        if line[0].y <= point.y <= line[1].y:
            return True
        if line[1].y <= point.y <= line[0].y:
            return True