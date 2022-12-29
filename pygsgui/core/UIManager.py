import pygame
import json
from pygsgui.core.Event import EventManager
from pygsgui.core.ShortCut import ShortCutManager
from pygsgui.core.Function import FunctionManager

import os

class UIManager:
    def __init__(self, sc: pygame.Surface):
        self.sc = sc
        self.screen = pygame.Surface(sc.get_size(), pygame.SRCALPHA)
        self.event_manager = EventManager()
        self.shortcut_manager = ShortCutManager(self)
        self.function_manager = FunctionManager()
        self.width = sc.get_width()
        self.height = sc.get_height()
        self.__focused_ui = None
        self.__ui_objects = {}
        self.__ids = []
        self.__theme = {}
        pkgPath = os.path.split(os.path.abspath(__file__))[0]
        pkgPath = os.path.abspath(os.path.join(pkgPath, os.path.pardir))
        themeLocation = os.path.join(pkgPath, "basicTheme.json")
        self.set_theme(themeLocation)

        self.set_event = False
        self.final_update = False
        self.delete = False

        self.__window_stack = []
        self.focusing_window = None
        self.next_focusing_window = None

    def set_theme(self, location: str):
        with open(location, 'r') as f:
            self.__theme = json.load(f)

    def add_window(self, window):
        self.__window_stack.append(window)

    def push(self, objects, obj_id: str):
        self.__ui_objects[obj_id] = objects
        self.__ids.append(obj_id)

    def pop(self, obj_id: str):
        try:
            del self.__ui_objects[obj_id]
            self.__ids.remove(obj_id)
        except:
            print("Key Error!!")

    def find(self, obj_id: str):
        return self.__ui_objects[obj_id]

    def update(self):
        self.function_manager.update()
        self.event_manager.update()
        self.get_current_window()

        if self.focusing_window is None:
            # ui update
            if self.__focused_ui is not None:
                if not self.__focused_ui.update():
                    self.__focused_ui.hover_reset()
                    self.__focused_ui = None

            else:
                for obj_id in reversed(self.__ids):
                    if self.__ui_objects[obj_id].update():
                        self.__focused_ui = self.__ui_objects[obj_id]
                        break

            # hover update
            if not self.final_update:
                hover = False
                for window in self.__window_stack:
                    if window.IsMouseOn() and window.visible:
                        hover = True
                        for k in self.__ids:
                            self.__ui_objects[k].hover_reset()
                        break
                if not hover:
                    for obj_id in reversed(self.__ids):
                        if self.__ui_objects[obj_id].hover_update():
                            for k in self.__ids:
                                if k != obj_id:
                                    self.__ui_objects[k].hover_reset()
                            break
            else:
                for obj_id in self.__ids:
                    self.__ui_objects[obj_id].hover_reset()

            if self.final_update:
                self.delete = True
                self.final_update = False

        else:
            self.focusing_window.update()

    def render(self):
        self.screen.fill("#00000000")
        for obj in self.__ui_objects:
            self.__ui_objects[obj].render(self.screen)

        for window in self.__window_stack:
            if window.visible:
                window.render()

        self.sc.blit(self.screen, (0, 0))

    def get_current_window(self):
        # set current window None
        if self.focusing_window is not None:
            if self.focusing_window.delete:
                self.focusing_window.active = False
                self.focusing_window.window_disable()
                self.focusing_window.delete = False
                self.focusing_window = None

        # change "focusing window" to "next focusing window"
        if self.next_focusing_window is not None and self.focusing_window is None:
            if self.set_event:
                if self.delete:
                    self.delete = False
                    self.set_event = False
                return

            self.focusing_window = self.next_focusing_window
            self.next_focusing_window = None
            self.focusing_window.active = True
            self.focusing_window.window_enable()
            self.__window_stack.remove(self.focusing_window)
            self.__window_stack.append(self.focusing_window)

        # choose next window
        if self.event_manager.MOUSEDOWN:
            if self.focusing_window is not None:
                if self.focusing_window.IsMouseOn():
                    return
                else:
                    self.focusing_window.final_update = True

            if self.focusing_window is None or self.focusing_window.final_update:
                self.next_focusing_window = None
                for window in reversed(self.__window_stack):
                    if window.delete is False and window.visible:
                        if window.IsMouseOn():
                            self.final_update = True
                            self.next_focusing_window = window
                            return

    def set_focusing(self, window):
        if window.visible:
            if self.focusing_window is None:
                self.final_update = True
                self.next_focusing_window = window
                # none window update
                self.set_event = True
            else:
                self.focusing_window.final_update = True
                self.next_focusing_window = window

    def get_current_handle(self):
        if self.focusing_window is not None:
            return self.focusing_window.handle
        else:
            return "Main"

    def is_any_focusing(self):
        if self.__focused_ui is None:
            if self.focusing_window is None:
                return True
            return False
        return False

    @property
    def theme(self):
        return self.__theme
