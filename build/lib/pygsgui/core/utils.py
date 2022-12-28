import pygame


def get_font_height(ui_manager, theme, size):
    theme = ui_manager.theme[theme]
    font = None
    if theme["text"]["font"]["is_sys"]:
        font = pygame.font.SysFont(theme["text"]["font"]["name"], size,
                                          theme["text"]["bold"],
                                          theme["text"]["italic"])
        font.set_underline(theme["text"]["underline"])
    else:
        font = pygame.font.Font(theme["text"]["font"]["name"], size)
        font.set_bold(theme["text"]["bold"])
        font.set_italic(theme["text"]["italic"])
        font.set_underline(theme["text"]["underline"])

    return font.get_height()
