import pygame
from overrides import overrides
from pygsgui.core.FriendMethod import FriendMethod
from pygsgui.elements.ISGUIBasicObject import ISGUIBasicObject
from pygsgui.core.UIManager import UIManager


class CheckBox(ISGUIBasicObject):
    ID = 0

    def __init__(self, x: int, y: int, size: int, value, ui_manager: UIManager,
                 text="check box", text_size=10, window=None, tag=None,
                 auto_push=True, update_flag="ONLY_SCREEN"):
        super().__init__(x, y, size, size)
        self.ui_manager = ui_manager
        self.window = window
        self.update_flag = update_flag
        self.__theme = None
        self.tag = tag
        self._id = "check_box_" + str(CheckBox.ID)
        CheckBox.ID += 1

        self.__disable = False

        self.__value = value

        # load theme from ui manager
        if self.tag is None:
            self.__theme = self.ui_manager.theme["CheckBox"]
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

        self.__normal_text = self.__font.render(self.__text, self.__theme["text"]["antialias"],
                                                self.__theme["text"]["color"]["normal"])
        self.__hover_text = self.__font.render(self.__text, self.__theme["text"]["antialias"],
                                               self.__theme["text"]["color"]["hover"])
        self.__press_text = self.__font.render(self.__text, self.__theme["text"]["antialias"],
                                               self.__theme["text"]["color"]["pressed"])
        self.__disable_text = self.__font.render(self.__text, self.__theme["text"]["antialias"],
                                                 self.__theme["text"]["color"]["disable"])
        self.__tw, self.__th = self.__font.size(text)
        self.__tw = self.__tw / 2
        self.__th = self.__th / 2

        # surface
        self.__surface = pygame.Surface((self._width + self.__tw * 2 + self.__text_size, max(self._height, int(self.__th * 2))), pygame.SRCALPHA)

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
        self.__padding = self.__theme["padding"]

        self.__checked = False

        # checked shape
        self.normal_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.lines(self.normal_surf, self.__theme["check_shape"]["normal"], False,
                          [[10, 50], [50, 90], [90, 10]], 20)
        self.normal_surf = pygame.transform.smoothscale(self.normal_surf, (self._width - 1, self._height - 1))

        self.hover_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.lines(self.hover_surf, self.__theme["check_shape"]["hover"], False,
                          [[10, 50], [50, 90], [90, 10]], 20)
        self.hover_surf = pygame.transform.smoothscale(self.hover_surf, (self._width - 1, self._height - 1))

        self.pressed_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.lines(self.pressed_surf, self.__theme["check_shape"]["pressed"], False,
                          [[10, 50], [50, 90], [90, 10]], 20)
        self.pressed_surf = pygame.transform.smoothscale(self.pressed_surf, (self._width - 1, self._height - 1))

        self.disable_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.lines(self.disable_surf, self.__theme["check_shape"]["disable"], False,
                          [[10, 50], [50, 90], [90, 10]], 20)
        self.disable_surf = pygame.transform.smoothscale(self.disable_surf, (self._width - 1, self._height - 1))

    def __draw_check_shape(self, status: str):
        if status == "normal":
            self.__surface.blit(self.normal_surf, (0, 0))
        elif status == "hover":
            self.__surface.blit(self.hover_surf, (0, 0))
        elif status == "pressed":
            self.__surface.blit(self.pressed_surf, (0, 0))
        elif status == "disable":
            self.__surface.blit(self.disable_surf, (0, 0))

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
    def hover_reset(self):
        self.__hover = False

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
                            self.__checked = not self.__checked
                        else:
                            self.__pressed = False

            if self.__pressed:
                return True

    @overrides
    def render(self, sc: pygame.Surface):
        if not self.window:
            sc = self.ui_manager.sc
        self.__surface.fill("#00000000")
        if self.__checked:
            if self.__disable:
                pygame.draw.rect(self.__surface, self.__theme["color"]["checked"]["disable"], (0, 0, self._width, self._height),
                                 border_radius=self.__theme["radius"])
                self.__draw_check_shape("disable")
                if self.__is_border is not None:
                    pygame.draw.rect(self.__surface, self.__theme["border"]["color"]["checked"]["disable"],
                                     (0, 0, self._width, self._height), self.__theme["border"]["width"],
                                     border_radius=self.__theme["radius"])

                self.__surface.blit(self.__disable_text, (self._width + self.__padding, self._height / 2 - self.__th))
            elif self.__pressed:
                pygame.draw.rect(self.__surface, self.__theme["color"]["checked"]["pressed"], (0, 0, self._width, self._height),
                                 border_radius=self.__theme["radius"])
                self.__draw_check_shape("pressed")
                if self.__is_border is not None:
                    pygame.draw.rect(self.__surface, self.__theme["border"]["color"]["checked"]["pressed"],
                                     (0, 0, self._width, self._height), self.__theme["border"]["width"],
                                     border_radius=self.__theme["radius"])

                self.__surface.blit(self.__press_text, (self._width + self.__padding, self._height / 2 - self.__th))
            elif not self.__hover:
                pygame.draw.rect(self.__surface, self.__theme["color"]["checked"]["normal"], (0, 0, self._width, self._height),
                                 border_radius=self.__theme["radius"])
                self.__draw_check_shape("normal")
                if self.__is_border is not None:
                    pygame.draw.rect(self.__surface, self.__theme["border"]["color"]["checked"]["normal"],
                                     (0, 0, self._width, self._height), self.__theme["border"]["width"],
                                     border_radius=self.__theme["radius"])

                self.__surface.blit(self.__normal_text, (self._width + self.__padding, self._height / 2 - self.__th))
            elif self.__hover:
                pygame.draw.rect(self.__surface, self.__theme["color"]["checked"]["hover"], (0, 0, self._width, self._height),
                                 border_radius=self.__theme["radius"])
                self.__draw_check_shape("hover")
                if self.__is_border is not None:
                    pygame.draw.rect(self.__surface, self.__theme["border"]["color"]["checked"]["hover"],
                                     (0, 0, self._width, self._height), self.__theme["border"]["width"],
                                     border_radius=self.__theme["radius"])

                self.__surface.blit(self.__hover_text, (self._width + self.__padding, self._height / 2 - self.__th))
        else:
            if self.__disable:
                pygame.draw.rect(self.__surface, self.__theme["color"]["unchecked"]["disable"], (0, 0, self._width, self._height),
                                 border_radius=self.__theme["radius"])
                if self.__is_border is not None:
                    pygame.draw.rect(self.__surface, self.__theme["border"]["color"]["unchecked"]["disable"],
                                     (0, 0, self._width, self._height), self.__theme["border"]["width"],
                                     border_radius=self.__theme["radius"])
                self.__surface.blit(self.__disable_text, (self._width + self.__padding, self._height / 2 - self.__th))
            elif self.__pressed:
                pygame.draw.rect(self.__surface, self.__theme["color"]["unchecked"]["pressed"], (0, 0, self._width, self._height),
                                 border_radius=self.__theme["radius"])
                if self.__is_border is not None:
                    pygame.draw.rect(self.__surface, self.__theme["border"]["color"]["unchecked"]["pressed"],
                                     (0, 0, self._width, self._height), self.__theme["border"]["width"],
                                     border_radius=self.__theme["radius"])
                self.__surface.blit(self.__press_text, (self._width + self.__padding, self._height / 2 - self.__th))
            elif not self.__hover:
                pygame.draw.rect(self.__surface, self.__theme["color"]["unchecked"]["normal"], (0, 0, self._width, self._height),
                                 border_radius=self.__theme["radius"])
                if self.__is_border is not None:
                    pygame.draw.rect(self.__surface, self.__theme["border"]["color"]["unchecked"]["normal"],
                                     (0, 0, self._width, self._height), self.__theme["border"]["width"],
                                     border_radius=self.__theme["radius"])
                self.__surface.blit(self.__normal_text, (self._width + self.__padding, self._height / 2 - self.__th))
            elif self.__hover:
                pygame.draw.rect(self.__surface, self.__theme["color"]["unchecked"]["hover"], (0, 0, self._width, self._height),
                                 border_radius=self.__theme["radius"])
                if self.__is_border is not None:
                    pygame.draw.rect(self.__surface, self.__theme["border"]["color"]["unchecked"]["hover"],
                                     (0, 0, self._width, self._height), self.__theme["border"]["width"],
                                     border_radius=self.__theme["radius"])
                self.__surface.blit(self.__hover_text, (self._width + self.__padding, self._height / 2 - self.__th))
        sc.blit(self.__surface, (self.x, self.y))

    def get(self):
        if self.__checked:
            return self.__value
        else:
            return

    @property
    def checked(self):
        return self.__checked

    @checked.setter
    def checked(self, value: bool):
        self.__checked = value

    def set_disable(self, value: bool):
        self.__disable = value
