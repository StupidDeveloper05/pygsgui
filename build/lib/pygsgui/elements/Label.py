import pygame
from overrides import overrides
from pygsgui.core.FriendMethod import FriendMethod
from pygsgui.elements.ISGUIBasicObject import ISGUIBasicObject
from pygsgui.core.UIManager import UIManager


class Label(ISGUIBasicObject):
    ID = 0

    def __init__(self, x: int, y: int, width: int, height: int, ui_manager: UIManager,
                 text="label", text_size=10, window=None, tag=None,
                 auto_push=True, update_flag="ONLY_SCREEN"):
        super().__init__(x, y, width, height)
        self.ui_manager = ui_manager
        self.window = window
        self.update_flag = update_flag
        self.__theme = None
        self.tag = tag
        self._id = "txt_" + str(Label.ID)
        Label.ID += 1

        self.__disable = False

        # surface
        self.__surface = pygame.Surface((self._width, self._height), pygame.SRCALPHA)

        # load theme from ui manager
        if self.tag is None:
            self.__theme = self.ui_manager.theme["Label"]
        else:
            self.__theme = self.ui_manager.theme[self.tag]

        # text setting
        self.__text = text
        self.__text_size = text_size
        self.__font = None
        if self.__theme["text"]["font"]["is_sys"]:
            self.__font = pygame.font.SysFont(self.__theme["text"]["font"]["name"], self.__text_size,
                                              self.__theme["text"]["bold"],
                                              self.__theme["text"]["italic"])
            self.__font.set_underline(self.__theme["text"]["underline"])
        else:
            self.__font = pygame.font.Font(self.__theme["text"]["font"]["name"], self.__text_size)
            self.__font.set_bold(self.__theme["text"]["bold"])
            self.__font.set_italic(self.__theme["text"]["italic"])
            self.__font.set_underline(self.__theme["text"]["underline"])

        self.__normal_text = self.__font.render(self.__text, self.__theme["text"]["antialias"], self.__theme["text"]["color"]["normal"])
        self.__hover_text = self.__font.render(self.__text, self.__theme["text"]["antialias"], self.__theme["text"]["color"]["hover"])
        self.__disable_text = self.__font.render(self.__text, self.__theme["text"]["antialias"], self.__theme["text"]["color"]["disable"])
        self.__tw, self.__th = self.__font.size(text)
        self.__tw = self.__tw / 2
        self.__th = self.__th / 2

        # hover values
        self.__hover = False

        # push ui manager
        if auto_push:
            if self.window is None:
                self.ui_manager.push(self, self._id)
            else:
                self.window.push(self, self._id)

        self.__is_bg_color = self.__theme.get("color")

    @FriendMethod("pygsgui.UIManager", "pygsgui.elements.Window")
    def hover_update(self):
        mx, my = self.ui_manager.event_manager.MOUSE_POS
        if self.window is not None:
            mx, my = self.window.get_relative_pos(mx, my, flag=self.update_flag)
        if self.x + self._width / 2 - self.__tw < mx < self.x + self._width / 2 + self.__tw and \
                self.y + self._height / 2 - self.__th < my < self.y + self._height / 2 + self.__th:
            self.__hover = True
        else:
            self.__hover = False
        return self.__hover

    @FriendMethod("pygsgui.UIManager", "pygsgui.elements.Window")
    def hover_reset(self):
        self.__hover = False

    @overrides
    def update(self):
        return

    @overrides
    def render(self, sc: pygame.Surface):
        if not self.window:
            sc = self.ui_manager.sc
        self.__surface.fill("#00000000")
        if self.__disable:
            if self.__is_bg_color is not None:
                pygame.draw.rect(self.__surface, self.__theme["color"]["disable"], (0, 0, self._width, self._height))
            self.__surface.blit(self.__disable_text, (self._width / 2 - self.__tw, self._height / 2 - self.__th))
        elif not self.__hover:
            if self.__is_bg_color is not None:
                pygame.draw.rect(self.__surface, self.__theme["color"]["normal"], (0, 0, self._width, self._height))
            self.__surface.blit(self.__normal_text, (self._width / 2 - self.__tw, self._height / 2 - self.__th))
        elif self.__hover:
            if self.__is_bg_color is not None:
                pygame.draw.rect(self.__surface, self.__theme["color"]["hover"], (0, 0, self._width, self._height))
            self.__surface.blit(self.__hover_text, (self._width / 2 - self.__tw, self._height / 2 - self.__th))

        sc.blit(self.__surface, (self.x, self.y))

    @property
    def hover(self):
        return self.__hover

    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, value: str):
        self.__text = value
        self.__re_text()

    @property
    def text_size(self):
        return self.__text_size

    @text_size.setter
    def text_size(self, size: int):
        self.__text_size = size
        if self.__theme["text"]["font"]["is_sys"]:
            self.__font = pygame.font.SysFont(self.__theme["text"]["font"]["name"], self.__text_size,
                                              self.__theme["text"]["bold"],
                                              self.__theme["text"]["italic"])
            self.__font.set_underline(self.__theme["text"]["underline"])
        else:
            self.__font = pygame.font.Font(self.__theme["text"]["font"]["name"], self.__text_size)
            self.__font.set_bold(self.__theme["text"]["bold"])
            self.__font.set_italic(self.__theme["text"]["italic"])
            self.__font.set_underline(self.__theme["text"]["underline"])

        self.__re_text()

    @property
    def underline(self):
        return self.__theme["text"]["underline"]

    @underline.setter
    def underline(self, value: bool):
        if self.__theme["text"]["underline"] == value:
            return
        self.__theme["text"]["underline"] = value
        self.__font.set_underline(self.__theme["text"]["underline"])

        self.__re_text()

    @property
    def bold(self):
        return self.__theme["text"]["bold"]

    @bold.setter
    def bold(self, value: bool):
        if self.__theme["text"]["bold"] == value:
            return
        self.__theme["text"]["bold"] = value
        self.__font.set_bold(self.__theme["text"]["bold"])

        self.__re_text()

    @property
    def italic(self):
        return self.__theme["text"]["italic"]

    @italic.setter
    def italic(self, value: bool):
        if self.__theme["text"]["italic"] == value:
            return
        self.__theme["text"]["italic"] = value
        self.__font.set_italic(self.__theme["text"]["italic"])

        self.__re_text()

    def set_disable(self, value: bool):
        self.__disable = value

    def __re_text(self):
        self.__normal_text = self.__font.render(self.__text, self.__theme["text"]["antialias"],
                                                self.__theme["text"]["color"]["normal"])
        self.__hover_text = self.__font.render(self.__text, self.__theme["text"]["antialias"],
                                               self.__theme["text"]["color"]["hover"])
        self.__disable_text = self.__font.render(self.__text, self.__theme["text"]["antialias"],
                                                 self.__theme["text"]["color"]["disable"])
        self.__tw, self.__th = self.__font.size(self.__text)
        self.__tw = self.__tw / 2
        self.__th = self.__th / 2

    def resized(self):
        self.__surface = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
