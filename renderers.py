import os.path
from itertools import chain
from abc import ABCMeta, abstractmethod

import tkinter as tk
from PIL import Image, ImageTk

from cells import CellStatus
from api import COS_SIN_DATA


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

    def draw_hexagon(self, center, size):
        vertices = tuple(
            tuple(center[j] + size*COS_SIN_DATA[i][j] for j in range(2))
            for i in range(6)
        )
        self.canvas.create_polygon(
            vertices,
            outline='black',
            width=2,
            fill=''
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
        pass


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
        if self.context is None:
            return

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


class LinearHexagonalRenderer(AbstractRenderer):
    def render(self, cell):
        raise NotImplementedError
