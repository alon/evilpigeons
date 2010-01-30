import itertools

import pygame

from sprite import Projectile
from mathutil import interpolate
import globals as g

class Shit(Projectile):
    def __init__(self, location, target):
        super(Shit, self).__init__(location=location, target=target, filename='shit.png') # end_sound=g.sounds['shit_splat'])

    def onhit(self, dest):
        g.sounds['shit_splat'].play()
        self.onhit = self.null_onhit

    def null_onhit(self, dest):
        pass
