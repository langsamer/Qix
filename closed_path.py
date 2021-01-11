from typing import List

from paths import point_is_on_line


class Polygon:
    """
    A Polygon stores a sequence of points in order.
    """
    def __init__(self, *args):
        self.points: List = list(args)

    def __len__(self):
        return len(self.points)

    def __contains__(self, item):
        return item in self.points

    def __iter__(self):
        return iter(self.points)

    def line_segments(self):
        return list(zip(self.points, self.points[1:] + [self.points[0]]))

    def insert(self, point, after=None):
        insert_at = 0
        if after:
            insert_at = self.points.index(after) + 1
        else:
            for insert_at, ls in enumerate(self.line_segments(), 1):
                if point_is_on_line(point, ls):
                    break
            else:  # no suitable line segment found
                raise ValueError(f"Point {point} is not on path")
        self.points[insert_at:insert_at] = [point]

    def replace(self, sub_path):
        sub_path = list(sub_path)
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
        if start < end:
            points = self.points[:start] + sub_path + self.points[end+1:]
        else:
            points = sub_path + self.points[end+1:start]
        return self.__class__(*points)

    def split(self, sub_path):
        forward = self.replace(sub_path)
        backward = self.replace(reversed(sub_path))
        return forward, backward
