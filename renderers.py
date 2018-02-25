from abc import ABCMeta, abstractmethod
import tkinter as tk
from PIL import ImageTk

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
        assert (isinstance(image, (tk.PhotoImage, ImageTk.PhotoImage)),
                "Image must be tkinter.PhotoImage or ImageTk.PhotoImage!")
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
    """
    Собирает изображение поля во внутреннем
    представлении, и отображает его на холст
    """

    @abstractmethod
    def render(self, cell):
        """
        Обновляет рисунок ячейки во внутреннем
        представлении
        """

    @abstractmethod
    def display(self):
        """
        Отображает внутреннее представление на
        экран
        """


class RectangleRenderer(AbstractRenderer):
    def __init__(self, context, cell_size=(32, 32)):
        self.context = context
        self.cell_size = cell_size

    def render_closed(self, cell):
        position = tuple(
            coord * size for coord, size
            in zip(cell.position, self.cell_size)
        )
        self.context.draw_rectangle(position, self.cell_size)

    def render(self, cell):
        pass

    def display(self):
        pass


class HexagonalRenderer(AbstractRenderer):
    pass
