# coding: utf-8

import time
from enum import IntEnum, auto

from fields import RectangleField
from api import FieldParams


class LevelEnum(IntEnum):
    ROOKIE = auto()
    VETERAN = auto()
    WARRIOR = auto()
    CUSTOM = auto()


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

        self.level_field_map = {
            LevelEnum.ROOKIE: FieldParams(10, 10, 10),
            LevelEnum.VETERAN: FieldParams(16, 16, 40),
            LevelEnum.WARRIOR: FieldParams(30, 16, 99),
        }

        self.level_names = {
            LevelEnum.ROOKIE: 'Rookie',
            LevelEnum.VETERAN: 'Veteran',
            LevelEnum.WARRIOR: 'Warrior',
            LevelEnum.CUSTOM: 'Custom',
        }

        self.default_field_params = FieldParams(
            width=10, height=10, mines_count=10)
        self.render_context = None
        self._reset_game_state()

    def _reset_game_state(self, field_params=None):
        if field_params is None:
            self.field_params = self.default_field_params
        else:
            self.field_params = field_params
        self.field = RectangleField(
            self.field_params, self)

        self.user_won = False
        self.game_active = True

        self.game_start_clock = None
        self.game_finish_clock = None

        self.mark_count = 0
        self.safe_opened_count = 0
        self.safe_count = self.field.cell_count - self.field_params.mines_count

    def set_render_context(self, render_context):
        render_context.resize(
            *self.field.get_canvas_size())
        self.render_context = render_context
        if self.field.renderer.context is None:
            self.field.renderer.context = render_context
        self.field.render()

    def new_game(self, level, custom_params):
        self._reset_game_state(self.level_field_map.get(level, custom_params))
        if self.render_context is not None:
            self.render_context.resize(*self.field.get_canvas_size())
        self.field.render()

    def mouse_click(self, event):
        if not self.game_active:
            return

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
        if self.game_start_clock is None:
            self.game_start_clock = time.time()

    def mined_cell_opened(self):
        self.finish_game(False)

    def add_mark(self, mark_count):
        self.mark_count += mark_count

    def get_time_info(self):
        if self.game_start_clock is None:
            return 0
        if self.game_finish_clock is None:
            return int(0.5 + time.time() - self.game_start_clock)
        return int(0.5 + self.game_finish_clock - self.game_start_clock)

    def get_mines_info(self):
        return self.field_params.mines_count - self.mark_count

    def all_safe_opened(self):
        self.finish_game(True)

    def finish_game(self, user_won):
        self.user_won = user_won
        self.game_active = False
        self.game_finish_clock = time.time()
        for cell in self.field.cells:
            cell.set_final_status(user_won)
        self.field.render()
