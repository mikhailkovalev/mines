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

    def __init__(self,
                 position,
                 field,
                 game_manager,
                 status=CellStatus.CLOSED):
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
        self.game_manager = game_manager
        self.position = position
        self.status = status
        try:
            self.status_idx = self.closed_statuses.index(status)
        except ValueError:
            raise ValueError(
                'Передан неверный аргумент: status={}!'.format(status))

    @abstractmethod
    def set_final_status(self, user_won):
        pass

    @abstractmethod
    def left_button_click(self):
        pass

    def right_button_click(self):
        if self.status not in self.closed_statuses:
            return

        was_marked = self.status in self.marked_statuses

        self.status_idx = (self.status_idx+1) % self.closed_statuses_count
        self.status = self.closed_statuses[self.status_idx]

        become_marked = self.status in self.marked_statuses

        if was_marked and not become_marked:
            self.game_manager.add_mark(-1)
        elif not was_marked and become_marked:
            self.game_manager.add_mark(1)

    @abstractmethod
    def middle_button_click(self):
        pass

    @abstractmethod
    def is_danger(self):
        pass


class MinedCell(Cell):
    def set_final_status(self, user_won):
        if self.status in (CellStatus.CLOSED, CellStatus.MARKED_BY_QUESTION):
            self.status = (
                CellStatus.MARKED_BY_FLAG
                if user_won else
                CellStatus.PASSIVE_MINE
            )

    def left_button_click(self):
        if self.status == CellStatus.CLOSED:
            self.status = CellStatus.ACTIVE_MINE
            self.game_manager.mined_cell_opened()

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
        self.neighbors = None

    def set_final_status(self, user_won):
        if self.status == CellStatus.CLOSED:
            self.status = CellStatus.NUMBER
            self.set_mined_around()
        elif self.status in self.marked_statuses:
            self.status = CellStatus.FALSE_MINE

    def left_button_click(self):
        if self.status != CellStatus.CLOSED:
            return

        self.status = CellStatus.NUMBER
        self.set_mined_around()
        self.game_manager.safe_cell_opened()

        if self.mined_around == 0:
            for cell in self.neighbors:
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

    def set_mined_around(self):
        self.neighbors = self.field.get_neighbors(self.position)
        self.mined_around = sum(1 for cell in self.neighbors if cell.is_danger())


class FakeCell(Cell):
    def left_button_click(self):
        self.field.generate(self.position)

    def middle_button_click(self):
        pass

    def is_danger(self):
        pass

    def set_final_status(self, user_won):
        pass


_cell_types_map = dict(
    fake=FakeCell,
    mined=MinedCell,
    safe=SafeCell
)


def cell_fabric(
        type_, position, field, game_manager, status=CellStatus.CLOSED):
    assert type_ in _cell_types_map, 'Incorrect cell-type "{}"!'.format(type_)
    return _cell_types_map[type_](position, field, game_manager, status)
