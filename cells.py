from abc import ABCMeta, abstractmethod
from enum import IntEnum, auto


class CellStatus(IntEnum):
    CLOSED = auto()
    MARKED_BY_FLAG = auto()
    MARKED_BY_QUESTION = auto()
    ACTIVE_MINE = auto()
    FALSE_MINE = auto()
    PASSIVE_MINE = auto()
    NUMBER = auto()


class Cell(metaclass=ABCMeta):
    marked_statuses = (
        CellStatus.MARKED_BY_FLAG,
        CellStatus.MARKED_BY_QUESTION,
    )
    closed_statuses = (
        CellStatus.CLOSED,
        CellStatus.MARKED_BY_FLAG,
        CellStatus.MARKED_BY_QUESTION,
    )
    closed_statuses_count = len(closed_statuses)

    def __init__(self, field, position, status=CellStatus.CLOSED):
        """

        :param field:
        :param position:
        :param status: В теории пользователь
            прежде чем открыть какую-либо ячейку
            может поставить сколь угодно флагов.
            Поэтому при создании нормального поля
            из фейкового, нужно переносить статус
            ячеек.
        """
        self.field = field
        self.position = position
        self.renderer = field.renderer
        self.status = status
        try:
            self.status_idx = self.closed_statuses.index(status)
        except ValueError:
            raise ValueError(
                'Передан неверный аргумент: status={}!'.format(status))

    @abstractmethod
    def left_button_click(self):
        pass

    def right_button_click(self):
        if self.status not in self.closed_statuses:
            return

        self.status_idx = (self.status_idx+1) % self.closed_statuses_count
        self.status = self.closed_statuses[self.status_idx]

    @abstractmethod
    def middle_button_click(self):
        pass

    @abstractmethod
    def is_danger(self):
        pass

    def render(self):
        self.renderer.render(self)


class MinedCell(Cell):
    def left_button_click(self):
        if self.status == CellStatus.CLOSED:
            # TODO: уведомить менеджера игры о
            # том, что была открыта
            # заминированная ячейка
            pass

    def middle_button_click(self):
        pass

    def is_danger(self):
        return True


class SafeCell(Cell):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Количество мин вокруг ячейки.
        # Вычисляется в момент открытия ячейки.
        # Обусловлено тем, что в момент создания
        # ячейки ещё могут быть не созданы
        # остальные ячейки на поле.
        self.mined_around = None

    def left_button_click(self):
        if self.status != CellStatus.CLOSED:
            return

        self.status = CellStatus.NUMBER
        neighbors = self.field.get_neighbors(self.position)
        self.mined_around = sum((1 for cell in neighbors if cell.is_danger()))
        self.image = self.image_manager.get(str(self.mined_around))
        self.field.safe_cell_opened()

        if self.mined_around == 0:
            for cell in neighbors:
                cell.left_button_click()

    def middle_button_click(self):
        if self.status != CellStatus.NUMBER:
            return

        neighbors = self.field.get_neighbors(self.position)
        marked_around = sum((
            1 for cell in neighbors
            if cell.status == CellStatus.MARKED_BY_FLAG
        ))

        if marked_around == self.mined_around:
            for cell in neighbors:
                cell.left_button_click()

    def is_danger(self):
        return False


class FakeCell(Cell):
    def left_button_click(self):
        self.field.generate(self.position)

    def middle_button_click(self):
        pass

    def is_danger(self):
        pass
