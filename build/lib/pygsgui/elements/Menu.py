import pygame
from pygsgui.core.UIManager import UIManager
from pygsgui.core.FriendMethod import FriendMethod
from pygsgui.core.ShortCut import generate_shortcut


class MenuButton:
    def __init__(self, text: str, menu, function=None, shortcut=None):
        self.text = text
        self.function = function
        self.menu = menu
        self.x, self.y = 0, 0
        self.__disable = False
        self.__shortcut = shortcut

        # hover
        self.__hover = False
        self.__pressed = False

        # text
        self.__text_instance_normal = self.menu.tool_bar.font.render(self.text, self.menu.tool_bar.theme["text"]["antialias"],
                                                                self.menu.tool_bar.theme["text"]["color"]["normal"])
        self.__text_instance_disable = self.menu.tool_bar.font.render(self.text, self.menu.tool_bar.theme["text"]["antialias"],
                                                                 self.menu.tool_bar.theme["text"]["color"]["disable"])
        self.__tw, self.__th = self.menu.tool_bar.font.size(self.text)[0], self.menu.tool_bar.font.get_height()

        # shortcut text
        if self.__shortcut is not None:
            self.__shortcut_instance_normal = self.menu.tool_bar.font.render(self.__shortcut,
                                                                         self.menu.tool_bar.theme["text"]["antialias"],
                                                                         self.menu.tool_bar.theme["text"]["color"][
                                                                             "normal"])
            self.__shortcut_instance_disable = self.menu.tool_bar.font.render(self.__shortcut,
                                                                          self.menu.tool_bar.theme["text"]["antialias"],
                                                                          self.menu.tool_bar.theme["text"]["color"][
                                                                              "disable"])
            self.__sc_tw = self.menu.tool_bar.font.size(self.__shortcut)[0]
            self.__shortcut_surface = pygame.Surface((self.__sc_tw, self.__th), pygame.SRCALPHA)

        # padding
        self.padding_tb, self.padding_lr = self.menu.padding_tb, self.menu.padding_lr

        # text surface
        self.height = self.__th + self.padding_tb * 2
        self.__surface = pygame.Surface((self.__tw, self.__th), pygame.SRCALPHA)

        # sub menu
        self.unhover = False
        self.press_switch = False

    def hover_update(self):
        if not self.disable and self.menu.show and not self.menu.super.stop_update:
            mx, my = self.menu.ui_manager.event_manager.MOUSE_POS
            x, y = 0, 0
            if self.menu.flag is None:
                x, y = self.menu.relative_coord(0,0)
                # 알맞은 위치로 좌표를 옮김
                if x + self.menu.menu_width > self.menu.ui_manager.width:
                    x -= self.menu.menu_width - self.menu.width
                if y + self.menu.menu_height > self.menu.ui_manager.height:
                    y -= self.menu.menu_height + self.height
            elif self.menu.flag == "SUBMENU":
                x, y = self.menu.parent.rendering_pos
                x += self.menu.parent.menu_width
                y += self.menu.y
                # 알맞은 위치로 좌표를 옮김
                if x + self.menu.menu_width > self.menu.ui_manager.width:
                    x -= self.menu.menu_width + self.menu.parent.menu_width
                if y + self.menu.menu_height > self.menu.ui_manager.height:
                    y -= self.menu.menu_height - self.menu.parent.height
            # 실질적인 호버 업데이트
            if x + self.x < mx < x + self.x + self.menu.menu_width and y + self.y < my < y + self.y + self.height:
                self.press_switch = True
                self.__hover = True
                if not self.menu.only_check_hover:
                    self.menu.focused_obj = self
                return True
            else:
                if self.__hover:
                    self.unhover = True
                else:
                    self.unhover = False
                self.press_switch = False
                self.__hover = False
                return False

    def update(self):
        if not self.disable:
            if self.menu.ui_manager.event_manager.MOUSEDOWN:
                if self.__hover:
                    self.__pressed = True

            if self.menu.ui_manager.event_manager.MOUSEUP:
                if self.__hover and self.__pressed:
                    self.__pressed = False
                    self.menu.super.set_all_child_show(False)
                    self.menu.super.set_all_child_obj(None)
                    self.menu.super.free_all_child_focused_obj()
                    self.menu.super.free_all_child_pressed()
                    self.menu.tool_bar.obj = None
                    self.menu.tool_bar.focused_menu = None
                    self.menu.tool_bar.child_active = False
                    if self.function is not None:
                        self.menu.ui_manager.function_manager.push(self.call, (), {})

    def call(self, *args, **kwargs):
        if not self.disable:
            self.function(*args, **kwargs)

    def render(self, sc):
        self.__surface.fill("#00000000")
        if self.__shortcut is not None:
            self.__shortcut_surface.fill("#00000000")
        if self.__hover:
            pygame.draw.rect(sc, self.menu.theme["color"]["pressed"],
                             (self.x, self.y + self.padding_tb, self.menu.menu_width, self.__th + self.padding_tb * 2),
                             border_radius=self.menu.theme["radius"])
        else:
            pygame.draw.rect(sc, self.menu.tool_bar.bg_theme["normal"],
                             (self.x, self.y + self.padding_tb, self.menu.menu_width, self.__th + self.padding_tb * 2),
                             border_radius=self.menu.theme["radius"])

        if not self.disable:
            self.__surface.blit(self.__text_instance_normal, (0, 0))
            if self.__shortcut is not None:
                self.__shortcut_surface.blit(self.__shortcut_instance_normal, (0, 0))
        else:
            self.__surface.blit(self.__text_instance_disable, (0, 0))
            if self.__shortcut is not None:
                self.__shortcut_surface.blit(self.__shortcut_instance_disable, (0, 0))

        sc.blit(self.__surface, (self.x + self.padding_lr + self.menu.tool_bar_border_width, self.y + self.padding_tb))
        if self.__shortcut is not None:
            sc.blit(self.__shortcut_surface, (self.x + self.menu.menu_width - self.padding_lr - self.__sc_tw - self.menu.tool_bar_border_width, self.y + self.padding_tb))

    @property
    def pressed(self):
        return self.__hover

    @pressed.setter
    def pressed(self, value):
        self.__hover = value

    @property
    def hover(self):
        return self.__hover

    @property
    def disable(self):
        return self.__disable

    @disable.setter
    def disable(self, value):
        self.__disable = value


class Separator:
    def __init__(self, menu):
        self.menu = menu
        self.padding_tb = self.menu.padding_tb
        self.height = self.menu.tool_bar_border_width
        self.y = 0

    def render(self, sc):
        pygame.draw.line(sc, self.menu.tool_bar.theme["border"]["color"], (0, self.y + self.height / 2), (self.menu.menu_width, self.y + self.height / 2),
                         self.menu.tool_bar_border_width)


class Menu:
    ID = 0

    def __init__(self, text, tool_bar, ui_manager: UIManager, minimum_spacing=50, tag=None, flag=None, parent=None):
        self.ui_manager = ui_manager
        self.tag = tag
        self.tool_bar = tool_bar
        self.__theme = None
        self.__flag = flag
        self._id = "menu_" + str(Menu.ID)
        Menu.ID += 1

        # load theme from ui manager
        if self.tag is None:
            self.__theme = self.ui_manager.theme["Menu"]
        else:
            self.__theme = self.ui_manager.theme[self.tag]

        # create text instance
        self.__text = text
        self.__text_instance_normal = self.tool_bar.font.render(self.__text, self.tool_bar.theme["text"]["antialias"], self.tool_bar.theme["text"]["color"]["normal"])
        self.__text_instance_disable = self.tool_bar.font.render(self.__text, self.tool_bar.theme["text"]["antialias"], self.tool_bar.theme["text"]["color"]["disable"])
        self.__tw, self.__th = self.tool_bar.font.size(self.__text)[0], self.tool_bar.font.get_height()
        self.padding_tb, self.padding_lr = self.tool_bar.padding

        # surface
        self.__width, self.__height = self.padding_lr * 2 + self.__tw, self.padding_tb * 2 + self.__th
        self.__x, self.__y = 0, 0
        self.__surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # menus
        self.__menus = []

        # click value
        self.__hover = False
        self.__pressed = False

        # disable enable
        self.disable = True

        # push
        if flag is None:
            self.tool_bar.add_menu(self)

        # menu surface
        self.minimum_spacing = minimum_spacing
        self.menu_width = minimum_spacing
        self.__border_width = self.tool_bar.theme["border"]["width"]
        self.__menu_surface = pygame.Surface((self.menu_width + self.__border_width * 2, 0), pygame.SRCALPHA)
        self.__round_surface = pygame.Surface((self.menu_width + self.__border_width * 2, 0), pygame.SRCALPHA)

        # menu switch
        self.press_switch = False
        self.unhover = False
        # 자식 메뉴를 보여 줄지 말지를 결정함.
        self.__show = False

        # parent
        self.__parent = parent
        # 최상위 부모 오브젝트
        self.__super = None
        if self.__flag is None:
            self.__super = self
        else:
            self.__super = self.__parent.super

        # 더이상 호버링 업데이트 루프를 돌지 않도록 하기 위함.
        self.stop_update = False
        # 마지막으로 눌린 오브젝트
        self.__obj = None
        # 현재 포커싱 중인 자식 오브젝트
        self.__focused_obj = None
        # 호버 업데이트를 돌릴때 오직 호버링만 체크하기위한 플래스
        self.only_check_hover = False
        # 메뉴가 랜더링 되는 포지션
        self.__rendering_pos = [0, 0]

        # ===== 서브 메뉴 화살표 =====
        self.__arrow_height = self.__th - self.padding_tb * 8
        self.__arrow_width = 60 / (100 / self.__arrow_height)
        self.__arrow_surf_normal = pygame.Surface((60, 100), pygame.SRCALPHA)
        self.__arrow_surf_normal.fill("#00000000")
        pygame.draw.line(self.__arrow_surf_normal, self.tool_bar.theme["text"]["color"]["normal"], [0, 0], [50, 50], 30)
        pygame.draw.line(self.__arrow_surf_normal, self.tool_bar.theme["text"]["color"]["normal"], [0, 100], [50, 50], 30)
        self.__arrow_surf_normal = pygame.transform.smoothscale(self.__arrow_surf_normal, (self.__arrow_width, self.__arrow_height))

        self.__arrow_surf_disable = pygame.Surface((60, 100), pygame.SRCALPHA)
        self.__arrow_surf_disable.fill("#00000000")
        pygame.draw.line(self.__arrow_surf_disable, self.tool_bar.theme["text"]["color"]["disable"], [0, 0], [50, 50], 30)
        pygame.draw.line(self.__arrow_surf_disable, self.tool_bar.theme["text"]["color"]["disable"], [0, 100], [50, 50], 30)
        self.__arrow_surf_disable = pygame.transform.smoothscale(self.__arrow_surf_disable, (self.__arrow_width, self.__arrow_height))

    def draw_arrow(self, sc):
        if self.disable:
            sc.blit(self.__arrow_surf_disable, (self.__parent.menu_width - self.__arrow_width - self.padding_lr - self.tool_bar_border_width, self.y + self.padding_tb + self.height / 2 - self.__arrow_height / 2))
        else:
            sc.blit(self.__arrow_surf_normal, (self.__parent.menu_width - self.__arrow_width - self.padding_lr - self.tool_bar_border_width, self.y + self.padding_tb + self.height / 2 - self.__arrow_height / 2))

    # 서브 메뉴를 위한 좌표
    def relative_coord(self, x, y):
        if self.__parent is None:
            return self.tool_bar.window.x + self.tool_bar.window.theme["border"]["width"] + self.x + x, self.tool_bar.window.y + self.tool_bar.window.theme["title_bar"]["height"] + self.tool_bar.window.theme["border"]["width"] + self.height + y
        else:
            return self.__parent.relative_coord(x + self.x + self.__parent.menu_width, y + self.y)

    def add_button(self, text, function=None, shortcut=None):
        # 단축키 값을 가공함
        gen_shortcut = None
        if shortcut is not None:
            gen_shortcut = generate_shortcut(shortcut)
        
        # 메뉴 버튼을 생성
        menu = MenuButton(text, self, function=function, shortcut=gen_shortcut)
        if len(self.__menus) == 0:
            menu.y = self.padding_tb + self.tool_bar_border_width
        else:
            menu.y = self.__menus[-1].y + self.__menus[-1].height + self.padding_tb * 2
        self.__menus.append(menu)
        
        # 메뉴 패널의 크기를 재설정
        height = self.padding_tb * 2
        for i in self.__menus:
            height += i.height + self.padding_tb * 2
        shortcut_length = 0
        if shortcut is not None:
            shortcut_length = self.tool_bar.font.size(gen_shortcut)[0]
        menu_width = self.tool_bar.font.size(text)[0] + shortcut_length + self.minimum_spacing + self.padding_lr * 2 + self.__border_width * 2
        if menu_width > self.menu_width:
            self.menu_width = menu_width
        self.__menu_surface = pygame.Surface((self.menu_width, height + self.tool_bar_border_width * 2), pygame.SRCALPHA)
        self.__round_surface = pygame.Surface((self.menu_width, height + self.tool_bar_border_width * 2), pygame.SRCALPHA)

        # add shortcut
        if shortcut is not None and function is not None:
            if self.tool_bar.window is not None:
                self.ui_manager.shortcut_manager.add_shortcut(shortcut, self.tool_bar.window.handle, menu.call)
            else:
                self.ui_manager.shortcut_manager.add_shortcut(shortcut, "Main", menu.call)

    def add_child(self, text: str):
        instance = Menu(text, self.tool_bar, self.ui_manager, flag="SUBMENU", parent=self)
        instance.width = self.menu_width
        instance.disable = False
        if len(self.__menus) == 0:
            instance.y = self.padding_tb + self.tool_bar_border_width
        else:
            instance.y = self.__menus[-1].y + self.__menus[-1].height + self.padding_tb * 2
        self.__menus.append(instance)

        # 메뉴 패널의 크기를 재설정
        height = self.padding_tb * 2
        for i in self.__menus:
            height += i.height + self.padding_tb * 2
        menu_width = self.tool_bar.font.size(text)[0] + self.minimum_spacing + self.padding_lr * 2 + self.__border_width * 2
        if menu_width > self.menu_width:
            self.menu_width = menu_width
        self.__menu_surface = pygame.Surface((self.menu_width, height + self.__border_width * 2), pygame.SRCALPHA)
        self.__round_surface = pygame.Surface((self.menu_width, height + self.__border_width * 2), pygame.SRCALPHA)

        return instance

    def add_separator(self):
        sep = Separator(self)
        if len(self.__menus) == 0:
            sep.y = self.tool_bar_border_width
        else:
            sep.y = self.__menus[-1].y + self.__menus[-1].height + self.padding_tb * 2
        height = self.padding_tb * 2 + self.tool_bar_border_width
        for i in self.__menus:
            height += i.height + self.padding_tb * 2
        self.__menus.append(sep)
        self.__menu_surface = pygame.Surface((self.menu_width, height), pygame.SRCALPHA)
        self.__round_surface = pygame.Surface((self.menu_width, height), pygame.SRCALPHA)

    @FriendMethod("pygsgui.elements.ToolBar")
    def hover_update(self):
        if not self.disable:
            # ============ 자식 메뉴들에 대한 업데이트를 돌릴지 결정하는 구간 입니다. ===============
            go = True
            if self.parent is not None:
                if self.parent.only_check_hover:
                    go = False
            if go:
                if self.focused_obj:
                    stop = False
                    if type(self.focused_obj) == Menu:
                        hover_result = self.focused_obj.hover_update()
                        is_hover = self.focused_obj.is_hover()
                        stop = hover_result or is_hover
                    else:
                        stop = self.focused_obj.hover_update()
            # ===============================================================================
                    if not stop:
                        if type(self.focused_obj) == Menu:
                            self.only_check_hover = True
                            for child in self.__menus:
                                if child == self.focused_obj or type(child) == Separator:
                                    continue
                                child.hover_update()
                                if child.hover:
                                    self.set_all_child_obj(None)
                                    self.set_all_child_show(False)
                                    self.free_all_child_focused_obj()
                                    self.free_all_child_pressed()
                                    self.focused_obj = child
                                    self.super.stop_update = True
                                    break
                            self.only_check_hover = False
                        else:
                            self.only_check_hover = True
                            no_changed = True
                            for child in self.__menus:
                                if child == self.focused_obj or type(child) == Separator:
                                    continue
                                child.hover_update()
                                if child.hover:
                                    #self.free_all_child_pressed()
                                    self.focused_obj = child
                                    self.super.stop_update = True
                                    no_changed = False
                                    break
                            if no_changed:
                                self.focused_obj = None
                            self.only_check_hover = False
                else:
                    for child in self.__menus:
                        if type(child) == Separator:
                            continue
                        child.hover_update()

            mx, my = self.ui_manager.event_manager.MOUSE_POS
            if self.__flag is None:
                if self.stop_update:
                    self.stop_update = False
                if self.tool_bar.window is not None:
                    mx, my = self.tool_bar.window.get_relative_pos(mx, my, flag="TOOL_BAR")
                else:
                    my += self.tool_bar.height

                width = self.x + self.width
                if self.tool_bar.window is not None:
                    width = min(width, self.tool_bar.window.get_real_size()[0])

                # child active 조건에 맞게 활성화함.
                child_active = False
                if self.tool_bar.focused_menu is not None:
                    if self.tool_bar.focused_menu == self:
                        child_active = True
                    elif self.tool_bar.focused_menu_is_hover is False:
                        child_active = True
                else:
                    child_active = True

                # 호버 업데이트
                if self.x < mx < width and self.y < my < self.y + self.height:
                    if self.tool_bar.child_active and child_active:
                        self.press_switch = True
                        self.__pressed = True
                    self.__hover = True
                else:
                    if self.tool_bar.child_active and child_active:
                        if self.__hover:
                            self.unhover = True
                        else:
                            self.unhover = False
                        self.press_switch = False
                        self.__pressed = False
                    self.__hover = False

            # 서브 메뉴에 대한 업데이트
            elif self.__flag == "SUBMENU" and self.__parent.show and not self.super.stop_update:
                x, y = self.__parent.rendering_pos
                y += self.y
                # 실질적인 호버 업데이트
                if x < mx < x + self.__parent.menu_width and y < my < y + self.height:
                    if not self.__parent.only_check_hover:
                        self.press_switch = True
                        self.__pressed = True
                        if self.__parent.focused_obj is None:
                            self.__parent.focused_obj = self
                    self.__hover = True
                    return True
                else:
                    if not self.__parent.only_check_hover:
                        if self.__hover:
                            self.unhover = True
                        else:
                            self.unhover = False
                        self.press_switch = False
                        self.__pressed = False
                    self.__hover = False
                    return False

    def update(self):
        if not self.disable:
            #print(self.show, self.text)
            if self.__pressed:
                for child in self.__menus:
                    if type(child) == Separator or type(child) == Menu:
                        continue
                    child.update()

                # 마지막으로 눌린 것
                set_last_press = True
                for child in self.__menus:
                    if type(child) == Separator:
                        continue
                    if child.unhover:
                        self.__obj = child
                    if child.press_switch:
                        set_last_press = False
                        break
                if set_last_press and type(self.__obj) == Menu:
                    self.__obj.pressed = True
                for child in self.__menus:
                    if type(child) != Menu:
                        continue
                    child.update()

            else:
                self.__show = False

            if self.tool_bar.obj != self.super:
                self.set_all_child_obj(None)
            if self.ui_manager.event_manager.MOUSEDOWN:
                do_update = False
                if self.tool_bar.focused_menu is not None:
                    if self.tool_bar.focused_menu == self:
                        do_update = True
                else:
                    do_update = True
                if self.__flag is None and do_update:
                    if self.__hover and not self.__pressed:
                        self.__pressed = True
                    elif self.__pressed and not self.is_hover():
                        self.set_all_child_obj(None)
                        self.free_all_child_focused_obj()
                        self.set_all_child_show(False)
                        self.free_all_child_pressed()
                        self.tool_bar.child_active = False
                        self.tool_bar.focused_menu = None
                        self.tool_bar.obj = None

    def render(self, sc):
        self.__surface.fill("#FFFFFF00")
        status = "normal"
        if self.tool_bar.disable:
            status = "disable"
        if self.__flag is None:
            if self.__pressed:
                pygame.draw.rect(self.__surface, self.__theme["color"]["pressed"], (0, 0, self.width, self.height),
                                 border_radius=self.__theme["radius"])
            elif not self.__hover:
                pygame.draw.rect(self.__surface, self.tool_bar.bg_theme[status], (0, 0, self.width, self.height),
                                 border_radius=self.__theme["radius"])
            elif self.__hover:
                pygame.draw.rect(self.__surface, self.__theme["color"]["hover"], (0, 0, self.width, self.height),
                                 border_radius=self.__theme["radius"])
            if not self.disable:
                self.__surface.blit(self.__text_instance_normal,
                                    (self.width / 2 - self.__tw / 2, self.height / 2 - self.__th / 2))
            else:
                self.__surface.blit(self.__text_instance_disable,
                                    (self.width / 2 - self.__tw / 2, self.height / 2 - self.__th / 2))
            sc.blit(self.__surface, (self.x, self.y))
        # 서브 메뉴에 대한 드로잉
        elif self.__flag == "SUBMENU":
            if self.__pressed:
                pygame.draw.rect(sc, self.__theme["color"]["pressed"], (0, self.y + self.padding_tb, self.__parent.menu_width, self.height),
                                 border_radius=self.__theme["radius"])
            elif not self.__hover:
                pygame.draw.rect(sc, self.tool_bar.bg_theme[status], (0, self.y + self.padding_tb, self.__parent.menu_width, self.height),
                                 border_radius=self.__theme["radius"])
            if not self.disable:
                self.__surface.blit(self.__text_instance_normal, (self.padding_lr, self.padding_tb))
            else:
                self.__surface.blit(self.__text_instance_disable, (self.padding_lr, self.padding_tb))
            self.draw_arrow(sc)
            sc.blit(self.__surface, (self.x + self.tool_bar_border_width, self.y))

    @FriendMethod("pygsgui.elements.ToolBar")
    def child_render(self, sc):
        if self.__pressed:
            self.__show_child(sc)

    def __show_child(self, sc):
        self.__show = True
        if self.__flag is None:
            if len(self.__menus) > 0:
                x, y = self.tool_bar.window.x + self.x + self.tool_bar.window.theme["border"]["width"], self.tool_bar.window.y + self.tool_bar.window.theme["title_bar"]["height"] + self.height + self.tool_bar.window.theme["border"]["width"]
                # 알맞은 위치로 좌표를 옮김
                if x + self.menu_width > self.ui_manager.width:
                    x -= self.menu_width - self.width
                if y + self.menu_height > self.ui_manager.height:
                    y -= self.menu_height + self.height
                self.__rendering_pos = x, y
                self.__round_surface.fill("#00000000")
                pygame.draw.rect(self.__round_surface, "#FFFFFF", (0, 0, self.menu_width, self.__menu_surface.get_height()), border_radius=self.theme["radius"])
                self.__menu_surface.fill(self.tool_bar.bg_theme["normal"])
                for child in self.__menus:
                    child.render(self.__menu_surface)
                pygame.draw.rect(self.__menu_surface, self.tool_bar.theme["border"]["color"],
                                 (0, 0, self.__menu_surface.get_width(), self.__menu_surface.get_height()),
                                 self.tool_bar.theme["border"]["width"], border_radius=self.theme["radius"])
                self.__round_surface.blit(self.__menu_surface, (0, 0), None, pygame.BLEND_RGBA_MIN)
                sc.blit(self.__round_surface, (x, y))
                for child in self.__menus:
                    if type(child) == Menu:
                        child.child_render(sc)

        elif self.__flag == "SUBMENU":
            if len(self.__menus) > 0:
                x, y = self.__decide_coord()
                self.__round_surface.fill("#00000000")
                pygame.draw.rect(self.__round_surface, "#FFFFFF", (0, 0, self.menu_width, self.__menu_surface.get_height()), border_radius=self.theme["radius"])
                self.__menu_surface.fill(self.tool_bar.bg_theme["normal"])
                for child in self.__menus:
                    child.render(self.__menu_surface)
                pygame.draw.rect(self.__menu_surface, self.tool_bar.theme["border"]["color"],
                                 (0, 0, self.__menu_surface.get_width(), self.__menu_surface.get_height()),
                                 self.tool_bar.theme["border"]["width"], border_radius=self.theme["radius"])
                self.__round_surface.blit(self.__menu_surface, (0, 0), None, pygame.BLEND_RGBA_MIN)
                sc.blit(self.__round_surface, (x, y))
                for child in self.__menus:
                    if type(child) == Menu:
                        child.child_render(sc)

    def is_hover(self):
        if self.__show and not self.disable:
            if self.tool_bar.window is not None:
                mx, my = self.ui_manager.event_manager.MOUSE_POS
                x, y = 0, 0
                if self.__flag is None:
                    x, y = self.relative_coord(0, 0)
                    x -= self.tool_bar.theme["border"]["width"]
                    # 알맞은 위치로 좌표를 옮김
                    if x + self.menu_width > self.ui_manager.width:
                        x -= self.menu_width - self.width
                    if y + self.menu_height > self.ui_manager.height:
                        y -= self.menu_height + self.height
                elif self.__flag == "SUBMENU":
                    x, y = self.__decide_coord()
                if x < mx < x + self.menu_width and y < my < y + self.__menu_surface.get_height():
                    return True
                else:
                    if type(self.focused_obj) == Menu:
                        return self.focused_obj.is_hover()
                    else:
                        return False

    # 메뉴 패널의 요소가 눌렸는지
    def get_pressed(self):
        if self.__show and not self.disable:
            if self.ui_manager.event_manager.MOUSEDOWN:
                if self.is_hover():
                    return True
                else:
                    return False

    def __decide_coord(self):
        x, y = self.__parent.rendering_pos
        y += self.y
        # 알맞은 위치로 좌표를 옮김
        if x + self.menu_width + self.__parent.menu_width > self.ui_manager.width:
            x -= self.menu_width
        else:
            x += self.__parent.menu_width
        if y + self.__menu_surface.get_height() > self.ui_manager.height:
            y -= self.__menu_surface.get_height() - self.height

        self.__rendering_pos = x, y
        return x, y

    # 툴바의 메뉴가 눌렸는지
    @property
    def pressed(self):
        return self.__pressed

    @pressed.setter
    def pressed(self, value: bool):
        if self.__parent is not None:
            self.__parent.pressed = value
        self.__pressed = value

    def free_all_child_pressed(self):
        for child in self.__menus:
            if type(child) == Menu:
                child.free_all_child_pressed()
            elif type(child) == MenuButton:
                child.pressed = False
                child.unhover = False
        self.__pressed = False
        self.__hover = False
        self.unhover = False

    @property
    def menu_height(self):
        return self.__menu_surface.get_height()

    @property
    def theme(self):
        return self.__theme

    @property
    def width(self):
        return self.__width

    @width.setter
    def width(self, value: int):
        self.__width = value

    @property
    def height(self):
        return self.__height

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):
        self.__x = value

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, value):
        self.__y = value

    def set_all_child_obj(self, value):
        for m in self.__menus:
            if type(m) == Menu:
                m.set_all_child_obj(value)
        self.__obj = value

    @property
    def rendering_pos(self):
        return self.__rendering_pos

    @property
    def flag(self):
        return self.__flag

    @property
    def parent(self):
        return self.__parent

    @property
    def hover(self):
        return self.__hover

    @property
    def super(self):
        return self.__super

    @property
    def show(self):
        return self.__show

    def set_all_child_show(self, value):
        for child in self.__menus:
            if type(child) == Menu:
                child.set_all_child_show(value)
        self.__show = value

    @property
    def focused_obj(self):
        return self.__focused_obj

    @focused_obj.setter
    def focused_obj(self, value):
        self.__focused_obj = value

    @property
    def tool_bar_border_width(self):
        return self.__border_width

    def free_all_child_focused_obj(self):
        for child in self.__menus:
            if type(child) == Menu:
                child.free_all_child_focused_obj()
        self.focused_obj = None

    def get_child_by_index(self, index):
        return self.__menus[index]
