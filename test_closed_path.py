import pytest

from closed_path import Polygon


def test_polygon_init_empty():
    path = Polygon()
    assert not len(path)


def test_polygon_init_nonempty():
    """You can give any number of points to a path at instantiation"""
    points = [(0, 0), (5, 0), (5, 5), (5, 10), (10, 10)]
    path = Polygon(*points)
    assert len(path) == len(points)


def test_polygon_line_segments():
    """You can give any number of points to a path at instantiation"""
    points = [(0, 0), (5, 0), (5, 5), (5, 10), (10, 10)]
    path = Polygon(*points)
    assert len(path.line_segments()) == len(points)


def test_polygon_insert_point():
    points = [(0, 0), (10, 0), (10, 10)]
    path = Polygon(*points)
    the_point = (5, 0)
    path.insert(the_point)
    assert len(path) == len(points) + 1
    assert the_point in path


def test_polygon_insert_point_in_correct_position1():
    """A new point on an existing line segment is added between the
    endpoints of that line segment
    """
    points = [(0, 0), (0, 10), (10, 10)]
    path = Polygon(*points)
    first_point = (0, 5)
    path.insert(first_point)
    second_point = (5, 10)
    path.insert(second_point)
    assert path.points.index(first_point) == 1
    assert path.points.index(second_point) == 3


def test_polygon_insert_point_in_correct_position2():
    """A new point on an existing line segment is added between the
    endpoints of that line segment: works also between last and first point
    """
    points = [(0, 0), (0, 10), (10, 10), (10, 0)]
    path = Polygon(*points)
    the_point = (5, 0)
    path.insert(the_point)
    assert path.points.index(the_point) == 4


def test_polygon_insert_point_error():
    """A new point is refused if it is not on an existing line segment
    """
    points = [(0, 0), (0, 10), (10, 10), (10, 0)]
    path = Polygon(*points)
    the_point = (5, 5)
    with pytest.raises(ValueError) as exc:
        path.insert(the_point)
    assert "not on path" in str(exc)


def test_polygon_can_insert_point_at_specific_linesegment():
    """You can tell a polygon to split a specified line segment by a point,
    even if the new point is not 'on' an existing line segment
    """
    points = [(0, 0), (0, 10), (10, 10), (10, 0)]
    path = Polygon(*points)
    the_point = (5, 5)
    path.insert(the_point, after=(0, 0))
    assert path.points[1] == the_point


def test_polygon_replace_makes_new_path():
    points = [(0, 0), (0, 5), (0, 10), (10, 10), (10, 0), (10, 5)]
    path = Polygon(*points)
    new_points = [(0, 5), (10, 5)]
    new_path = path.replace(new_points)
    assert new_path is not path


def test_polygon_replace_part1():
    """A single line segment that is given as a replacement will be part of the new Polygon"""
    points = [(0, 0), (0, 5), (0, 10), (10, 10), (10, 5), (10, 0)]
    path = Polygon(*points)
    new_points = [(0, 5), (10, 5)]
    # replace the "bottom" part of the path with the line across the middle ((0,5), (10,5))
    new_path = path.replace(new_points)
    assert tuple(new_points) in new_path.line_segments()


def test_polygon_replace_part_replaces():
    """The segments that shall be replaced are not in the resulting Polygon"""
    points = [(0, 0), (0, 5), (0, 10), (10, 10), (10, 5), (10, 0)]
    path = Polygon(*points)
    new_points = [(0, 5), (10, 5)]
    # replace the "bottom" part of the path with the line across the middle ((0,5), (10,5))
    expected = [(0, 0), (0, 5), (10, 5), (10, 0)]
    new_path = path.replace(new_points)
    assert (0, 10) not in new_path.points
    assert (10, 10) not in new_path.points
    assert expected == new_path.points


def test_polygon_replace_part_replaces_across_ends():
    """The segments that shall be replaced are not in the resulting Polygon.
    This also works when the part to be replaced wraps around from the end of the list to the start."""
    points = [(10, 10), (10, 5), (10, 0), (0, 0), (0, 5), (0, 10)]
    path = Polygon(*points)
    new_points = [(0, 5), (10, 5)]
    # replace the "bottom" part of the path with the line across the middle ((0,5), (10,5))
    expected = [(0, 5), (10, 5), (10, 0), (0, 0)]
    new_path = path.replace(new_points)
    assert (0, 10) not in new_path.points
    assert (10, 10) not in new_path.points
    assert expected == new_path.points


def test_polygon_replace_requires_points_on_the_polygon():
    points = [(10, 10), (10, 5), (10, 0), (0, 0), (0, 5), (0, 10)]
    path = Polygon(*points)
    new_points = [(0, 3), (10, 5)]
    with pytest.raises(ValueError) as exc:
        path.replace(new_points)
    assert "must be on polygon" in str(exc)


def test_polygon_split1():
    """Like .replace(), .split() returns a new polygon with the relevant part replaced
    by the polyline given, but it returns a pair of polygons"""
    points = [(0, 0), (0, 5), (0, 10), (10, 10), (10, 5), (10, 0)]
    path = Polygon(*points)
    new_points = [(0, 5), (10, 5)]
    # replace the "bottom" part of the path with the line across the middle ((0,5), (10,5))
    new_path, _ = path.split(new_points)
    assert tuple(new_points) in new_path.line_segments()


def test_polygon_split2():
    """The second polygon returned by .split() is the 'other half' that is defined by the
    splitting path.  There the splitting path is reversed in order to keep the overall
    orientation of each polygon consistent"""
    points = [(0, 0), (0, 5), (0, 10), (10, 10), (10, 5), (10, 0)]
    path = Polygon(*points)
    new_points = [(0, 5), (10, 5)]
    # replace the "bottom" part of the path with the line across the middle ((0,5), (10,5))
    _, new_path = path.split(new_points)
    assert type(new_path) == Polygon
    assert tuple(reversed(new_points)) in new_path.line_segments()


def test_polygon_split3():
    """The first and second polygons returned by .split() are indeed complements"""
    points = [(0, 0), (0, 5), (0, 10), (10, 10), (10, 5), (10, 0)]
    path = Polygon(*points)
    new_points = [(0, 5), (10, 5)]
    # replace the "bottom" part of the path with the line across the middle ((0,5), (10,5))
    path1, path2 = path.split(new_points)
    assert set(path1).intersection(set(path2)) == set(new_points)


def test_polygon_surrounds1():
    points = [(0, 0), (0, 10), (10, 10), (10, 0)]
    path = Polygon(*points)
    the_point = (5, 5)
    assert path.surrounds(the_point)


def test_polygon_surrounds2():
    points = [(0, 0), (0, 10), (5, 10), (5, 1), (7, 1), (7, 10), (10, 10), (10, 0)]
    path = Polygon(*points)
    the_point = (2, 2)
    assert path.surrounds(the_point)


def test_polygon_surrounds_not1():
    points = [(0, 0), (0, 10), (10, 10), (10, 0)]
    path = Polygon(*points)
    the_point = (5, 15)
    assert not path.surrounds(the_point)


def test_polygon_surrounds_not2():
    points = [(0, 0), (0, 10), (5, 10), (5, 1), (7, 1), (7, 10), (10, 10), (10, 0)]
    path = Polygon(*points)
    the_point = (6, 2)
    assert not path.surrounds(the_point)


def test_polygon_surrounds_edge1():
    points = [(0, 0), (0, 10), (10, 10), (10, 0)]
    path = Polygon(*points)
    the_point = (5, 0)
    assert path.surrounds(the_point)


def test_polygon_surrounds_edge2():
    points = [(0, 0), (0, 10), (10, 10), (10, 0)]
    path = Polygon(*points)
    the_point = (0, 5)
    assert path.surrounds(the_point)


def test_polygon_surrounds_not_edge_right():
    points = [(0, 0), (0, 10), (10, 10), (10, 0)]
    path = Polygon(*points)
    the_point = (10, 0)
    assert not path.surrounds(the_point)


def test_polygon_surrounds_not_edge_bottom():
    points = [(0, 0), (0, 10), (10, 10), (10, 0)]
    path = Polygon(*points)
    the_point = (0, 10)
    assert not path.surrounds(the_point)
