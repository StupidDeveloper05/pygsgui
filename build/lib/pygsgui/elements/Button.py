import pygame
from overrides import overrides
from pygsgui.elements.ISGUIBasicObject import ISGUIBasicObject
from pygsgui.core.FriendMethod import FriendMethod
from pygsgui.core.UIManager import UIManager


class Button(ISGUIBasicObject):
    ID = 0

    def __init__(self, x: int, y: int, width: int, height: int, ui_manager: UIManager,
                 text="", text_size=10, window=None, tag=None,
                 function=None, auto_push=True, update_flag="ONLY_SCREEN"):
        super().__init__(x, y, width, height)
        self.ui_manager = ui_manager
        self.window = window
        self.update_flag = update_flag
        self.__theme = None
        self.tag = tag
        self._id = "btn_" + str(Button.ID)
        Button.ID += 1

        self.__disable = False

        # event function
        self.__function = function
        self.__args = ()
        self.__kwargs = {}

        # load theme from ui manager
        if self.tag is None:
            self.__theme = self.ui_manager.theme["Button"]
        else:
            self.__theme = self.ui_manager.theme[self.tag]

        # surface
        self.__surface = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        self.__padding_lr, self.__padding_tb = self.__theme["padding_lr"], self.__theme["padding_tb"]
        self.__text_surface_width, self.__text_surface_height = max(0, self._width - self.__padding_lr * 2), max(0, self._height - self.__padding_tb * 2)
        self.__text_surface = pygame.Surface((self.__text_surface_width, self.__text_surface_height), pygame.SRCALPHA)

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
        self.__press_text = self.__font.render(self.__text, self.__theme["text"]["antialias"], self.__theme["text"]["color"]["pressed"])
        self.__disable_text = self.__font.render(self.__text, self.__theme["text"]["antialias"], self.__theme["text"]["color"]["disable"])
        self.__tw, self.__th = self.__font.size(text)
        self.__tw = self.__tw / 2
        self.__th = self.__th / 2

        # click values
        self.__click = False
        self.__hover = False
        self.__pressed = False

        # push ui manager
        if auto_push:
            if self.window is None:
                self.ui_manager.push(self, self._id)
            else:
                self.window.push(self, self._id)

        self.__is_border = self.__theme.get("border")

    @FriendMethod("pygsgui.UIManager", "pygsgui.elements.Window")
    def hover_update(self):
        mx, my = self.ui_manager.event_manager.MOUSE_POS
        if self.window is not None:
            mx, my = self.window.get_relative_pos(mx, my, flag=self.update_flag)
        if self.x < mx < self.x + self._width and self.y < my < self.y + self._height:
            self.__hover = True
        else:
            self.__hover = False
        return self.__hover

    @FriendMethod("pygsgui.UIManager", "pygsgui.elements.Window")
    def hover_reset(self, press=False):
        self.__hover = False
        if press:
            self.__pressed = False

    @overrides
    def update(self):
        if not self.__disable:
            mx, my = self.ui_manager.event_manager.MOUSE_POS
            if self.window is not None:
                mx, my = self.window.get_relative_pos(mx, my, flag=self.update_flag)
            self.__click = False

            optional_update = True
            if self.window is not None:
                if self.window.final_update:
                    optional_update = False
            else:
                if self.ui_manager.final_update:
                    optional_update = False

            if optional_update:
                if self.ui_manager.event_manager.MOUSEDOWN:
                    if self.x < mx < self.x + self._width and self.y < my < self.y + self._height:
                        self.__pressed = True
                elif self.ui_manager.event_manager.MOUSEUP:
                    if self.__pressed:
                        if self.x < mx < self.x + self._width and self.y < my < self.y + self._height:
                            self.__pressed = False
                            self.__click = True
                            if self.__function is not None:
                                self.ui_manager.function_manager.push(self.__function, self.__args, self.__kwargs)
                        else:
                            self.__pressed = False

            if self.__pressed:
                return True

    @overrides
    def render(self, sc: pygame.Surface):
        if not self.window:
            sc = self.ui_manager.sc
        self.__surface.fill("#00000000")
        self.__text_surface.fill("#00000000")
        if self.__disable:
            pygame.draw.rect(self.__surface, self.__theme["color"]["disable"], (0, 0, self._width, self._height),
                             border_radius=self.__theme["radius"])
            if self.__is_border is not None:
                pygame.draw.rect(self.__surface, self.__theme["border"]["color"]["disable"],
                                 (0, 0, self._width, self._height), self.__theme["border"]["width"],
                                 border_radius=self.__theme["radius"])
            self.__text_surface.blit(self.__disable_text, (self.__text_surface_width / 2 - self.__tw, self.__text_surface_height / 2 - self.__th))
        elif self.__pressed:
            pygame.draw.rect(self.__surface, self.__theme["color"]["pressed"], (0, 0, self._width, self._height),
                             border_radius=self.__theme["radius"])
            if self.__is_border is not None:
                pygame.draw.rect(self.__surface, self.__theme["border"]["color"]["pressed"],
                                 (0, 0, self._width, self._height), self.__theme["border"]["width"],
                                 border_radius=self.__theme["radius"])
            self.__text_surface.blit(self.__press_text, (self.__text_surface_width / 2 - self.__tw, self.__text_surface_height / 2 - self.__th))
        elif not self.__hover:
            pygame.draw.rect(self.__surface, self.__theme["color"]["normal"], (0, 0, self._width, self._height),
                             border_radius=self.__theme["radius"])
            if self.__is_border is not None:
                pygame.draw.rect(self.__surface, self.__theme["border"]["color"]["normal"],
                                 (0, 0, self._width, self._height), self.__theme["border"]["width"],
                                 border_radius=self.__theme["radius"])
            self.__text_surface.blit(self.__normal_text, (self.__text_surface_width / 2 - self.__tw, self.__text_surface_height / 2 - self.__th))
        elif self.__hover:
            pygame.draw.rect(self.__surface, self.__theme["color"]["hover"], (0, 0, self._width, self._height),
                             border_radius=self.__theme["radius"])
            if self.__is_border is not None:
                pygame.draw.rect(self.__surface, self.__theme["border"]["color"]["hover"],
                                 (0, 0, self._width, self._height), self.__theme["border"]["width"],
                                 border_radius=self.__theme["radius"])
            self.__text_surface.blit(self.__hover_text, (self.__text_surface_width / 2 - self.__tw, self.__text_surface_height / 2 - self.__th))

        self.__surface.blit(self.__text_surface, (self.__padding_lr, self.__padding_tb))
        sc.blit(self.__surface, (self.x, self.y))

    @property
    def click(self):
        return self.__click

    @property
    def hover(self):
        return self.__hover

    @property
    def pressed(self):
        return self.__pressed

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

    def set_arguments(self, *args, **kwargs):
        self.__args = args
        self.__kwargs = kwargs

    def set_disable(self, value: bool):
        self.__disable = value

    def __re_text(self):
        self.__normal_text = self.__font.render(self.__text, self.__theme["text"]["antialias"],
                                                self.__theme["text"]["color"]["normal"])
        self.__hover_text = self.__font.render(self.__text, self.__theme["text"]["antialias"],
                                               self.__theme["text"]["color"]["hover"])
        self.__press_text = self.__font.render(self.__text, self.__theme["text"]["antialias"],
                                               self.__theme["text"]["color"]["pressed"])
        self.__disable_text = self.__font.render(self.__text, self.__theme["text"]["antialias"],
                                                 self.__theme["text"]["color"]["disable"])
        self.__tw, self.__th = self.__font.size(self.__text)
        self.__tw = self.__tw / 2
        self.__th = self.__th / 2
