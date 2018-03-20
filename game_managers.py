import time

from fields import RectangleField
from api import FieldParams


class GameManager:
    """
    Хранит текущее состояние игры, а также управляет им.
    """
    def __init__(self):
        self.button_method_map = {
            1: 'left_button_click',
            2: 'middle_button_click',
            3: 'right_button_click'
        }
        self.field_params = None
        self.field = None
        self.user_won = None
        self.game_active = None

        self.mark_count = None
        self.safe_opened_count = None
        self.safe_count = None

        self.game_start_clock = None
        self.game_finish_clock = None

        self.render_context = None
        self.new_game()

    def set_render_context(self, render_context):
        render_context.resize(
            *self.field.get_canvas_size())
        self.render_context = render_context
        if self.field.renderer.context is None:
            self.field.renderer.context = render_context

    def new_game(self):
        # FIXME: Сейчас класс поля, а также его
        # размеры заданы хардкодом. В дальнейшем
        # следует использовать фабрику, берущую
        # информацию о типе поля в
        # конфиг-словаре.
        self.field_params = FieldParams(
            width=12, height=12, mines_count=14)
        self.field = RectangleField(
            self.field_params, self)

        if self.render_context is not None:
            self.render_context.resize(self.field.get_canvas_size())

        self.user_won = False
        self.game_active = True

        self.game_start_clock = None
        self.game_finish_clock = None

        self.mark_count = 0
        self.safe_opened_count = 0
        self.safe_count = self.field.cell_count - self.field_params.mines_count

    def mouse_click(self, event):
        position = self.field.get_position_by_pixel((event.x, event.y))
        if self.field.valid_position(position):
            idx = self.field.get_idx_by_position(position)
            getattr(
                self.field.cells[idx],
                self.button_method_map[event.num]
            )()
            self.field.render()

    def safe_cell_opened(self):
        self.safe_opened_count += 1
        if self.safe_opened_count == self.safe_count:
            self.all_safe_opened()

    def add_mark(self, mark_count):
        self.mark_count += mark_count

    def get_game_time(self):
        if self.game_start_clock is None:
            return 0
        if self.game_finish_clock is None:
            return int(0.5 + time.clock() - self.game_start_clock)
        return int(0.5 + self.game_finish_clock - self.game_start_clock)

    def get_remaining_mines_count(self):
        return self.field_params.mines_count - self.mark_count

    def all_safe_opened(self):
        self.user_won = True
