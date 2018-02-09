from random import randrange
from abc import ABCMeta, abstractmethod

from api import abs_sub
from cells import FakeCell


class AbstractField(metaclass=ABCMeta):
    def __init__(self, width, height, mines_count, game):
        self.width = None
        self.height = None
        self.mines_count = None

        # Общее количество ячеек
        self.cell_count = None

        # Количество открытых безопасных ячеек и
        # общее количество безопасных ячеек
        self.safe_opened_count = None
        self.safe_count = None

        # Коллекция ячеек
        self.cells = None
        self.game = game
        self.cell_renderer = game.cell_renderer
        self.create_fake_field(width, height, mines_count)

    @abstractmethod
    def get_cell_count(self, width, height):
        return 0

    @abstractmethod
    def get_position_by_idx(self, idx):
        return tuple()

    @abstractmethod
    def get_idx_by_position(self, position):
        return 0

    @abstractmethod
    def create_fake_field(self, width, height, mines_count):
        self.width = width
        self.height = height
        self.mines_count = mines_count
        self.cell_count = self.get_cell_count(width, height)
        self.safe_count = self.cell_count - mines_count
        self.safe_opened_count = 0

        self.cells = tuple((
            FakeCell(self, self.get_position_by_idx(i))
            for i in range(self.cell_count)
        ))

    def safe_cell_opened(self):
        self.safe_opened_count += 1
        if self.safe_opened_count == self.safe_count:
            self.game.all_safe_opened()

    @abstractmethod
    def generate(self, safe_position):
        """
        Генерирует минное поле, такое, что в
        ячейке с координатами safe_position и в
        ячейках вокруг неё нет мин.

        :param safe_position:
        :return:
        """

    @abstractmethod
    def are_neighbors(self, position1, position2):
        return False

    @abstractmethod
    def get_neighbors(self, position):
        """
        Возвращает список всех ячеек, соседних с
        position.

        :param position:
        :return:
        """


class RectangleField(AbstractField):
    """
    Класс, описывающий прямоугольное минное поле
    """
    def get_cell_count(self, width, height):
        return width * height

    def get_position_by_idx(self, idx):
        return divmod(idx, self.width)

    def generate(self, safe_position):
        mined_cells = set()
        mined_count = 0
        while mined_count < self.mines_count:
            idx = randrange(self.cell_count)
            position = self.get_position_by_idx(idx)
            if (idx in mined_cells
                    or self.are_neighbors(position, safe_position)):
                continue

            mined_cells.add(idx)
            mined_count += 1

    def valid_position(self, position):
        return (0 <= position[0] < self.width and
                0 <= position[1] < self.height)

    def are_neighbors(self, position1, position2):
        return max(map(abs_sub, position1, position2)) <= 1

    def get_neighbors(self, position):
        column_offset = (1, 1, 1, 0, -1, -1, -1, 0)
        row_offset = (-1, 0, 1, 1, 1, 0, -1, -1)
        neighbors_count = len(column_offset)
        assert neighbors_count == len(row_offset)

        checking_positions = (
            (position[0] + row_offset[i], position[1] + column_offset[i])
            for i in range(neighbors_count)
        )
        return tuple(filter(self.valid_position, checking_positions))


