import pygame
import pytest

from paths import (
    lines_with_point,
    point_is_on_line,
    split_line_at_point,
    orientation,
    find_path,
)


@pytest.fixture(scope="module")
def boundary_rectangular():
    b = [
        (0, 0),
        (0, 50),
        (40, 50),
        (40, 0),
        (0, 0),
    ]
    yield list(zip(b, b[1:]))


def test_point_is_on_line_true1():
    the_point = (0, 20)
    the_line = ((0, 0), (0, 50))
    assert point_is_on_line(the_point, the_line)


def test_point_is_on_line_true2():
    the_point = (30, 0)
    the_line = ((50, 0), (0, 0))
    assert point_is_on_line(the_point, the_line)


def test_point_is_on_line_true3():
    the_point = (40, 50)
    the_line = ((40, 50), (0, 50))
    assert point_is_on_line(the_point, the_line)


def test_point_is_on_line_true4():
    the_point = (30, 50)
    the_line = ((0, 50), (40, 50))
    assert point_is_on_line(the_point, the_line)


def test_point_is_on_line_false():
    the_point = (5, 20)
    the_line = ((0, 0), (0, 50))
    assert not point_is_on_line(the_point, the_line)


def test_point_is_on_line_false2():
    the_point = (0, 20)
    the_line = ((0, 50), (40, 50))
    assert not point_is_on_line(the_point, the_line)


def test_lines_with_point1():
    all_lines = [
        ((0, 0), (0, 50)),
        ((0, 50), (40, 50)),
        ((40, 50), (40, 0)),
        ((40, 0), (0, 0)),
    ]
    the_point = (0, 20)
    lines = lines_with_point(all_lines, the_point)
    assert len(lines) == 1
    assert all_lines[0] in lines


def test_lines_with_point2():
    all_lines = [
        ((0, 0), (0, 50)),
        ((0, 50), (40, 50)),
        ((40, 50), (40, 0)),
        ((40, 0), (0, 0)),
    ]
    the_point = (0, 50)
    lines = lines_with_point(all_lines, the_point)
    assert len(lines) == 2
    assert all_lines[0] in lines
    assert all_lines[1] in lines


def test_split_line_at_point1():
    the_point = (50, 0)
    the_line = ((50, 0), (0, 0))
    result = split_line_at_point(the_line, the_point)
    assert len(result) == 1
    assert the_line in result


def test_split_line_at_point2():
    """When the line meets the point, the result is always delivered with the
    given point as the first point"""
    the_point = (0, 0)
    the_line = ((50, 0), (0, 0))
    result = split_line_at_point(the_line, the_point)
    assert len(result) == 1
    assert ((0, 0), (50, 0)) in result


def test_split_line_at_point3():
    """When line is split, both segments start with the given point"""
    the_point = (30, 0)
    the_line = ((50, 0), (0, 0))
    result = split_line_at_point(the_line, the_point)
    assert len(result) == 2
    assert ((30, 0), (50, 0)) in result
    assert ((30, 0), (0, 0)) in result


def test_split_line_at_point_value_error():
    the_point = (30, 5)
    the_line = ((50, 0), (0, 0))
    with pytest.raises(ValueError) as exc:
        result = split_line_at_point(the_line, the_point)
    assert "is not on line" in str(exc)


def test_orientation_leftturn1():
    line_from = ((0, 0), (0, 10))
    line_to = ((0, 10), (10, 10))
    assert orientation(line_from, line_to) == 1, "Should be left turn"


def test_orientation_leftturn2():
    line_from = ((10, 0), (0, 0))
    line_to = ((0, 0), (0, 5))
    assert orientation(line_from, line_to) == 1, "Should be left turn"


def test_orientation_rightturn1():
    line_from = ((0, 0), (10, 0))
    line_to = ((10, 0), (10, 10))
    assert orientation(line_from, line_to) == -1, "Should be right turn"


def test_orientation_raises_value_error():
    line_from = ((10, 10), (10, 0))
    line_to = ((0, 10), (0, 0))
    with pytest.raises(ValueError) as exc:
        orientation(line_from, line_to)
    assert "do not connect" in str(exc)


def test_orientation4():
    line_from = ((10, 10), (10, 5))
    line_to = ((10, 5), (3, 5))
    assert orientation(line_from, line_to) == 1, "Should be left turn"


def test_cross():
    """The sign is inverted because screen coordinates are upside down
    (Y axis increases downwards, ie. we are calculating with the mirror image)"""
    v1 = pygame.Vector2(0, 1)
    v2 = pygame.Vector2(1, 0)
    assert v1.cross(v2) == -1


def test_find_path_prequel(boundary_rectangular):
    stix_as_lines = [((0, 20), (20, 20)), ((20, 20), (20, 30)), ((20, 30), (0, 30))]
    closed = [
        ((0, 20), (20, 20)),
        ((20, 20), (20, 30)),
        ((20, 30), (0, 30)),
        ((0, 30), (0, 20)),
    ]
    starting_line = stix_as_lines[-1]
    first_line = lines_with_point(boundary_rectangular, starting_line[1])[0]
    assert first_line == ((0, 0), (0, 50))
    splits = split_line_at_point(first_line, starting_line[1])
    assert splits == [((0, 30), (0, 0)), ((0, 30), (0, 50))]
    assert (
        orientation(starting_line, splits[0]) > 0
        or orientation(starting_line, splits[1]) > 0
    )


def test_find_path(boundary_rectangular):
    stix_as_lines = [((0, 20), (20, 20)), ((20, 20), (20, 30)), ((20, 30), (0, 30))]
    closed = [
        ((0, 20), (20, 20)),
        ((20, 20), (20, 30)),
        ((20, 30), (0, 30)),
        ((0, 30), (0, 20)),
    ]
    assert find_path(boundary_rectangular, stix_as_lines) == closed
