import pytest

from linestore import LineStore
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


