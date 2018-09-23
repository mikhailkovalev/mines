from abc import ABCMeta
from collections import namedtuple


def abs_sub(x, y): return abs(x - y)


FieldParams = namedtuple(
    'FieldSize',
    ('width', 'height', 'mines_count')
)


class SingletonAbcMeta(ABCMeta):
    __instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            instance = super().__call__(*args, **kwargs)
            cls.__instances[cls] = instance
        else:
            instance = cls.__instances[cls]
        return instance
