class FriendMethod:
    def __init__(self, *friend_modules):
        self.friends_modules = friend_modules

    def __call__(self, func):
        def run(*args, **kwargs):
            return func(*args, **kwargs)
        return run
