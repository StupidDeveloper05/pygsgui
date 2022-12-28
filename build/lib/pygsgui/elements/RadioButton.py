import pygame
import math
from overrides import overrides
from pygsgui.core.FriendMethod import FriendMethod
from pygsgui.elements.ISGUIBasicObject import ISGUIBasicObject
from pygsgui.core.UIManager import UIManager


class RadioGroup:
    ID = 0

    def __init__(self, ui_manager: UIManager, window=None):
        self.__id = "rad_group_" + str(RadioGroup.ID)
        RadioGroup.ID += 1
        self.__focused_ui = None
        self.__container = {}
        self.__ids = []

        self.ui_manager = ui_manager
        self.window = window

        if self.window is None:
            self.ui_manager.push(self, self.__id)
        else:
            self.window.push(self, self.__id)

        self.checked_item = None

    def push(self, obj, obj_id: str):
        self.__container[obj_id] = obj
        self.__ids.append(obj_id)

    def uncheck_without_me(self, obj_id: str):
        if self.__container[obj_id].checked:
            self.checked_item = self.__container[obj_id]
            for obj in self.__ids:
                if obj != obj_id:
                    self.__container[obj].checked = False

    def update(self):
        # ui update
        if self.__focused_ui is not None:
            if not self.__focused_ui.update():
                self.__focused_ui = None
            else:
                return True
        else:
            for obj_id in reversed(self.__ids):
                if self.__container[obj_id].update():
                    self.__focused_ui = self.__container[obj_id]
                    return True

    def render(self, sc):
        for obj in self.__container:
            self.__container[obj].render(sc)

    def hover_update(self):
        # hover update
        for obj_id in reversed(self.__ids):
            if self.__container[obj_id].hover_update():
                for k in self.__ids:
                    if k != obj_id:
                        self.__container[k].hover_reset()
                break

    def hover_reset(self):
        return

    def get(self):
        if self.checked_item is not None:
            return self.checked_item.get()


class RadioButton(ISGUIBasicObject):
    ID = 0

    def __init__(self, x: int, y: int, size: int, value, ui_manager: UIManager,
                 text="radio button", text_size=10, group=None, window=None, tag=None,
                 auto_push=True, update_flag="ONLY_SCREEN"):
        super().__init__(x, y, size, size)
        self.ui_manager = ui_manager
        self.window = window
        self.update_flag = update_flag
        self.group = group
        self.__theme = None
        self.tag = tag
        self._id = "radio_" + str(RadioButton.ID)
        RadioButton.ID += 1

        self.__disable = False

        self.__value = value

        # load theme from ui manager
        if self.tag is None:
            self.__theme = self.ui_manager.theme["Radio"]
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
        self.__surface = pygame.Surface((self._width * 2 + self.__tw * 2 + self.__text_size, max(self._height * 2, int(self.__th * 2))),
                                        pygame.SRCALPHA)

        # click values
        self.__click = False
        self.__hover = False
        self.__pressed = False

        # push ui manager
        if auto_push:
            if self.group is not None:
                self.group.push(self, self._id)
            else:
                if self.window is None:
                    self.ui_manager.push(self, self._id)
                else:
                    self.window.push(self, self._id)

        self.__is_border = self.__theme.get("border")
        self.__padding = self.__theme["padding"]

        self.__checked = False

        # checked shape
        self.normal_surf = pygame.Surface((99, 99), pygame.SRCALPHA)
        pygame.draw.circle(self.normal_surf, self.__theme["check_shape"]["normal"], (50, 50), 30)
        self.normal_surf = pygame.transform.smoothscale(self.normal_surf, (self._width * 2, self._height * 2))

        self.hover_surf = pygame.Surface((99, 99), pygame.SRCALPHA)
        pygame.draw.circle(self.hover_surf, self.__theme["check_shape"]["hover"], (50, 50), 30)
        self.hover_surf = pygame.transform.smoothscale(self.hover_surf, (self._width * 2, self._height * 2))

        self.pressed_surf = pygame.Surface((99, 99), pygame.SRCALPHA)
        pygame.draw.circle(self.pressed_surf, self.__theme["check_shape"]["pressed"], (50, 50), 30)
        self.pressed_surf = pygame.transform.smoothscale(self.pressed_surf, (self._width * 2, self._height * 2))

        self.disable_surf = pygame.Surface((99, 99), pygame.SRCALPHA)
        pygame.draw.circle(self.disable_surf, self.__theme["check_shape"]["disable"], (50, 50), 30)
        self.disable_surf = pygame.transform.smoothscale(self.disable_surf, (self._width * 2, self._height * 2))

    def __draw_check_shape(self, status: str):
        if status == "normal":
            self.__surface.blit(self.normal_surf, (0, 0))
        elif status == "hover":
            self.__surface.blit(self.hover_surf, (0, 0))
        elif status == "pressed":
            self.__surface.blit(self.pressed_surf, (0, 0))
        elif status == "disable":
            self.__surface.blit(self.disable_surf, (0, 0))

    def __get_dist(self, start, end):
        return math.sqrt((abs(start[0] - end[0]) ** 2) + (abs(start[1] - end[1]) ** 2))

    @FriendMethod("pygsgui.UIManager", "pygsgui.elements.Window")
    def hover_update(self):
        mx, my = self.ui_manager.event_manager.MOUSE_POS
        if self.window is not None:
            mx, my = self.window.get_relative_pos(mx, my, flag=self.update_flag)
        if self.__get_dist((self.x + self._width, self.y + self._height), (mx, my)) < self._width:
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
                    if self.__get_dist((self.x + self._width, self.y + self._height), (mx, my)) < self._width:
                        self.__pressed = True
                elif self.ui_manager.event_manager.MOUSEUP:
                    if self.__pressed:
                        if self.__get_dist((self.x + self._width, self.y + self._height), (mx, my)) < self._width:
                            self.__pressed = False
                            self.__click = True
                            self.__checked = not self.__checked
                            if self.group is not None:
                                self.group.uncheck_without_me(self._id)
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
                pygame.draw.circle(self.__surface, self.__theme["color"]["checked"]["disable"],
                                   (self._width, self._height), self._width)
                if self.__is_border is not None:
                    pygame.draw.circle(self.__surface, self.__theme["border"]["color"]["checked"]["disable"],
                                       (self._width, self._height), self._width, self.__theme["border"]["width"])
                self.__draw_check_shape("disable")
                self.__surface.blit(self.__disable_text, (self._width * 2 + self.__padding, self._height - self.__th))
            elif self.__pressed:
                pygame.draw.circle(self.__surface, self.__theme["color"]["checked"]["pressed"],
                                   (self._width, self._height), self._width)
                if self.__is_border is not None:
                    pygame.draw.circle(self.__surface, self.__theme["border"]["color"]["checked"]["pressed"],
                                       (self._width, self._height), self._width, self.__theme["border"]["width"])
                self.__draw_check_shape("pressed")
                self.__surface.blit(self.__press_text, (self._width * 2 + self.__padding, self._height - self.__th))
            elif not self.__hover:
                pygame.draw.circle(self.__surface, self.__theme["color"]["checked"]["normal"],
                                   (self._width, self._height), self._width)
                if self.__is_border is not None:
                    pygame.draw.circle(self.__surface, self.__theme["border"]["color"]["checked"]["normal"],
                                       (self._width, self._height), self._width, self.__theme["border"]["width"])
                self.__draw_check_shape("normal")
                self.__surface.blit(self.__normal_text, (self._width * 2 + self.__padding, self._height - self.__th))
            elif self.__hover:
                pygame.draw.circle(self.__surface, self.__theme["color"]["checked"]["hover"],
                                   (self._width, self._height), self._width)
                if self.__is_border is not None:
                    pygame.draw.circle(self.__surface, self.__theme["border"]["color"]["checked"]["hover"],
                                       (self._width, self._height), self._width, self.__theme["border"]["width"])
                self.__draw_check_shape("hover")
                self.__surface.blit(self.__hover_text, (self._width * 2 + self.__padding, self._height - self.__th))
        else:
            if self.__disable:
                pygame.draw.circle(self.__surface, self.__theme["color"]["unchecked"]["disable"],
                                   (self._width, self._height), self._width)
                if self.__is_border is not None:
                    pygame.draw.circle(self.__surface, self.__theme["border"]["color"]["unchecked"]["disable"],
                                       (self._width, self._height), self._width, self.__theme["border"]["width"])
                self.__surface.blit(self.__disable_text, (self._width * 2 + self.__padding, self._height - self.__th))
            elif self.__pressed:
                pygame.draw.circle(self.__surface, self.__theme["color"]["unchecked"]["pressed"],
                                   (self._width, self._height), self._width)
                if self.__is_border is not None:
                    pygame.draw.circle(self.__surface, self.__theme["border"]["color"]["unchecked"]["pressed"],
                                       (self._width, self._height), self._width, self.__theme["border"]["width"])
                self.__surface.blit(self.__press_text, (self._width * 2 + self.__padding, self._height - self.__th))
            elif not self.__hover:
                pygame.draw.circle(self.__surface, self.__theme["color"]["unchecked"]["normal"],
                                   (self._width, self._height), self._width)
                if self.__is_border is not None:
                    pygame.draw.circle(self.__surface, self.__theme["border"]["color"]["unchecked"]["normal"],
                                       (self._width, self._height), self._width, self.__theme["border"]["width"])
                self.__surface.blit(self.__normal_text, (self._width * 2 + self.__padding, self._height - self.__th))
            elif self.__hover:
                pygame.draw.circle(self.__surface, self.__theme["color"]["unchecked"]["hover"],
                                   (self._width, self._height), self._width)
                if self.__is_border is not None:
                    pygame.draw.circle(self.__surface, self.__theme["border"]["color"]["unchecked"]["hover"],
                                       (self._width, self._height), self._width, self.__theme["border"]["width"])
                self.__surface.blit(self.__hover_text, (self._width * 2 + self.__padding, self._height - self.__th))
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
        if self.__checked and self.group is not None:
            self.group.uncheck_without_me(self._id)

    def set_disable(self, value: bool):
        self.__disable = value
