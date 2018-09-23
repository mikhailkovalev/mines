import os.path
from copy import copy
from abc import abstractmethod

import tkinter as tk
from PIL import Image, ImageTk

from api import SingletonAbcMeta
from cells import CellStatus


class AbstractRenderContext(metaclass=SingletonAbcMeta):
    """
    Предоставляет интерфейс рисования примитивов
    """

    @abstractmethod
    def draw_image(self, position, image):
        pass

    @abstractmethod
    def draw_rectangle(self, position, size):
        pass

    @abstractmethod
    def draw_text(self, position, text, font):
        pass

    @abstractmethod
    def resize(self, width, height):
        pass

    @abstractmethod
    def clear(self):
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

    def clear(self):
        self.canvas.delete('all')


class AbstractRenderer(metaclass=SingletonAbcMeta):
    def __init__(self, context):
        self.context = context

    @abstractmethod
    def render(self, cell):
        pass

    @abstractmethod
    def clear(self):
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

    def clear(self):
        self.context.clear()


class HexagonalRenderer(AbstractRenderer):
    pass
