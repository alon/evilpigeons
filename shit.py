import itertools
import random

import pygame

from sprite import Projectile
from mathutil import interpolate
from car import Car
import data
import globals as g

class Shit(Projectile):

    def __init__(self, location, target):
        super(Shit, self).__init__(location=location, target=target, filename='shit_flying.png', eternal=True) # end_sound=g.sounds['shit_splat'])

    def onhit(self, dest):
        if dest.__class__ != Car: return
        # stop sound, continue current path for 3 iterations and then move on
        g.sounds['shit_splat'].play()
        new_sprite = data.get_sprite('shit_on_car.png')
        self.onhit = self.null_onhit
        def set_orig():
            self.set_sprite(new_sprite)
            self._orig_sprite = new_sprite
        print "BRRRR"
        rest_of_path = self._active_path[self._active_i:random.choice(range(self._active_i, len(self._active_path)))]
        self._action = self.do_end(self.do_path_with_size(rest_of_path), end=set_orig)
            

    def null_onhit(self, dest):
        pass
