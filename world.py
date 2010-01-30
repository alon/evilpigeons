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
        self._font = pygame.font.Font(None, 48)
        self._background_channel = g.sounds['pigeon_background']
        self._background_channel.set_volume(0.8)
        self._restart()

    def set_car_value(self, v):
        self._car_value = v

    def get_car_value(self):
        return self._car_value

    car_value = property(get_car_value, set_car_value)

    def update_car_value(self, car_value):
        print "car value = %s" % car_value
        self.car_value = car_value
        self._car_value_text = self._font.render("Car Value: %s$" % (self._car_value), 1, g.yellow)
        self._car_value_rect = self._car_value_text.get_rect(centerx=g.width*85/100, centery = g.height*9/10)

    def _restart(self):
        self.update_car_value(g.start_car_value)
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

    def start_background_sound(self):
        self._background_channel.play(-1)

    def stop_background_sound(self):
        self._background_channel.stop()

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
        for i in sorted(set(removed), reverse=True):
            try:
                del self._sprites[i]
            except:
                print "cannot delete sprite %s, have %s sprites left" % (i, len(self._sprites))

    def blit(self, screen):
        for s in self._sprites:
            if s.visible():
                screen.blit(s._sprite, s._rect)
        # show car_value
        screen.blit(self._car_value_text, self._car_value_rect)

    # End game
    def car_is_dead_long_live_the_pigeons(self):
        splash(pygame.display.get_surface(), 'pigeon_win_splash.png', min_timeout=1.0)
        self._restart()

    def pigeons_dead_long_live_the_car(self):
        splash(pygame.display.get_surface(), 'car_win_splash.png', min_timeout=1.0)
        self._restart()

