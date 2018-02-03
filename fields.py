from abc import ABCMeta, abstractmethod, abstractproperty


class AbstractField(metaclass=ABCMeta):
    def __init__(self, game):
        self.game = game

    @abstractmethod
    def generate(self, position):
        pass

    @abstractmethod
    def get_neighbors(self, position):
        pass
