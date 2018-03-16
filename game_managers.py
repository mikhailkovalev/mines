from fields import RectangleField
from renderers import TkRenderContext, RectangleRenderer
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

    def mouse_click(self, event):
        position = self.field.get_position_by_pixel((event.x, event.y))
        if self.field.valid_position(position):
            idx = self.field.get_idx_by_position(position)
            getattr(
                self.field.cells[idx],
                self.button_method_map[event.num]
            )()
            self.field.render()

    def all_safe_opened(self):
        pass
