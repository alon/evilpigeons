# vim: set fileencoding=UTF-8 :

import pygame

from pigeon import PigeonController
from car import Car
from crosshair import Crosshair
from eventhandler import EventHandler
from pygameutil import splash
import globals as g

class World(EventHandler):

    def __init__(self):
        super(World, self).__init__()
        self._restart()

    def _restart(self):
        self._sprites = []
        self._just_simulated = []
        self._pcontroller = PigeonController(world=self, keymap=self._keymap)
        car = Car(self)
        self._crosshair = Crosshair(self)
        self.add_sprite(self._crosshair)
        if '--showcar' in g.argv:
            self.add_sprite(car)
        else:
            self.add_just_simulated_sprite(car)
        print "keys = %s" % len(self._keymap)

    def on_mouse_down(self):
        self._crosshair.shoot()

    def add_sprite(self, sprite):
        self._sprites.append(sprite)

    def add_just_simulated_sprite(self, sprite):
        self._just_simulated.append(sprite)

    def simulated_pairs(self):
        all = self._sprites + self._just_simulated
        n = len(all)
        for i_src, src in enumerate(all):
            for i_dest in xrange(i_src + 1, n):
                dest = all[i_dest]
                yield src, dest

    def simulate(self):
        """ core interactions - simulate everything, collide everything, O(n^2) """
        removed = []
        for i, s in enumerate(self._sprites):
            if s.simulate() == 'killme':
                removed.append(i)
        # Check for collision, kill collided stuff
        for src, dest in self.simulated_pairs():
            if src._rect.colliderect(dest._rect):
                src.onhit(dest) # \
                dest.onhit(src) # / this makes it easier to implement - just define onhit where it matters
                # NOTE: it will only die in the next loop - not that bad..
        # Delete finished projectiles / pigeons
        for i in reversed(sorted(removed)):
            del self._sprites[i]

    def blit(self, screen):
        for s in self._sprites:
            screen.blit(s._sprite, s._rect)

    # End game
    def car_is_dead_long_live_the_pigeons(self):
        splash(pygame.display.get_surface(), 'pigeon_win_splash.png')
        self._restart()

    def pigeons_dead_long_live_the_car(self):
        splash(pygame.display.get_surface(), 'car_win_splash.png')
        self._restart()


