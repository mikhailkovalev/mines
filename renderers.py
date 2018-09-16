import os.path
from itertools import chain
from abc import ABCMeta, abstractmethod

import tkinter as tk
from PIL import Image, ImageTk

from cells import CellStatus, Cell
from api import COS_SIN_DATA, SQRT_THREE


class AbstractRenderContext(metaclass=ABCMeta):
    """
    Предоставляет интерфейс рисования примитивов
    """

    @abstractmethod
    def draw_image(self, position, image):
        pass

    @abstractmethod
    def draw_hexagon(self, center, size):
        """
        Рисует шестиугольник

        :param center: Координаты цента шестиугольника
        :type center: Iterable

        :param size: Размер стороны шестиугольника в пикселях
        :type size: int, float
        """

    @abstractmethod
    def draw_rectangle(self, position, size):
        pass

    @abstractmethod
    def draw_text(self, position, text, font):
        pass

    @abstractmethod
    def resize(self, width, height):
        pass


class TkRenderContext(AbstractRenderContext):
    def __init__(self, canvas=None):
        """
        :type canvas: tkinter.Canvas
        """
        self.canvas = canvas

    def draw_image(self, position, image):
        assert isinstance(image, (tk.PhotoImage, ImageTk.PhotoImage)), \
               'Image must be tkinter.PhotoImage or ImageTk.PhotoImage!'
        self.canvas.create_image(position, image=image, anchor=tk.NW)

    def draw_hexagon(self, center, size, **kwargs):
        vertices = tuple(
            tuple(center[j] + size*COS_SIN_DATA[i][j] for j in range(2))
            for i in range(6)
        )

        default_kwargs = dict(
            outline='grey',
            width=2,
            fill=''
        )

        default_kwargs.update(kwargs)

        self.canvas.create_polygon(
            vertices,
            **default_kwargs
        )

    def draw_rectangle(self, position, size):
        bbox = (
            position[0],
            position[1],
            position[0] + size[0],
            position[1] + size[1],
        )
        self.canvas.create_rectangle(*bbox)

    def draw_text(self, position, text, font):
        self.canvas.create_text(position, text=text, font=font)

    def set_canvas(self, canvas):
        """
        :type canvas: tkinter.Canvas
        """
        self.canvas = canvas

    def resize(self, width, height):
        self.canvas.configure(
            width=width,
            height=height
        )


class AbstractRenderer(metaclass=ABCMeta):
    def __init__(self, context):
        self.context = context

    @abstractmethod
    def render(self, cell):
        assert self.context is not None, 'Render context is None!'


class RectangleRenderer(AbstractRenderer):
    def __init__(self, context):
        super().__init__(context)
        self.images = None
        self.numbers = None
        self.images_are_got = False
        self.cell_size = None
        self.get_images()

    def get_images(self):
        def get_sprite(idx):
            return ImageTk.PhotoImage(sprite.crop((
                0, idx * width,
                width, (idx+1) * width
            )))
        path_to_curren_module = os.path.abspath(__file__)
        path_to_sprite = os.path.join(
            os.path.dirname(path_to_curren_module),
            'res',
            'sprite.jpg'
        )
        sprite = Image.open(path_to_sprite)
        width = sprite.size[0]

        self.cell_size = (width, width)

        numbers_range = range(8, -1, -1)
        ids_range = range(7, 16)
        self.numbers = {
            number: get_sprite(sprite_idx)
            for number, sprite_idx
            in zip(numbers_range, ids_range)
        }

        statuses = (
            CellStatus.CLOSED,
            CellStatus.MARKED_BY_FLAG,
            CellStatus.MARKED_BY_QUESTION,
            CellStatus.ACTIVE_MINE,
            CellStatus.FALSE_MINE,
            CellStatus.PASSIVE_MINE
        )
        ids_range = range(len(statuses))
        self.images = {
            status: get_sprite(sprite_idx)
            for status, sprite_idx
            in zip(statuses, ids_range)
        }
        self.images_are_got = True

    def render(self, cell):
        super().render(cell)

        if not self.images_are_got:
            self.get_images()

        if cell.status == CellStatus.NUMBER:
            sprite = self.numbers[cell.mined_around]
        else:
            sprite = self.images[cell.status]

        position = (
            # ширину ячейки умножаем на номер столбца
            self.cell_size[0] * cell.position[1],

            # высоту ячейки умножаем на номер строки
            self.cell_size[1] * cell.position[0],
        )
        self.context.draw_image(position, sprite)


class HexagonalRenderer(AbstractRenderer):
    def __init__(self, context):
        super().__init__(context)
        self.cell_side = 20
        self.cell_width = self.cell_side * SQRT_THREE
        self.cell_height = 2 * self.cell_side
        self.partial_cell_height = (self.cell_side * 3) >> 1
        self.cell_size = (self.cell_width, self.cell_height)

    def render(self, cell):
        super().render(cell)

        row, column = cell.position

        y = row * self.partial_cell_height + (self.cell_height >> 1)
        x = column * self.cell_width + (1 + (row & 1)) * (self.cell_width / 2)

        center = (x, y)

        if cell.status == CellStatus.CLOSED:
            self.context.draw_hexagon(center, self.cell_side, fill='black')
        elif cell.status == CellStatus.NUMBER:
            self.context.draw_hexagon(center, self.cell_side, fill='white')
            self.context.draw_text(center, str(cell.mined_around), 'arial')
        elif cell.status in Cell.marked_statuses:
            self.context.draw_hexagon(center, self.cell_side, fill='blue')
        elif cell.status == CellStatus.ACTIVE_MINE:
            self.context.draw_hexagon(center, self.cell_side, fill='red')

