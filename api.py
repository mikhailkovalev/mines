from collections import namedtuple


def abs_sub(x, y): return abs(x - y)


COS_SIN_DATA = (
    (0.866, 0.500),
    (0.000, 1.000),
    (-0.866, 0.500),
    (-0.866, -0.500),
    (-0.000, -1.000),
    (0.866, -0.500),
)

FieldParams = namedtuple(
    'FieldSize',
    ('width', 'height', 'mines_count')
)
