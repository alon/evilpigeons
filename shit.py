import itertools

import pygame

from sprite import Sprite
from mathutil import interpolate

class Shit(Sprite):
    def __init__(self, location, target):
        Sprite.__init__(self, location)
        self._target = target
        self._shit_path = interpolate(10, self._start_location, self._target)
        self._action = itertools.chain(
            self.do_path(self._shit_path),
            self.do_quit())
    
