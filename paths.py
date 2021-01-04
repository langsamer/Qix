def point_is_on_line(point, line):
    """Determine if given point lies on the given line

    This function works for horizontal and vertical lines only!"""
    x0, y0 = line[0]
    x1, y1 = line[1]
    if y0 == y1:  # horizontal
        return point[1] == y0 and min(x0, x1) <= point[0] <= max(x0, x1)
    elif x0 == x1:  # vertical
        return point[0] == x0 and min(y0, y1) <= point[1] <= max(y0, y1)
    else:
        raise ValueError("point_is_on_line can only check horizontal and vertical lines")


def lines_with_point(lines, point):
    result = [
        line for line in lines
        if point_is_on_line(point, line)
    ]
    return result


def split_line_at_point(line, point):
    if not point_is_on_line(point, line):
        raise ValueError(f"Point {point} is not on line {line}")
    if point in line:
        return [line]
    else:
        return [(line[0], point), (point, line[1])]


def find_path(all_paths, closing):
    pass
