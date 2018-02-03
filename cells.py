from abc import ABCMeta, abstractmethod
from enum import IntEnum, auto


class CellStatus(IntEnum):
    CLOSED = auto()
    OPENED = auto()
    MARKED_BY_FLAG = auto()
    MARKED_BY_QUESTION = auto()


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
    closed_names = (
        'closed',
        'marked_by_flag',
        'marked_by_question',
    )
    closed_statuses_count = len(closed_statuses)
    assert(len(closed_names) == closed_statuses_count)

    def __init__(self, field, position):
        self.field = field
        self.position = position
        self.image_manager = field.image_manager
        self.renderer = field.renderer
        self.status_idx = 0
        self.status = CellStatus.CLOSED
        self.image = self.image_manager.get('closed')

    @abstractmethod
    def left_button_click(self):
        pass

    def right_button_click(self):
        if self.status not in self.closed_statuses:
            return

        self.status_idx = (self.status_idx+1) % self.closed_statuses_count
        self.status = self.closed_statuses[self.status_idx]
        image_name = self.closed_names[self.status_idx]
        self.image = self.image_manager.get(image_name)

    @abstractmethod
    def middle_button_click(self):
        pass

    @abstractmethod
    def is_danger(self):
        pass

    def render(self):
        self.renderer.render(self.position, self.image)

    @abstractmethod
    def set_final_image(self):
        """
        Изображение, которое должно быть
        установлено для ячейки после завершения
        игры
        :return: Image
        """


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

    def set_final_image(self):
        if self.status == CellStatus.OPENED:
            image_name = 'active_mine'
        elif (self.field.game.user_won or
              self.status == CellStatus.MARKED_BY_FLAG):
            image_name = 'marked_by_flag'
        else:
            image_name = 'passive_mine'
        self.image = self.image_manager.get(image_name)


class SafeCell(Cell):
    def __init__(self, field, position, image_manager, renderer):
        super().__init__(field, position, image_manager, renderer)

        # Количество мин вокруг ячейки.
        # Вычисляется в момент открытия ячейки.
        # Обусловлено тем, что в момент создания
        # ячейки ещё могут быть не созданы
        # остальные ячейки на поле.
        self.mined_around = None

    def left_button_click(self):
        if self.status != CellStatus.CLOSED:
            return

        self.status = CellStatus.OPENED
        neighbors = self.field.get_neighbors(self.position)
        self.mined_around = sum((1 for cell in neighbors if cell.is_danger()))
        self.image = self.image_manager.get(str(self.mined_around))
        self.field.safe_cell_opened()

        if self.mined_around == 0:
            for cell in neighbors:
                cell.left_button_click()

    def middle_button_click(self):
        if self.status != CellStatus.OPENED:
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

    def set_final_image(self):
        if self.status in self.marked_statuses:
            self.image = self.image_manager.get('false_mine')
        elif self.mined_around is None:
            neighbors = self.field.get_neighbors(self.position)


class FakeCell(Cell):
    def left_button_click(self):
        self.field.generate(self.position)

    def middle_button_click(self):
        pass

    def is_danger(self):
        pass

    def set_final_image(self):
        pass
