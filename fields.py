from random import randrange
from abc import ABCMeta, abstractmethod

from api import (abs_sub, oddr_to_cube, cube_to_oddr, cube_distance,
                 cube_round, ONE_DIV_THREE, TWO_DIV_THREE, ONE_DIV_SQRT_THREE)
from cells import FakeCell, cell_fabric
from renderers import RectangleRenderer, HexagonalRenderer
from functools import partial


class AbstractField(metaclass=ABCMeta):
    def __init__(self, field_params, game_manager):
        self.width = None
        self.height = None
        self.mines_count = None

        self.game_manager = game_manager

        # Общее количество ячеек
        self.cell_count = None

        # Количество открытых безопасных ячеек и
        # общее количество безопасных ячеек
        self.safe_opened_count = None
        self.safe_count = None

        # Коллекция ячеек
        self.cells = None

        # self.renderer = self.create_renderer(game_manager.render_context)
        self.renderer = self.create_renderer(
            getattr(game_manager, 'render_context', None))
        self.create_fake_field(field_params)

    @abstractmethod
    def get_cell_count(self, width, height):
        return 0

    @abstractmethod
    def get_position_by_idx(self, idx):
        return tuple()

    @abstractmethod
    def get_idx_by_position(self, position):
        return 0

    # @abstractmethod
    def get_position_by_pixel(self, pixel):
        return 0

    def get_cell_by_position(self, position):
        idx = self.get_idx_by_position(position)
        return self.cells[idx]

    @staticmethod
    @abstractmethod
    def create_renderer(render_context):
        pass

    def create_fake_field(self, field_params):
        """
        Создаёт поле из фальшивых ячеек, клик по любой
        из которых запускает генерацию настоящего поля.

        Нужно для того, чтобы пользователь гарантированно
        первым кликом не подорвался на мине, и получил
        возможность нормально начать игру.
        :param field_params:
        :return:
        """
        self.width, self.height, self.mines_count = field_params
        self.cell_count = self.get_cell_count(
            self.width, self.height)
        self.safe_count = self.cell_count - self.mines_count
        self.safe_opened_count = 0

        self.cells = tuple(
            FakeCell(self.get_position_by_idx(i), self, self.game_manager)
            for i in range(self.cell_count)
        )

    def generate(self, safe_position):
        """
        Генерирует минное поле, такое, что в
        ячейке с координатами safe_position и в
        ячейках вокруг неё нет мин.
        """
        mined_cells = set()
        mined_count = 0
        while mined_count < self.mines_count:
            idx = randrange(self.cell_count)
            position = self.get_position_by_idx(idx)
            if (idx in mined_cells
                    or self.are_neighbors(position, safe_position)):
                continue

            mined_cells.add(idx)
            mined_count += 1

        partial_cell_fabric = partial(
            cell_fabric, field=self, game_manager=self.game_manager)

        new_cells = tuple(
            partial_cell_fabric(
                type_=('mined' if i in mined_cells else 'safe'),
                position=self.get_position_by_idx(i),
                status=self.cells[i].status
            )
            for i in range(self.cell_count)
        )
        self.cells = new_cells

        # TODO: вынести на уровень выше
        self.cells[self.get_idx_by_position(safe_position)].left_button_click()

    @abstractmethod
    def valid_position(self, position):
        """
        Возвращает True, если ячейка с указанными
        координатами находится в пределах поля.
        """

    @abstractmethod
    def are_neighbors(self, position1, position2):
        return False

    @abstractmethod
    def get_neighbors(self, position):
        """
        Возвращает список всех ячеек, соседних с
        position.
        """

    def render(self):
        for cell in self.cells:
            self.renderer.render(cell)

    def get_canvas_size(self):
        """
        Возвращает ширину и высоту холста в пикселях
        """
        return (self.width * self.renderer.cell_size[0],
                self.height * self.renderer.cell_size[1])


class RectangleField(AbstractField):
    """
    Класс, описывающий прямоугольное минное поле
    """
    @staticmethod
    def create_renderer(render_context):
        return RectangleRenderer(render_context)

    def get_cell_count(self, width, height):
        return width * height

    def get_position_by_idx(self, idx):
        return divmod(idx, self.width)

    def get_idx_by_position(self, position):
        return position[0] * self.width + position[1]

    def get_position_by_pixel(self, pixel):
        column = pixel[0] // self.renderer.cell_size[0]
        row = pixel[1] // self.renderer.cell_size[1]
        return row, column

    def valid_position(self, position):
        return (0 <= position[0] < self.height and
                0 <= position[1] < self.width)

    def are_neighbors(self, position1, position2):
        return max(map(abs_sub, position1, position2)) <= 1

    def get_neighbors(self, position):
        row, column = position

        column_offset = (1, 1, 1, 0, -1, -1, -1, 0)
        row_offset = (-1, 0, 1, 1, 1, 0, -1, -1)
        neighbors_count = len(column_offset)
        assert neighbors_count == len(row_offset)

        checking_positions = (
            (row + row_offset[i], column + column_offset[i])
            for i in range(neighbors_count)
        )
        
        return tuple(
            self.get_cell_by_position(position)
            for position in checking_positions
            if self.valid_position(position)
        )


class HexagonalField(AbstractField):
    def get_cell_count(self, width, height):
        height_div_2, residue = divmod(height, 2)
        cell_count = (width*(height_div_2 + residue) +
                      (width-1)*height_div_2)
        return cell_count

    def get_position_by_idx(self, idx):
        double_row, column = divmod(idx, 2*self.width - 1)
        row = 2 * double_row
        if column >= self.width:
            row += 1
            column -= self.width

        return row, column

    def get_idx_by_position(self, position):
        row, column = position
        row_div_two, row_percent_two = divmod(row, 2)
        idx = (row_div_two * (2*self.width - 1) +
               self.width * row_percent_two + column)
        return idx

    def get_position_by_pixel(self, pixel):
        pixel_x, pixel_y = pixel
        pixel_x -= self.renderer.cell_width / 2
        pixel_y -= self.renderer.cell_height / 2
        one_div_cell_side = 1 / self.renderer.cell_side
        x = (ONE_DIV_SQRT_THREE*pixel_x -
             ONE_DIV_THREE*pixel_y) * one_div_cell_side
        z = (TWO_DIV_THREE * pixel_y) * one_div_cell_side
        y = -x - z

        return cube_to_oddr(cube_round((x, y, z)))

    @staticmethod
    def create_renderer(render_context):
        return HexagonalRenderer(render_context)

    def valid_position(self, position):
        row, column = position

        column_bound = self.width
        if row & 1:
            column_bound -= 1

        return (0 <= row < self.height and
                0 <= column < column_bound)

    def are_neighbors(self, position1, position2):
        cubes = map(oddr_to_cube, (position1, position2))
        return cube_distance(*cubes) <= 1

    def get_neighbors(self, position):
        x_offset = (1, 1, 0, -1, -1, 0)
        y_offset = (-1, 0, 1, 1, 0, -1)
        z_offset = (0, -1, -1, 0, 1, 1)

        neighbors_count = len(x_offset)
        assert (neighbors_count == len(y_offset) and
                neighbors_count == len(z_offset))

        cube = oddr_to_cube(position)

        checking_positions = (
            cube_to_oddr((
                cube[0] + x_offset[i],
                cube[1] + y_offset[i],
                cube[2] + z_offset[i],
            ))
            for i in range(neighbors_count)
        )

        return tuple(
            self.get_cell_by_position(position)
            for position in checking_positions
            if self.valid_position(position)
        )
