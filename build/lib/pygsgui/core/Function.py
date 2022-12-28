class FunctionManager:
    def __init__(self):
        self.__func_stack = []

    def push(self, func, args, kwargs):
        obj = [func, args, kwargs]
        self.__func_stack.append(obj)

    def update(self):
        for obj in self.__func_stack:
            obj[0](*obj[1], **obj[2])

        self.__func_stack = []
