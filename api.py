from collections import namedtuple


def abs_sub(x, y): return abs(x - y)


FieldParams = namedtuple(
    'FieldSize',
    ('width', 'height', 'mines_count')
)
