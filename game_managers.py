from fields import RectangleField
from renderers import TkRenderContext, RectangleRenderer


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
        self.render_context = TkRenderContext()
        self.new_game()

    def new_game(self):
        # FIXME: Сейчас класс поля, а также его
        # размеры заданы хардкодом. В дальнейшем
        # следует использовать фабрику, берущую
        # информацию о типе поля в
        # конфиг-словаре.
        self.field_width = 12
        self.field_height = 12
        self.mines_count = 14
        self.field = RectangleField(
            self.field_width, self.field_height, self.mines_count, self)

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
