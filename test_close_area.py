import pytest

from paths import lines_with_point, point_is_on_line, split_line_at_point


@pytest.fixture(scope='module')
def boundary_rectangular():
    b = [
        (0, 0), (0, 50),
        (40, 50), (40, 0),
        (0, 0),
    ]


# def test_find_path(boundary_rectangular):
#     stix = [(0, 20), (40, 20)]
#     closed = [
#         (40, 20), (40, 0), (0, 0), (0, 20), (40, 20),
#     ]
#     assert find_path(boundary_rectangular, stix) == closed

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
        ((40, 0), (0, 0))
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
        ((40, 0), (0, 0))
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
    the_point = (30, 0)
    the_line = ((50, 0), (0, 0))
    result = split_line_at_point(the_line, the_point)
    assert len(result) == 2
    assert ((50, 0), (30, 0)) in result
    assert ((30, 0), (0, 0)) in result


def test_split_line_at_point_value_error():
    the_point = (30, 5)
    the_line = ((50, 0), (0, 0))
    with pytest.raises(ValueError) as exc:
        result = split_line_at_point(the_line, the_point)
    assert "is not on line" in str(exc)
