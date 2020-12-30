import itertools
from collections import defaultdict
from typing import Tuple, Union, Optional

import pygame


class LineStore:
    def __init__(self, dim: str):
        if dim not in ['horizontal', 'vertical']:
            raise ValueError("Dimension dim must be either 'horizontal' or 'vertical'")
        self.dim = dim
        self.lines = defaultdict(list)

    def _make_lines(self, other_coord, line_endpoints):
        """Turn the internal representation by only one coordinate of the endpoints
        and an index for the other dimension into the standard representation of
        a tuple of startpoint and endpoint: ((x0,y0), (x1,y1))"""
        if self.dim == 'horizontal':
            return [
                ((x0, other_coord), (x1, other_coord)) for x0, x1 in line_endpoints
            ]
        else:
            return [
                ((other_coord, y0), (other_coord, y1)) for y0, y1 in line_endpoints
            ]

    def get_lines(self, key):
        return self._make_lines(key, self.lines[key])

    def get_near(self, key):
        """Proximity search: Find lines that depart at a position +/-2 pixels around `key`.

        Closer matches are returned first in the list.
        """
        return [
                line
                for k in [key, key - 1, key + 1, key - 2, key + 2]
                for line in self.get_lines(k)
        ]

    def add(self, line: Tuple[Union[Tuple[int, int], pygame.math.Vector2],
                              Union[Tuple[int, int], pygame.math.Vector2]]):
        """Add a line segment to this LineStore.

        The line segment is not checked whether its direction (horizontal or vertical)
        matches the type of the LineStore. Expect weird results when you place a horizontal
        line in a 'vertical' LineStore or vice versa.
        """
        if self.dim == 'horizontal':
            key = line[0][1]  # index by y coordinate
            value = (line[0][0], line[1][0])  # store x_0 and x_1
        else:
            key = line[0][0]  # index by x coordinate
            value = (line[0][1], line[1][1])  # store y_0 and y_1
        self.lines[key].append(value)

    def simplify(self, key: Optional[int] = None) -> None:
        """Merge overlapping line segments

        :param key: (optional) simplify for this index. If not given, simplify for all keys
        """
        if key is not None:
            self._simplify(key)
        else:
            for key in self.lines.keys():
                self._simplify(key)

    def _simplify(self, key: int):
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


def decompose_rects(*rects: pygame.Rect,
                    horizontals: Optional[LineStore] = None,
                    verticals: Optional[LineStore] = None):
    horizontals = horizontals or LineStore(dim='horizontal')
    verticals = verticals or LineStore(dim='vertical')
    for r in rects:
        # We insert each side so that it runs from left to right or top to bottom
        # (x_start <= x_end && y_start <= y_end)
        horizontals.add((r.topleft, r.topright))
        horizontals.add((r.bottomleft, r.bottomright))
        verticals.add((r.topleft, r.bottomleft))
        verticals.add((r.topright, r.bottomright))
    horizontals.simplify()
    verticals.simplify()
    return horizontals, verticals


def decompose_polyline(polyline,
                       horizontals: Optional[LineStore] = None,
                       verticals: Optional[LineStore] = None):
    horizontals = horizontals or LineStore(dim='horizontal')
    verticals = verticals or LineStore(dim='vertical')
    for p0, p1 in polyline2linesegments(polyline):
        if p0[0] == p1[0]:  # same x coordinate: vertical line
            verticals.add((p0, p1))
        elif p0[1] == p1[1]:  # same y coordinate: horizontal line
            horizontals.add((p0, p1))
        else:
            raise ValueError("Polyline contains a diagonal line")
    return horizontals, verticals


def polyline2linesegments(polyline):
    if len(polyline) < 2:
        raise ValueError("A polyline must have at least length 2")
    result = []
    for p0, p1 in zip(polyline, polyline[1:]):
        result.append((p0, p1))
    return result
