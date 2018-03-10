from fields import RectangleField
from renderers import TkRenderContext, RectangleRenderer


class GameManager:
    """
    Хранит текущее состояние игры, а также управляет им.
    """
    def __init__(self):
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

    def left_button_click(self, event):
        print('left button click!')

    def right_button_click(self, event):
        print('right button click!')

    def middle_button_click(self, event):
        print('middle button click!')

    def all_safe_opened(self):
        pass
