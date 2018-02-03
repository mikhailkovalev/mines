from abc import ABCMeta, abstractmethod

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
    def get_cell_position_by_idx(self, idx):
        return tuple()

    @abstractmethod
    def create_fake_field(self, width, height, mines_count):
        self.width = width
        self.height = height
        self.mines_count = mines_count
        self.cell_count = self.get_cell_count(width, height)
        self.safe_count = self.cell_count - mines_count
        self.safe_opened_count = 0

        self.cells = tuple((
            FakeCell(self, self.get_cell_position_by_idx(i))
            for i in range(self.cell_count)
        ))

    def safe_cell_opened(self):
        self.safe_opened_count += 1
        if self.safe_opened_count == self.safe_count:
            self.game.all_safe_opened()

    @abstractmethod
    def generate(self, position):
        pass

    @abstractmethod
    def get_neighbors(self, position):
        pass
