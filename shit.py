import itertools

import pygame

from sprite import Projectile
from mathutil import interpolate

class Shit(Projectile):
    def __init__(self, location, target):
        super(Shit, self).__init__(location=location, target=target, filename='shit.png')

