import itertools

import pygame

from sprite import SpriteWorld
from shit import Shit
import globals as g

class Pigeon(SpriteWorld):

    def __init__(self, world, location, key, dive_path, return_path):
        SpriteWorld.__init__(self, world=world, location=location, filename='pigeon_fly.jpg')
        self._key = key
        self._dive_path = dive_path # predetermined path (later - generated?)
        self._return_path = return_path
        self._target = (int(g.width*0.5), int(g.height*0.5))

    def defecate(self):
        self.general_shoot(projectile_class=Shit, location=self._rect.midbottom, target=self._target)

    def isdiving(self):
        return self._state == 'diving'

    def start_dive(self):
        self._state = 'diving'
        self._action = itertools.chain(
            self.do_path(self._dive_path),
            self.do_f(self.defecate),
            self.do_path(self._return_path))

    # die
    def onhit(self, dest):
        from crosshair import Bullet
        if dest.__class__ == Bullet:
            self.killed(dest)

