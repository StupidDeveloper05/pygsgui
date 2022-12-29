import pygame
from abc import *

class ISGUIBasicObject(metaclass=ABCMeta):
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self._width = width
        self._height = height
        self._id = None

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def render(self, sc: pygame.Surface):
        pass

    @abstractmethod
    def hover_update(self):
        pass

    @abstractmethod
    def hover_reset(self):
        pass

    @property
    def id(self):
        return self._id
