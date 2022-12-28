import pygame
from PIL import Image, ImageFilter
from pygsgui.elements.Button import Button
from pygsgui.elements.Label import Label
from pygsgui.core.FriendMethod import FriendMethod
from pygsgui.core.UIManager import UIManager


class Window:
    Handle = 0

    def __init__(self, x: int, y: int, width: int, height: int, ui_manager: UIManager,
                 caption="window", resizable=False, tag=None,
                 close_button=True, tool_bar=None, visible=True):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.__handle = Window.Handle
        Window.Handle += 1
        self.__visible = visible

        self.__final_update = False
        self.__delete = False

        self.__close = False

        # window properties
        self.__caption = caption
        self.resizable = resizable
        self.close_btn = close_button
        self.__tool_bar = tool_bar

        # title bar instances
        self.close_btn_instance = None
        self.caption_instance = None

        self.minimum_size = (50, 50)

        self.ui_manager = ui_manager
        self.tag = tag

        self.theme = None

        # load theme from ui manager
        if self.tag is None:
            self.theme = self.ui_manager.theme["Window"]
        else:
            self.theme = self.ui_manager.theme[self.tag]

        self.active = False

        # surfaces
        self.__surface = pygame.Surface((self.get_real_size()), pygame.SRCALPHA)
        self.__title_surface = pygame.Surface((self.get_real_size()[0], self.theme["border"]["width"] * 2 +
                                               self.theme["title_bar"]["height"]), pygame.SRCALPHA)
        self.__temp_surface = pygame.Surface((self.get_real_size()[0], self.theme["border"]["width"] * 2 +
                                              self.theme["title_bar"]["height"]), pygame.SRCALPHA)
        self.__background = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.__ui_objects_screen = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.__tool_bar_surf = pygame.Surface((self.get_real_size()[0], 10), pygame.SRCALPHA)

        if self.__tool_bar is not None:
            self.__tool_bar_surf = pygame.Surface((self.get_real_size()[0], self.__tool_bar.height), pygame.SRCALPHA)

        # resize
        self.__resize_width = 10
        self.__resizing = False
        self.__resize_case = None

        # resize switch
        self.__can_resize_top = True
        self.__can_resize_bottom = True
        self.__can_resize_left = True
        self.__can_resize_right = True

        # blur setting
        self.__blur_window = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.__is_blur = self.theme["background"]["blur"]["active"]

        self.ui_manager.add_window(self)

        # moving window
        self.__drag_pos = (0, 0)
        self.__drag_start = False

        # objects setting
        self.__focused_ui = None
        self.__ui_objects = {}
        self.__ids = []

        # caption
        if self.close_btn:
            height = self.theme["title_bar"]["height"]
            close_tag = ""
            if self.tag is None:
                close_tag = "Window.close_button"
            else:
                close_tag = self.tag + ".close_button"
            # x좌표 resize update 에서 수정
            self.close_btn_instance = Button(self.theme["border"]["width"] + self.width - self.theme["title_bar"]["height"], self.theme["border"]["width"], height, height,
                                             text="X", text_size=10, ui_manager=self.ui_manager, window=self,
                                             auto_push=False, update_flag="ALL_SURFACE", tag=close_tag)
            self.close_btn_instance.set_disable(True)

        # title caption
        caption_height = self.theme["title_bar"]["height"]
        caption_tag = ""
        if self.tag is None:
            caption_tag = "Window.caption"
        else:
            caption_tag = self.tag + ".caption"
        self.caption_instance = Label(self.theme["border"]["width"], self.theme["border"]["width"], self.width, caption_height, text=self.__caption,
                                      ui_manager=self.ui_manager, text_size=int(self.theme["title_bar"]["height"] * 0.75), window=self,
                                      auto_push=False, update_flag="ALL_SURFACE", tag=caption_tag)

    # Optimized blurring algorithm by The New St. Paul aka MintFan
    def blur(self, sc, radius=10, alpha=255, resolution=90):
        tool_bar = 0
        if self.__tool_bar is not None:
            tool_bar = self.__tool_bar.height

        self.__blur_window.fill("#FFFFFF00")
        pygame.draw.rect(self.__blur_window, "#FFFFFF", (0, 0, self.width, self.height),
                         border_bottom_left_radius=self.theme["radius"],
                         border_bottom_right_radius=self.theme["radius"])

        resolution = resolution  # percentage of pixels to use for blur
        s = pygame.Surface((self.width, self.height))
        s.blit(sc, (0, 0), (self.x + self.theme["border"]["width"], self.y + self.theme["title_bar"]["height"] + self.theme["border"]["width"] + tool_bar, self.width, self.height))
        s = pygame.transform.rotozoom(s, 0, (resolution / 100.0) * 1)
        size2 = s.get_size()
        rad = radius
        b = pygame.image.tostring(s, "RGBA", False)
        b = Image.frombytes("RGBA", size2, b)
        b = b.filter(ImageFilter.GaussianBlur(radius=int(rad)))
        b = pygame.image.frombuffer(b.tobytes(), b.size, b.mode).convert()
        b.set_alpha(alpha)
        b = pygame.transform.rotozoom(b, 0, (100.0 / resolution) * 1)
        b = pygame.transform.scale(b, (self.width, self.height))
        self.__blur_window.blit(b, (0, 0), None, special_flags=pygame.BLEND_RGBA_MIN)

        sc.blit(self.__blur_window, (self.x + self.theme["border"]["width"], self.y + self.theme["title_bar"]["height"] + self.theme["border"]["width"] + tool_bar))

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

    def get_relative_pos(self, mx, my, flag="ONLY_SCREEN"):
        tool_bar = 0
        if self.__tool_bar is not None:
            tool_bar = self.__tool_bar.height
        if flag == "ONLY_SCREEN":
            return mx - (self.x + self.theme["border"]["width"]), \
                   my - (self.y + self.theme["border"]["width"] * 2 +
                         self.theme["title_bar"]["height"] + tool_bar)
        elif flag == "ALL_SURFACE":
            return mx - self.x, my - self.y
        elif flag == "TOOL_BAR":
            return mx - (self.x + self.theme["border"]["width"]), \
                   my - (self.y + self.theme["border"]["width"] + self.theme["title_bar"]["height"])

    def get_real_size(self):
        width = self.width + self.theme["border"]["width"] * 2
        height = self.height + self.theme["border"]["width"] * 3 + self.theme["title_bar"]["height"]
        if self.__tool_bar is not None:
            height += self.__tool_bar.height
        return width, height

    def IsMouseOn(self):
        mx, my = self.ui_manager.event_manager.MOUSE_POS
        width, height = self.get_real_size()
        if self.x - self.__resize_width < mx < self.x + width + self.__resize_width \
                and self.y - self.__resize_width < my < self.y + height + self.__resize_width:
            return True
        else:
            result = False
            if self.__tool_bar is not None:
                result = self.__tool_bar.is_hover
            return result

    def window_disable(self):
        if self.close_btn is True:
            self.close_btn_instance.set_disable(True)
        self.caption_instance.set_disable(True)
        self.__close = False
        pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)
        self.final_update = False
        if self.__tool_bar is not None:
            self.__tool_bar.disable = True

    def window_enable(self):
        if self.close_btn is True:
            self.close_btn_instance.set_disable(False)
        self.caption_instance.set_disable(False)
        pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)
        self.final_update = False
        if self.__tool_bar is not None:
            self.__tool_bar.disable = False

    def should_close(self):
        return self.__close

    def update(self):
        mx, my = self.ui_manager.event_manager.MOUSE_POS

        do_hover_update = True
        do_ui_update = True
        if self.__tool_bar is not None:
            do_hover_update, do_ui_update = self.__tool_bar.update()

        if self.resizable and do_hover_update:
            case = None
            if not self.__resizing and not self.__drag_start:
                case = self.__resize_update()
            if case is not None:
                if self.ui_manager.event_manager.MOUSEDOWN:
                    self.__resizing = True
                    self.__resize_case = case

            if self.__resizing:
                self.__resize_window(self.__resize_case)

            if self.ui_manager.event_manager.MOUSEUP:
                if self.__resizing:
                    self.__resizing = False
                    self.__resize_x, self.__resize_y = 0, 0
        else:
            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)

        drag_update = True

        if self.close_btn and do_ui_update:
            if self.close_btn_instance.update():
                drag_update = False
            else:
                drag_update = True

            self.close_btn_instance.hover_update()

            if self.close_btn_instance.click:
                self.__close = True
            else:
                self.__close = False

        # caption update
        self.caption_instance.hover_update()

        if not self.__resizing and do_hover_update:
            if drag_update:
                if self.ui_manager.event_manager.MOUSEDOWN:
                    if self.x < mx < self.x + self.width and self.y < my < self.y + self.theme["title_bar"]["height"]:
                        if not self.__drag_start:
                            self.__drag_pos = pygame.mouse.get_pos()
                        self.__drag_start = True

                elif self.ui_manager.event_manager.MOUSEUP:
                    self.__drag_start = False

                if self.__drag_start:
                    x, y = pygame.mouse.get_pos()
                    self.x += x - self.__drag_pos[0]
                    self.y += y - self.__drag_pos[1]
                    self.__drag_pos = x, y

        # object update
        if do_ui_update and not self.__resizing:
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
        if do_hover_update and not self.__resizing:
            for obj_id in reversed(self.__ids):
                if self.__ui_objects[obj_id].hover_update():
                    for k in self.__ids:
                        if k != obj_id:
                            self.__ui_objects[k].hover_reset()
                    break
        else:
            for k in self.__ids:
                self.__ui_objects[k].hover_reset()

        if self.final_update:
            self.delete = True
            self.final_update = False

    def render(self):
        sc = self.ui_manager.sc
        self.__surface.fill("#FFFFFF00")
        tool_bar = 0
        if self.__tool_bar is not None:
            tool_bar = self.__tool_bar.height

        key = "disable"
        if self.active:
            key = "normal"

        pygame.draw.rect(self.__surface, "#FFFFFF" + self.theme["background"]["transparent"],
                         (0, 0, self.get_real_size()[0], self.get_real_size()[1]),
                         border_top_left_radius=self.theme["title_bar"]["radius"],
                         border_top_right_radius=self.theme["title_bar"]["radius"],
                         border_bottom_left_radius=self.theme["radius"],
                         border_bottom_right_radius=self.theme["radius"])

        # background
        self.__background.fill(self.theme["background"][key])
        self.__surface.blit(self.__background, (self.theme["border"]["width"], self.theme["title_bar"]["height"] + self.theme["border"]["width"] * 2 + tool_bar), None, pygame.BLEND_RGBA_MIN)

        self.__ui_objects_screen.fill("#FFFFFF00")

        for obj in self.__ui_objects:
            self.__ui_objects[obj].render(self.__ui_objects_screen)

        self.__surface.blit(self.__ui_objects_screen, (self.theme["border"]["width"], self.theme["title_bar"]["height"] + self.theme["border"]["width"] * 2 + tool_bar))

        # title bar
        pygame.draw.rect(self.__surface, self.theme["title_bar"][key],
                         (0, 0, self.width + self.theme["border"]["width"] * 2,
                          self.theme["title_bar"]["height"] + self.theme["border"]["width"]),
                         border_top_left_radius=self.theme["title_bar"]["radius"],
                         border_top_right_radius=self.theme["title_bar"]["radius"])

        # caption
        self.caption_instance.render(self.__surface)

        # close button
        if self.close_btn:
            self.__title_surface.fill("#FFFFFF00")
            self.__temp_surface.fill("#FFFFFF00")
            pygame.draw.rect(self.__title_surface, "#FFFFFF",
                             (0, 0, self.__title_surface.get_width(), self.__title_surface.get_height()),
                             border_top_left_radius=self.theme["title_bar"]["radius"],
                             border_top_right_radius=self.theme["title_bar"]["radius"])

            self.close_btn_instance.render(self.__surface)
            self.__title_surface.blit(self.__temp_surface, (0, 0), None, pygame.BLEND_RGBA_MIN)
            self.__surface.blit(self.__title_surface, (0, 0))

        # title bar border
        pygame.draw.rect(self.__surface, self.theme["border"]["color"][key],
                         (0, 0, self.width + self.theme["border"]["width"] * 2,
                          self.theme["title_bar"]["height"] + self.theme["border"]["width"] * 2 + tool_bar),
                         self.theme["border"]["width"],
                         border_top_left_radius=self.theme["title_bar"]["radius"],
                         border_top_right_radius=self.theme["title_bar"]["radius"])

        # border
        pygame.draw.rect(self.__surface, self.theme["border"]["color"][key],
                         (0, self.theme["title_bar"]["height"] + tool_bar + self.theme["border"]["width"],
                          self.width + self.theme["border"]["width"] * 2,
                          self.height + self.theme["border"]["width"] * 2),
                         self.theme["border"]["width"],
                         border_bottom_left_radius=self.theme["radius"],
                         border_bottom_right_radius=self.theme["radius"])

        # blur
        if self.__is_blur:
            self.blur(sc, resolution=self.theme["background"]["blur"]["resolution"])

        # tool bar
        if self.__tool_bar is not None:
            self.__tool_bar_surf.fill("#00000000")
            self.__tool_bar.render(self.__tool_bar_surf)
            self.__surface.blit(self.__tool_bar_surf,
                                (self.theme["border"]["width"], self.theme["border"]["width"] + self.theme["title_bar"]["height"]))

        sc.blit(self.__surface, (self.x, self.y))
        if self.__tool_bar is not None:
            self.__tool_bar.child_render(sc)

    def __resize_update(self):
        mx, my = self.ui_manager.event_manager.MOUSE_POS
        width, height = self.get_real_size()
        # edge
        # top
        if self.x + self.__resize_width < mx < self.x + width - self.__resize_width and \
            self.y - self.__resize_width < my < self.y:
            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_SIZENS)
            return "top"
        # bottom
        elif self.x + self.__resize_width < mx < self.x + width - self.__resize_width and \
            self.y + height < my < self.y + height + self.__resize_width:
            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_SIZENS)
            return "bottom"
        # left
        elif self.x - self.__resize_width < mx < self.x and \
            self.y + self.__resize_width < my < self.y + height - self.__resize_width:
            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_SIZEWE)
            return "left"
        # right
        elif self.x + width < mx < self.x + width + self.__resize_width and \
            self.y + self.__resize_width < my < self.y + height - self.__resize_width:
            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_SIZEWE)
            return "right"
        # top left
        elif self.x - self.__resize_width < mx < self.x + self.__resize_width and \
            self.y - self.__resize_width < my < self.y + self.__resize_width:
            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_SIZENWSE)
            return "top left"
        # top right
        elif self.x + width < mx < self.x + width + self.__resize_width and \
            self.y - self.__resize_width < my < self.y:
            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_SIZENESW)
            return "top right"
        # bottom left
        elif self.x - self.__resize_width < mx < self.x + self.__resize_width and \
            self.y + height - self.__resize_width < my < self.y + height + self.__resize_width:
            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_SIZENESW)
            return "bottom left"
        # bottom right
        elif self.x + width - self.__resize_width < mx < self.x + width + self.__resize_width and \
                self.y + height - self.__resize_width < my < self.y + height + self.__resize_width:
            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_SIZENWSE)
            return "bottom right"
        else:
            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)
            return None

    def __resize_window(self, case: str):
        x, y = self.ui_manager.event_manager.MOUSE_REL
        mx, my = self.ui_manager.event_manager.MOUSE_POS
        width, height = self.get_real_size()
        if case == "top" or case == "top left" or case == "top right":
            if self.__can_resize_top:
                self.height -= y
                self.y += y
                if self.height < self.minimum_size[1]:
                    self.y -= self.minimum_size[1] - self.height
                    self.height = self.minimum_size[1]
                    self.__can_resize_top = False
            else:
                if self.y > my:
                    self.__can_resize_top = True
                    self.height -= (my - self.y)
                    self.y += my - self.y
        if case == "bottom" or case == "bottom left" or case == "bottom right":
            if self.__can_resize_bottom:
                self.height += y
                if self.height < self.minimum_size[1]:
                    self.height = self.minimum_size[1]
                    self.__can_resize_bottom = False
            else:
                if self.y + height < my:
                    self.__can_resize_bottom = True
                    self.height += my - (self.y + height)
        if case == "left" or case == "bottom left" or case == "top left":
            if self.__can_resize_left:
                self.width -= x
                self.x += x
                if self.width < self.minimum_size[0]:
                    self.x -= self.minimum_size[0] - self.width
                    self.width = self.minimum_size[0]
                    self.__can_resize_left = False
            else:
                if self.x > mx:
                    self.__can_resize_left = True
                    self.width -= (mx - self.x)
                    self.x += mx - self.x
        if case == "right" or case == "top right" or case == "bottom right":
            if self.__can_resize_right:
                self.width += x
                if self.width < self.minimum_size[0]:
                    self.width = self.minimum_size[0]
                    self.__can_resize_right = False
            else:
                if self.x + width < mx:
                    self.__can_resize_right = True
                    self.width += mx - (self.x + width)
        self.__resize_surface()

    def __resize_surface(self):
        self.__surface = pygame.Surface((self.get_real_size()), pygame.SRCALPHA)
        self.__title_surface = pygame.Surface((self.get_real_size()[0], self.theme["border"]["width"] * 2 +
                                               self.theme["title_bar"]["height"]), pygame.SRCALPHA)
        self.__temp_surface = pygame.Surface((self.get_real_size()[0], self.theme["border"]["width"] * 2 +
                                              self.theme["title_bar"]["height"]), pygame.SRCALPHA)
        self.__background = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.__ui_objects_screen = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.__blur_window = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        if self.__tool_bar is not None:
            self.__tool_bar_surf = pygame.Surface((self.get_real_size()[0], self.__tool_bar.height), pygame.SRCALPHA)

        # close button
        if self.close_btn:
            self.close_btn_instance.x = self.theme["border"]["width"] + self.width - self.theme["title_bar"]["height"]

        # caption
        self.caption_instance._width = self.width
        self.caption_instance.resized()

        # tool bar
        if self.__tool_bar is not None:
            self.__tool_bar.resize()

    @property
    def visible(self):
        return self.__visible

    @visible.setter
    def visible(self, value: bool):
        self.__visible = value
        if value is False:
            self.final_update = True

    @property
    def final_update(self):
        return self.__final_update

    @final_update.setter
    @FriendMethod("pygsgui.UIManager")
    def final_update(self, value):
        self.__final_update = value

    @property
    def delete(self):
        return self.__delete

    @delete.setter
    @FriendMethod("pygsgui.UIManager")
    def delete(self, value):
        self.__delete = value

    @property
    def handle(self):
        return self.__handle

    def set_tool_bar(self, obj):
        self.__tool_bar = obj
        self.__resize_surface()
        self.__tool_bar_surf = pygame.Surface((self.get_real_size()[0], self.__tool_bar.height), pygame.SRCALPHA)
