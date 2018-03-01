import os.path
from abc import ABCMeta, abstractmethod

import tkinter as tk
from PIL import Image, ImageTk

from cells import CellStatus


class AbstractRenderContext(metaclass=ABCMeta):
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


class TkRenderContext(AbstractRenderContext):
    def __init__(self, canvas):
        """
        :type canvas: tkinter.Canvas
        """
        self.canvas = canvas

    def draw_image(self, position, image):
        assert isinstance(image, (tk.PhotoImage, ImageTk.PhotoImage)), \
               'Image must be tkinter.PhotoImage or ImageTk.PhotoImage!'
        self.canvas.create_image(position, image)

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


class AbstractRenderer(metaclass=ABCMeta):
    def __init__(self, context):
        self.context = context

    @abstractmethod
    def render(self, cell):
        pass


class PictureRectangleRenderer(AbstractRenderer):
    def __init__(self, context):
        super().__init__(context)
        self._get_images()

    def _get_images(self):
        def get_sprite(idx):
            return ImageTk.PhotoImage(sprite.crop((0, idx * width,
                    width, (idx+1) * width)))

        path_to_sprite = os.path.join(
            os.path.dirname(__file__),
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

    def render(self, cell):
        if cell.status == CellStatus.NUMBER:
            sprite = self.numbers[cell.mined_around]
        else:
            sprite = self.images[cell.status]

        position = tuple(
            size * coord
            for size, coord
            in zip(self.cell_size, cell.position)
        )
        self.context.draw_image(position, sprite)


class HexagonalRenderer(AbstractRenderer):
    pass
