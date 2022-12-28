import pygame
from pygsgui.core.UIManager import UIManager
from pygsgui.elements.Menu import Menu
from pygsgui.core.FriendMethod import FriendMethod


class ToolBar:
    ID = 0

    def __init__(self, ui_manager: UIManager, text_size=15, window=None, tag=None):
        self.ui_manager = ui_manager
        self.window = window
        self.tag = tag
        self.text_size = text_size
        self.__bg_theme = None
        self.__theme = None
        self._id = "toolbar_" + str(ToolBar.ID)
        ToolBar.ID += 1

        # load background theme from ui manager
        if self.window is not None:
            self.__bg_theme = self.window.theme["title_bar"]

        # theme
        if self.tag is not None:
            self.__theme = self.ui_manager.theme[self.tag]
        else:
            self.__theme = self.ui_manager.theme["Tool_Bar"]

        # font
        self.__text_size = self.text_size
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

        # menu container
        self.__menus = []

        # padding
        self.__padding_tb = self.__theme["padding-tb"]
        self.__padding_lr = self.__theme["padding-lr"]

        # surface
        self.height = self.__theme["padding-tb"] * 2 + self.__font.get_height()
        if self.window is not None:
            self.surface = pygame.Surface((self.window.width, self.height))
        else:
            self.surface = pygame.Surface((self.ui_manager.width, self.height))

        # switch
        self.__disable = True
        self.__child_active = False
        self.obj = None
        self.focused_menu = None
        self.focused_menu_is_hover = None
        self.__prev_menu = None

        if self.window is not None:
            self.window.set_tool_bar(self)

        # hover
        self.is_hover = False

    def add_menu(self, menu: Menu):
        if len(self.__menus) == 0:
            menu.x = 0
        elif len(self.__menus) == 1:
            menu.x = self.__menus[-1].width
        else:
            menu.x = self.__menus[-1].x + self.__menus[-1].width
        self.__menus.append(menu)

    def update(self):
        optional_update = True
        if self.window.final_update:
            optional_update = False

        if optional_update:
            self.is_hover = False
            set_last_press = True
            no_hover = True
            no_press = True
            if self.focused_menu:
                if self.focused_menu.is_hover():
                    self.focused_menu_is_hover = True
                else:
                    self.focused_menu_is_hover = False
            else:
                self.focused_menu_is_hover = None
            for m in self.__menus:
                m.hover_update()
            if self.focused_menu is not None:
                if not self.focused_menu_is_hover:
                    self.focused_menu = None
            if self.focused_menu is None:
                for m in self.__menus:
                    if m.pressed:
                        self.focused_menu = m
                        if self.__prev_menu is not None:
                            if self.__prev_menu != self.focused_menu:
                                self.__prev_menu.set_all_child_show(False)
                                self.__prev_menu.set_all_child_obj(None)
                                self.__prev_menu.free_all_child_focused_obj()
                                self.__prev_menu.free_all_child_pressed()
                        self.__prev_menu = m
                        break
            if self.focused_menu is not None:
                self.child_active = True
            else:
                self.child_active = False
            if self.focused_menu is not None:
                if self.focused_menu_is_hover:
                    self.is_hover = True
                    no_hover = False
                if self.focused_menu.get_pressed():
                    no_press = False
            for m in self.__menus:
                if m.unhover:
                    self.obj = m
                if m.press_switch:
                    set_last_press = False
                    break
            if set_last_press and self.obj is not None:
                self.obj.pressed = True
            for m in self.__menus:
                m.update()
            return no_hover, no_press
        else:
            if self.__prev_menu is not None:
                self.__prev_menu.set_all_child_show(False)
                self.__prev_menu.set_all_child_obj(None)
                self.__prev_menu.free_all_child_focused_obj()
                self.__prev_menu.free_all_child_pressed()
            self.focused_menu = None
            self.__prev_menu = None
            self.obj = None
            return True, True

    def render(self, sc):
        status = "normal"
        if self.__disable:
            status = "disable"

        self.surface.fill(self.__bg_theme[status])

        for m in self.__menus:
            m.render(self.surface)

        sc.blit(self.surface, (0, 0))

    def child_render(self, sc):
        for m in self.__menus:
            m.child_render(sc)

    def resize(self):
        if self.window is not None:
            self.surface = pygame.Surface((self.window.width, self.height))
        else:
            self.surface = pygame.Surface((self.ui_manager.width, self.height))

    @property
    def bg_theme(self):
        return self.__bg_theme

    @property
    def theme(self):
        return self.__theme

    @property
    def font(self):
        return self.__font

    @property
    def padding(self):
        return self.__padding_tb, self.__padding_lr

    @property
    def child_active(self):
        return self.__child_active

    @child_active.setter
    @FriendMethod("pygsgui.elements.Menu")
    def child_active(self, value: bool):
        self.__child_active = value

    @property
    def disable(self):
        return self.__disable

    @disable.setter
    def disable(self, value: bool):
        if value is True:
            for m in self.__menus:
                m.disable = True
        else:
            for m in self.__menus:
                m.disable = False
        self.__disable = value
