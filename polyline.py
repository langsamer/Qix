from typing import List

import pygame

from paths import point_is_on_line, intersect_2d_segments


class Polyline:
    """
    A Polyline stores a sequence of points in order.

    The implementation does not prevent the line from crossing itself,
    but things may go wrong if that happens. (not tested!)
    """

    points: List

    def __init__(self, *args):
        if len(args) == 1:
            self.points = list(*args)
        else:
            self.points = list(args)

    def __len__(self):
        return len(self.points)

    def __getitem__(self, item):
        return self.points[item]

    def __contains__(self, item):
        return item in self.points

    def __iter__(self):
        return iter(self.points)

    def __eq__(self, other):
        return self.points == other.points

    def __repr__(self):
        return f"{self.__class__.__name__}({self.points!r})"

    def append(self, point):
        self.points.append(point)

    def index(self, item):
        return self.points.index(item)

    def line_segments(self):
        return zip(self.points, self.points[1:])

    def insert(self, point, after=None):
        insert_at = 0
        if after:
            insert_at = self.index(after) + 1
        else:
            for insert_at, ls in enumerate(self.line_segments(), 1):
                if point_is_on_line(point, ls):
                    break
            else:  # no suitable line segment found
                raise ValueError(f"Point {point} is not on path")
        self.points[insert_at:insert_at] = [point]

    def _splicepoints(self, sub_path):
        start, end = 0, 0
        for start, point in enumerate(self.points):
            if sub_path[0] == point:
                break
        else:
            raise ValueError("Starting point of replacement path must be on polygon")
        for end, point in enumerate(self.points):
            if sub_path[-1] == point:
                break
        else:
            raise ValueError("End point of replacement path must be on polygon")
        return start, end

    def replace(self, sub_path):
        sub_path = list(sub_path)
        start, end = self._splicepoints(sub_path)
        if start < end:
            points = self.points[:start] + sub_path + self.points[end + 1 :]
        else:
            raise ValueError(
                "Cannot replace a segment of original in reverse direction"
            )
        return self.__class__(*points)

    def intersect(self, line):
        """"""
        point = None
        for segment in self.line_segments():
            if point := intersect_2d_segments(line, segment):
                break
        return point


class ClosedPolyline(Polyline):
    """
    A ClosedPolyline stores a sequence of points in order.
    The polygon is assumed to be closed, the last point is implicitly
    connected to the first point.

    In addition to the methods of `Polyline`, objects of this class
    can calculate their own area and test if a given point lies inside
    the polygon.
    """

    def line_segments(self):
        return zip(self.points, self.points[1:] + [self.points[0]])

    def replace(self, sub_path):
        sub_path = list(sub_path)
        start, end = self._splicepoints(sub_path)
        if start < end:
            points = self.points[:start] + sub_path + self.points[end + 1 :]
        else:
            points = sub_path + self.points[end + 1 : start]
        return self.__class__(*points)

    def split(self, sub_path):
        forward = self.replace(sub_path)
        backward = self.replace(reversed(sub_path))
        return forward, backward

    def area(self):
        """Calculate the area surrounded by the polygon.

        There is an assumption that the x coordinates will always be non-negative,
        but the calculation may work für negative x's, too. I just have not checked.
        """
        # add up rectangles left and right of vertical edges:
        area = sum(p[0] * (q[1] - p[1]) for p, q in self.line_segments())
        return area

    def surrounds(self, point):
        """Check if point is inside the polygon

        The right and bottom edges are not considered part of the area"""
        print(point)
        x, y = point
        crossing = 0
        for line in self.line_segments():
            if line[0][0] == line[1][0] > x:  # vertical
                ys = sorted((line[0][1], line[1][1], y))
                if y == ys[1] and y != ys[2]:
                    crossing += 1
        return crossing % 2 == 1


def rect2poly(rect: pygame.Rect):
    return ClosedPolyline(
        rect.topleft, rect.topright, rect.bottomright, rect.bottomleft
    )
