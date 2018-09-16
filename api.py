from collections import namedtuple


FieldParams = namedtuple(
    'FieldParams',
    ('width', 'height', 'mines_count')
)


def abs_sub(x, y): return abs(x - y)


def cube_to_oddr(cube):
    x, y, z = cube
    column = x + ((z - (z&1)) >> 1)
    row = z
    return row, column


def oddr_to_cube(position):
    row, col = position
    x = col - ((row - (row&1)) >> 1)
    z = row
    y = -x - z
    return x, y, z


def cube_distance(cube1, cube2):
    return sum(abs_sub(*e) for e in zip(cube1, cube2)) >> 1


def cube_round(cube):
    rx, ry, rz = map(round, cube)
    dx, dy, dz = map(abs_sub, (rx, ry, rz), cube)

    if dx > dy and dx > dz:
        rx = -ry - rz
    elif dy > dz:
        ry = -rx - rz
    else:
        rz = -rx - ry

    return rx, ry, rz


COS_SIN_DATA = (
    (0.866, 0.500),
    (0.000, 1.000),
    (-0.866, 0.500),
    (-0.866, -0.500),
    (-0.000, -1.000),
    (0.866, -0.500),
)

CUBE_DIRECTIONS = (
    (1, -1, 0),
    (1, 0, -1),
    (0, 1, -1),
    (-1, 1, 0),
    (-1, 0, 1),
    (0, -1, 1),
)

ONE_DIV_THREE = 0.333
TWO_DIV_THREE = 0.667
ONE_DIV_SQRT_THREE = 0.577
SQRT_THREE = 1.732
