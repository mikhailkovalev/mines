from abc import ABCMeta, abstractmethod


class AbstractCellRenderer(metaclass=ABCMeta):
    @abstractmethod
    def render(self, position, image):
        pass
