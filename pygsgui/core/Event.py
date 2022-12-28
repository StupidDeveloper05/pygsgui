import pygame


class EventManager:
    def __init__(self):
        self.__press = False
        self.MOUSEDOWN = False
        self.MOUSEUP = False
        self.MOUSE_REL = (0, 0)
        self.MOUSE_POS = (0, 0)
        self.__prev_pos = pygame.mouse.get_pos()

    def update(self):
        pos = pygame.mouse.get_pos()
        self.MOUSE_REL = pos[0] - self.__prev_pos[0], pos[1] - self.__prev_pos[1]
        self.__prev_pos = pos
        self.MOUSE_POS = pos

        if pygame.mouse.get_pressed()[0]:
            if not self.__press:
                self.__press = True
                self.MOUSEDOWN = True
            else:
                self.MOUSEDOWN = False
        else:
            if self.__press:
                self.__press = False
                self.MOUSEUP = True
            else:
                self.MOUSEUP = False
