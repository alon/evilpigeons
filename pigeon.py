import itertools

import pygame

from sprite import Sprite
from shit import Shit

import globals as g

class Pigeon(Sprite):
    def __init__(self, world, location, key, dive_path, return_path):
        Sprite.__init__(self, location)
        self._world = world
        self._key = key
        self._dive_path = dive_path # predetermined path (later - generated?)
        self._return_path = return_path
        self._target = (int(g.width*0.5), int(g.height*0.5))

    def defecate(self):
        self._world.add_sprite(Shit(location=self._rect.midbottom, target=self._target))

    def isdiving(self):
        return self._state == 'diving'

    def start_dive(self):
        self._state = 'diving'
        self._action = itertools.chain(
            self.do_path(self._dive_path),
            self.do_f(self.defecate),
            self.do_path(self._return_path))

