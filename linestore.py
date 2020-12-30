import itertools
from collections import defaultdict
from typing import Tuple, Union

import pygame


class LineStore:
    def __init__(self, dim: str):
        if dim not in ['horizontal', 'vertical']:
            raise ValueError("Dimension dim must be either 'horizontal' or 'vertical'")
        self.dim = dim
        self.lines = defaultdict(list)

    def __getitem__(self, item):
        return self.lines[item]

    def get_near(self, key):
        """Proximity search: Find lines that depart at a position +/-2 pixels around `key`.

        Closer matches are returned first in the list.
        """
        return itertools.chain([
            self.lines[k]
            for k in [key, key - 1, key + 1, key - 2, key + 2]
        ])

    def add(self, line: Tuple[Union[Tuple[int], pygame.math.Vector2]]):
        if self.dim == 'horizontal':
            key = line[0][1]  # index by y coordinate
            value = (line[0][0], line[1][0])  # store x_0 and x_1
        else:
            key = line[0][0]  # index by x coordinate
            value = (line[0][1], line[1][1])  # store y_0 and y_1
        self.lines[key].append(value)

    def simplify(self, key=None):
        if key is not None:
            self._simplify(key)
        else:
            for key in self.lines.keys():
                self._simplify(key)

    def _simplify(self, key):
        self.lines[key] = simplify_one_coord(self.lines[key])


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