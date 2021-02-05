import pytest

from polyline import Polyline


# Note: most of the basic behaviour is tested by test_closed_polyline
# Here we test only what differentiates (or should differentiate)
# open and closed polylines.

def test_convert_polyline_to_list():
    """A Polyline object can be cast to a plain list by list()"""
    points = [(0, 0), (10, 0), (10, 10)]
    path = Polyline(*points)
    assert list(path) == points


def test_polyline_append():
    points = [(0, 0), (10, 0), (10, 10)]
    path = Polyline(*points)
    the_point = (5, 10)
    path.append(the_point)
    assert len(path) == len(points) + 1
    assert the_point in path


def test_polyline_index():
    """A Polyline object can be cast to a plain list by list()"""
    points = [(0, 0), (10, 0), (10, 10)]
    path = Polyline(*points)
    assert path.index((10, 0)) == 1


def test_polyline_number_of_line_segments():
    """an open polyline has one less line segments than it has points"""
    points = [(0, 0), (10, 0), (10, 10)]
    path = Polyline(*points)
    assert len(path) == len(list(path.line_segments())) + 1


def test_polyline_insert_point():
    points = [(0, 0), (10, 0), (10, 10)]
    path = Polyline(*points)
    the_point = (5, 0)
    path.insert(the_point)
    assert len(path) == len(points) + 1
    assert the_point in path


def test_polyline_insert_point_failure():
    """a point to be inserted must lie on the path, you cannot use insert to append or prepend a point."""
    points = [(0, 0), (10, 0), (10, 10)]
    path = Polyline(*points)
    the_point = (5, 10)
    with pytest.raises(ValueError) as exc:
        path.insert(the_point)
    assert "is not on path" in str(exc)


def test_polyline_insert_point_at_position_1():
    points = [(0, 0), (10, 0), (10, 10)]
    path = Polyline(*points)
    the_point = (5, 0)
    path.insert(the_point, after=points[0])
    assert len(path) == len(points) + 1
    assert the_point == path[1]


def test_polyline_insert_point_at_position_end():
    points = [(0, 0), (10, 0), (10, 10)]
    path = Polyline(*points)
    the_point = (5, 0)
    path.insert(the_point, after=points[-1])
    assert len(path) == len(points) + 1
    assert the_point == path[-1]


def test_polyline_replace1():
    points_1 = [(0, 0), (5, 0), (10, 0), (10, 10)]
    path_1 = Polyline(*points_1)
    path_2 = [(5, 0), (5, 5), (10, 0)]
    new_path = path_1.replace(path_2)
    assert len(new_path) == len(path_1) + 1
    assert path_2[0] in new_path
    assert path_2[1] in new_path
    assert path_2[2] in new_path
    assert new_path[2] == path_2[1]


def test_polyline_replace2():
    points_1 = [(0, 0), (5, 0), (10, 0), (10, 10)]
    path_1 = Polyline(*points_1)
    path_2 = [(5, 0), (5, 5), (10, 10)]
    new_path = path_1.replace(path_2)
    assert path_2[0] in new_path
    assert path_2[1] in new_path
    assert path_2[2] in new_path
    assert new_path[2] == path_2[1]


def test_polyline_replace_requires_both_ends_on_path():
    points_1 = [(0, 0), (5, 0), (10, 0), (10, 10)]
    path_1 = Polyline(*points_1)
    path_2 = [(5, 0), (5, 5), (10, 5)]
    with pytest.raises(ValueError) as exc:
        new_path = path_1.replace(path_2)
    assert "point of replacement path must be on" in str(exc)


def test_polyline_replace_fails_when_direction_of_subpath_is_wrong():
    """The replacement path must have the same direction as the current path.
    That is, the starting point of the replacement path must appear in the current path
    before the end point of the replacement path.
    Otherwise, Polyline.replace() raises a ValueError."""
    points_1 = [(0, 0), (5, 0), (10, 0), (10, 10)]
    path_1 = Polyline(*points_1)
    path_2 = [(10, 0), (10, 5), (5, 5), (5, 0)]
    with pytest.raises(ValueError) as exc:
        new_path = path_1.replace(path_2)
    assert "reverse direction" in str(exc)


def test_polyline_intersect1():
    points = [(5, 0), (5, 10), (10, 10)]
    path = Polyline(*points)
    line = ((0, 5), (10, 5))
    assert path.intersect(line) == (5, 5)


def test_polyline_intersect2():
    points = [(5, 0), (5, 10), (10, 10)]
    path = Polyline(*points)
    line = ((0, 3), (8, 3))
    assert path.intersect(line) == (5, 3)


def test_polyline_intersect3():
    points = [(4, 0), (4, 10)]
    path = Polyline(*points)
    line = ((0, 3), (8, 3))
    assert path.intersect(line) == (4, 3)


def test_polyline_intersect4():
    points = [(2, 0), (2, 4)]
    path = Polyline(*points)
    line = ((1, 3), (4, 0))
    assert path.intersect(line) == (2, 2)


def test_polyline_intersect5():
    points = [(2, 0), (2, 4)]
    path = Polyline(*points)
    line = ((1, 3), (3, 2))
    assert path.intersect(line) == (2, 2.5)


def test_polyline_intersect_may_return_none():
    points = [(2, 0), (2, 4)]
    path = Polyline(*points)
    line = ((3, 3), (5, 0))
    assert path.intersect(line) is None
