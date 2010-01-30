import itertools

import pygame

from sprite import SpriteWorld
from shit import Shit
import data
import globals as g

class Pigeon(SpriteWorld):

    def __init__(self, world, location, key, dive_path, return_path):
        SpriteWorld.__init__(self, world=world, location=location, filename='pigeon_fly.jpg')
        self._key = key
        self._dive_path = dive_path # predetermined path (later - generated?)
        self._return_path = return_path
        self._target = g.unit_pos_to_screen_pos(*g.config.car_start_position)
        flap_steps = 3
        d = flap_delay_steps = 2
        flap_sprite = data.get_sprite('pigeon_flap.png')
        a, b = flap_sprite, self._sprite
        self._flap_sprites = sum([[(a, d), (b, d)] for i in xrange(flap_steps)], []) + [(self._sprite, 0)]

    def defecate(self):
        self.general_shoot(projectile_class=Shit, location=self._rect.midbottom, target=self._target)

    def isdiving(self):
        return self._state == 'diving'

    def is_unprotected_from_hit(self):
        return self.isdiving() # TODO - check if out of perch

    def start_dive(self):
        self._state = 'diving'
        self._action = itertools.chain(
            self.do_path(self._dive_path),
            self.do_f(self.defecate),
            self.do_path(self._return_path))

    def diversion_flap(self):
        self._state = 'diversion_flap'
        self._action = self.do_animate(self._flap_sprites)

    # die
    def onhit(self, dest):
        from crosshair import Bullet
        if dest.__class__ == Bullet and self.is_unprotected_from_hit():
            self.killed(dest)

