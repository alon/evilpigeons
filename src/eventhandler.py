from keymap import KeyMap

class EventHandler(object):

    # class list of active handlers - they will be called. Any object here can add another
    # object here. So the menu will add or remove the world as it sees fit, and the world will
    # remove itself when the game is done

    active_handlers = set()

    def __init__(self):
        self._keymap = KeyMap() # personal keymap

    def on_key_down(self, key, mod):
        self._keymap.onkey(key, mod)

    def on_mouse_down(self):
        """mouse down - reimplement me """


