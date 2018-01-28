from abc import ABCMeta, abstractmethod
from enum import IntEnum, auto


class CellStatus(IntEnum):
    CLOSED = auto()
    OPENED = auto()
    MARKED_BY_FLAG = auto()
    MARKED_BY_QUESTION = auto()


class Cell(metaclass=ABCMeta):
    flag_statuses = (
        CellStatus.CLOSED,
        CellStatus.MARKED_BY_FLAG,
        CellStatus.MARKED_BY_QUESTION,
    )
    flag_names = (
        'closed',
        'marked_by_flag',
        'marked_by_question',
    )
    flag_statuses_count = len(flag_statuses)
    assert(len(flag_names) == flag_statuses_count)

    def __init__(self, field, position, image_manager, renderer):
        self.field = field
        self.position = position
        self.image_manager = image_manager
        self.renderer = renderer
        self.status_idx = 0
        self.status = self.flag_statuses[self.status_idx]
        self.image = image_manager.get(self.flag_names[self.status_idx])

    @abstractmethod
    def left_button_click(self):
        pass

    def right_button_click(self):
        if self.status not in self.flag_statuses:
            return

        self.status_idx = (self.status_idx+1) % self.flag_statuses_count
        self.status = self.flag_statuses[self.status_idx]
        image_name = self.flag_names[self.status_idx]
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