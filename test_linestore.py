import pytest

from linestore import LineStore, polyline2linesegments, line_intersect
from pygame.math import Vector2


def test_linestore_init():
    ls1 = LineStore('horizontal')
    ls2 = LineStore('vertical')
    assert ls1
    assert ls2


def test_linestore_init_requires_dim():
    """Not passing 'horizontal' or 'vertical' as dim results in an error"""
    with pytest.raises(ValueError):
        LineStore('something else')


def test_linestore_add_horizontal1():
    line = ((1, 2), (3, 4))
    ls = LineStore('horizontal')
    ls.add(line)
    assert (1, 3) in ls.lines[2]


def test_linestore_add_horizontal2():
    line1 = ((1, 2), (3, 4))
    line2 = ((5, 6), (10, 6))
    ls = LineStore('horizontal')
    ls.add(line1)
    ls.add(line2)
    assert (1, 3) in ls.lines[2]
    assert (5, 10) in ls.lines[6]


def test_linestore_add_horizontal3():
    line1 = ((1, 6), (3, 6))
    line2 = ((5, 6), (10, 6))
    ls = LineStore('horizontal')
    ls.add(line1)
    ls.add(line2)
    assert (1, 3) in ls.lines[6]
    assert (5, 10) in ls.lines[6]


def test_linestore_add_vertical1():
    line = ((3, 2), (3, 4))
    ls = LineStore('vertical')
    ls.add(line)
    assert (2, 4) in ls.lines[3]


def test_linestore_add_vertical2():
    line1 = ((3, 2), (3, 4))
    line2 = ((5, 6), (5, 19))
    ls = LineStore('vertical')
    ls.add(line1)
    ls.add(line2)
    assert (2, 4) in ls.lines[3]
    assert (6, 19) in ls.lines[5]


def test_linestore_add_vertical3():
    line1 = ((5, 1), (5, 3))
    line2 = ((5, 4), (5, 10))
    ls = LineStore('vertical')
    ls.add(line1)
    ls.add(line2)
    assert (1, 3) in ls.lines[5]
    assert (4, 10) in ls.lines[5]


def test_linestore_add_simplify1():
    """Where lines overlap, LineStore.simplify merges them, and the original line segments are removed"""
    line1 = ((5, 1), (5, 5))
    line2 = ((5, 4), (5, 10))
    ls = LineStore('vertical')
    ls.add(line1)
    ls.add(line2)
    ls.simplify(5)
    assert (1, 10) in ls.lines[5]
    assert (1, 5) not in ls.lines[5]
    assert (4, 10) not in ls.lines[5]


def test_linestore_add_simplify2():
    """Where lines do not overlap, LineStore.simplify keeps them separate"""
    line1 = ((5, 1), (5, 3))
    line2 = ((5, 4), (5, 10))
    ls = LineStore('vertical')
    ls.add(line1)
    ls.add(line2)
    ls.simplify(5)
    assert (1, 3) in ls.lines[5]
    assert (4, 10) in ls.lines[5]


def test_linestore_get_lines_horizontal():
    line1 = ((0, 1), (4, 1))
    line2 = ((5, 1), (7, 1))
    line3 = ((6, 2), (7, 2))
    line4 = ((3, 5), (6, 5))
    ls = LineStore('horizontal')
    ls.add(line1)
    ls.add(line2)
    ls.add(line3)
    ls.add(line4)
    assert len(ls.get_lines(1)) == 2
    assert line1 in ls.get_lines(1)
    assert line2 in ls.get_lines(1)
    assert ls.get_lines((5)) == [line4]


def test_linestore_get_lines_vertical():
    line1 = ((5, 1), (5, 4))
    line2 = ((5, 6), (5, 10))
    line3 = ((6, 2), (6, 10))
    line4 = ((7, 0), (7, 5))
    ls = LineStore('vertical')
    ls.add(line1)
    ls.add(line2)
    ls.add(line3)
    ls.add(line4)
    assert len(ls.get_lines(5)) == 2
    assert line1 in ls.get_lines(5)
    assert line2 in ls.get_lines(5)


def test_linestore_get_near_horizontal():
    line1 = ((0, 1), (4, 1))
    line2 = ((5, 1), (7, 1))
    line3 = ((6, 2), (7, 2))
    line4 = ((3, 5), (6, 5))
    ls = LineStore('horizontal')
    ls.add(line1)
    ls.add(line2)
    ls.add(line3)
    ls.add(line4)
    assert len(ls.get_near(1)) == 3
    assert line1 in ls.get_near(1)
    assert line2 in ls.get_near(1)
    assert line2 in ls.get_near(1)
    assert line4 not in ls.get_near(1)


def test_linestore_get_near_vertical():
    line1 = ((5, 1), (5, 4))
    line2 = ((5, 6), (5, 10))
    line3 = ((6, 2), (6, 10))
    line4 = ((7, 0), (7, 5))
    ls = LineStore('vertical')
    ls.add(line1)
    ls.add(line2)
    ls.add(line3)
    ls.add(line4)
    lines_near_6 = ls.get_near(6)
    assert lines_near_6[0] == line3
    assert lines_near_6[1] == line1
    assert lines_near_6[2] == line2
    assert lines_near_6[3] == line4


def test_polyline2linesegments():
    pl = [(0, 0), (0, 2), (3, 2), (3, 5)]
    expected = [((0, 0), (0, 2)), ((0, 2), (3, 2)), ((3, 2), (3, 5))]
    assert polyline2linesegments(pl) == expected


def test_polyline2linesegments_requires_more_than_1_point():
    pl = [(10, 10)]
    with pytest.raises(ValueError) as exc:
        polyline2linesegments(pl)


def test_line_intersect0():
    ls = LineStore('horizontal')
    the_line = ((1, 1), (2, 1))
    assert type(line_intersect(the_line, ls)) == tuple


def test_line_intersect_horizontal_overlap1():
    line1 = ((0, 1), (4, 1))
    line2 = ((5, 1), (7, 1))
    line3 = ((6, 2), (7, 2))
    line4 = ((3, 5), (6, 5))
    ls = LineStore('horizontal')
    ls.add(line1)
    ls.add(line2)
    ls.add(line3)
    ls.add(line4)
    the_line = ((1, 1), (2, 1))
    assert line_intersect(the_line, ls) == the_line


def test_line_intersect_horizontal_overlap2():
    line1 = ((0, 1), (4, 1))
    line3 = ((6, 2), (7, 2))
    line4 = ((3, 5), (6, 5))
    ls = LineStore('horizontal')
    ls.add(line1)
    ls.add(line3)
    ls.add(line4)
    the_line = ((1, 1), (6, 1))
    assert line_intersect(the_line, ls) == ((1, 1), (4, 1))


def test_line_intersect_horizontal_overlap_single_point():
    line1 = ((0, 1), (4, 1))
    line3 = ((6, 2), (7, 2))
    line4 = ((3, 5), (6, 5))
    ls = LineStore('horizontal')
    ls.add(line1)
    ls.add(line3)
    ls.add(line4)
    the_line = ((4, 1), (6, 1))
    assert line_intersect(the_line, ls) == (4, 1)


def test_line_intersect_horizontal_overlap_single_point_ignore():
    line1 = ((0, 1), (4, 1))
    line3 = ((6, 2), (7, 2))
    line4 = ((3, 5), (6, 5))
    ls = LineStore('horizontal')
    ls.add(line1)
    ls.add(line3)
    ls.add(line4)
    the_line = ((4, 1), (6, 1))
    assert not line_intersect(the_line, ls, ignore=(4, 1))


def test_line_intersect2_horizontal_no_overlap():
    line1 = ((0, 1), (4, 1))
    line2 = ((5, 1), (7, 1))
    line3 = ((6, 2), (7, 2))
    line4 = ((3, 5), (6, 5))
    ls = LineStore('horizontal')
    ls.add(line1)
    ls.add(line2)
    ls.add(line3)
    ls.add(line4)
    the_line = ((1, 2), (2, 2))
    assert not line_intersect(the_line, ls)


def test_line_intersect_vertical_overlap1():
    line1 = ((0, 1), (0, 4))
    line2 = ((5, 2), (5, 10))
    line3 = ((7, 20), (7, 25))
    line4 = ((3, 5), (3, 15))
    ls = LineStore('vertical')
    ls.add(line1)
    ls.add(line2)
    ls.add(line3)
    ls.add(line4)
    the_line = ((7, 19), (7, 21))
    assert line_intersect(the_line, ls)


def test_line_intersect_vertical_overlap2():
    line1 = ((0, 1), (0, 4))
    line2 = ((5, 2), (5, 10))
    line3 = ((7, 20), (7, 25))
    line4 = ((3, 5), (3, 15))
    ls = LineStore('vertical')
    ls.add(line1)
    ls.add(line2)
    ls.add(line3)
    ls.add(line4)
    the_line = ((7, 19), (7, 21))
    assert line_intersect(the_line, ls) == ((7, 20), (7, 21))


def test_line_intersect_vertical_overlap_single_point():
    line1 = ((0, 1), (0, 4))
    line2 = ((5, 2), (5, 10))
    line3 = ((7, 20), (7, 25))
    line4 = ((3, 5), (3, 15))
    ls = LineStore('vertical')
    ls.add(line1)
    ls.add(line2)
    ls.add(line3)
    ls.add(line4)
    the_line = ((3, 2), (3, 5))
    assert line_intersect(the_line, ls) == (3, 5)


def test_line_intersect_vertical_overlap_single_point_ignore():
    line1 = ((0, 1), (0, 4))
    line2 = ((5, 2), (5, 10))
    line3 = ((7, 20), (7, 25))
    line4 = ((3, 5), (3, 15))
    ls = LineStore('vertical')
    ls.add(line1)
    ls.add(line2)
    ls.add(line3)
    ls.add(line4)
    the_line = ((3, 2), (3, 5))
    assert not line_intersect(the_line, ls, ignore=(3, 5))


def test_line_intersect2_vertical_no_overlap():
    line1 = ((0, 1), (0, 4))
    line2 = ((5, 2), (5, 10))
    line3 = ((7, 20), (7, 25))
    line4 = ((3, 5), (3, 15))
    ls = LineStore('vertical')
    ls.add(line1)
    ls.add(line2)
    ls.add(line3)
    ls.add(line4)
    the_line = ((3, 2), (3, 4))
    assert not line_intersect(the_line, ls)


def test_line_intersect_horizontal_intersection():
    line1 = ((0, 1), (5, 1))
    line2 = ((6, 1), (15, 1))
    line3 = ((7, 20), (17, 20))
    line4 = ((3, 5), (13, 5))
    ls = LineStore('horizontal')
    ls.add(line1)
    ls.add(line2)
    ls.add(line3)
    ls.add(line4)
    the_line = ((6, 1), (6, 9))  # vertical line!
    assert line_intersect(the_line, ls)
    assert (6, 1) == line_intersect(the_line, ls)


def test_line_intersect_horizontal_intersection_ignore():
    line1 = ((0, 1), (5, 1))
    line2 = ((6, 1), (15, 1))
    line4 = ((3, 5), (13, 5))
    ls = LineStore('horizontal')
    ls.add(line1)
    ls.add(line2)
    ls.add(line4)
    the_line = ((8, 0), (8, 4))  # vertical line!
    assert line_intersect(the_line, ls) == (8, 1)
    assert not line_intersect(the_line, ls, ignore=(8, 1))


def test_line_intersect_horizontal_intersection_ignore2():
    line1 = ((0, 1), (5, 1))
    line2 = ((6, 1), (15, 1))
    line4 = ((3, 5), (13, 5))
    ls = LineStore('horizontal')
    ls.add(line1)
    ls.add(line2)
    ls.add(line4)
    the_line = ((8, 0), (8, 6))  # vertical line!
    assert line_intersect(the_line, ls) == (8, 1)
    assert line_intersect(the_line, ls, ignore=(8, 1)) == (8, 5)
    assert line_intersect(the_line, ls, ignore=(8, 5)) == (8, 1)


def test_line_intersect1_horizontal_no_intersection():
    line1 = ((0, 1), (4, 1))
    line2 = ((6, 1), (15, 1))
    line3 = ((7, 20), (17, 20))
    line4 = ((3, 5), (13, 5))
    ls = LineStore('horizontal')
    ls.add(line1)
    ls.add(line2)
    ls.add(line3)
    ls.add(line4)
    the_line = ((5, 1), (5, 4))  # vertical line!
    assert not line_intersect(the_line, ls)


def test_line_intersect1_vertical_intersection():
    line1 = ((0, 1), (0, 4))
    line2 = ((5, 2), (5, 10))
    line3 = ((7, 20), (7, 25))
    line4 = ((3, 5), (3, 15))
    ls = LineStore('vertical')
    ls.add(line1)
    ls.add(line2)
    ls.add(line3)
    ls.add(line4)
    the_line = ((6, 22), (9, 22))  # horizontal line!
    assert line_intersect(the_line, ls)
    assert (7, 22) == line_intersect(the_line, ls)


def test_line_intersect_vertical_intersection_ignore():
    line1 = ((0, 1), (0, 4))
    line2 = ((5, 2), (5, 10))
    line3 = ((7, 20), (7, 25))
    line4 = ((3, 5), (3, 15))
    ls = LineStore('vertical')
    ls.add(line1)
    ls.add(line2)
    ls.add(line3)
    ls.add(line4)
    the_line = ((6, 22), (9, 22))  # horizontal line!
    assert not line_intersect(the_line, ls, ignore=(7, 22))


def test_line_intersect_vertical_intersection_ignore2():
    line1 = ((0, 1), (0, 4))
    line2 = ((5, 2), (5, 10))
    line3 = ((7, 20), (7, 25))
    line4 = ((3, 5), (3, 15))
    ls = LineStore('vertical')
    ls.add(line1)
    ls.add(line2)
    ls.add(line3)
    ls.add(line4)
    the_line = ((2, 8), (9, 8))  # horizontal line!
    assert line_intersect(the_line, ls)
    assert line_intersect(the_line, ls, ignore=(5, 8)) == (3, 8)
    assert line_intersect(the_line, ls, ignore=(3, 8)) == (5, 8)


def test_line_intersect1_vertical_no_intersection():
    line1 = ((0, 1), (0, 4))
    line2 = ((5, 2), (5, 10))
    line3 = ((7, 20), (7, 25))
    line4 = ((3, 5), (3, 15))
    ls = LineStore('vertical')
    ls.add(line1)
    ls.add(line2)
    ls.add(line3)
    ls.add(line4)
    the_line = ((6, 14), (9, 14))  # horizontal line!
    assert not line_intersect(the_line, ls)
