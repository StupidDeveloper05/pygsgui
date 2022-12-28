import keyboard


def generate_shortcut(shortcut: str):
    splitted_value = shortcut.lower().replace(" ", "").split("+")
    text = ""
    for i in range(len(splitted_value)):
        text += splitted_value[i][0].upper() + splitted_value[i][1:]
        if i < len(splitted_value) - 1:
            text += "+"
    return text


class ShortCutManager:
    def __init__(self, ui_manager):
        self.ui_manager = ui_manager
        self.__short_cuts = {}

    def add_shortcut(self, short_cut: str, handle, function):
        generated_short_cut = generate_shortcut(short_cut)
        if self.__short_cuts.get(generated_short_cut) is None:
            self.__short_cuts[generated_short_cut] = {}
            keyboard.add_hotkey(generated_short_cut, self.__call_shortcut, args=(generated_short_cut,))
        self.__short_cuts[generated_short_cut][handle] = function

    def __call_shortcut(self, short_cut):
        function = self.__short_cuts[short_cut].get(self.ui_manager.get_current_handle())
        if function is not None:
            self.__short_cuts[short_cut][self.ui_manager.get_current_handle()]()
