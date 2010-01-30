# Copyright Evil Pegions team Global Game Jam 2010:
#  Simon Reisman
#  Near Privman
#  Benny?
#  Flash Guy
#  Ori #2
#  Ori
#  Alon Levy

import os
import sys
from collections import defaultdict

import pygame
from pygame.locals import *

from pigeon import Pigeon
from sprite import Sprite
from crosshair import Crosshair
from car import Car
import globals as g
import mathutil
import data

# Constants
black = 0, 0, 0
white = 255, 255, 255

def num_to_numkey(num):
    if num > 9 or num < 0:
        raise Exception("No numkey for num %s" % num)
    return [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0][num]

pigeons_data = []

#pigeons_start_positions = [
#    (0.1, 0.4),
#    (0.1, 0.8),
#    (0.9, 0.8),
#    (0.9, 0.4)
#]
# Keys for initial
pigeons_start_positions = g.config['pigeons_start_positions']
for i, (x, y) in enumerate(pigeons_start_positions):
    key = num_to_numkey(i)
    to_int = lambda points: [(int(_x*g.width), int(_y*g.height)) for _x, _y in points]
    dive_path = to_int(mathutil.path(n=10, points=[(x, y), g.config.pigeon_dive_position]))
    return_path = to_int(mathutil.path(n=10, points=[g.config.pigeon_dive_position, (x, y)]))
    pigeons_data.append(dict(location=(int(x*g.width), int(y*g.height)), key=key,
                             dive_path=dive_path, return_path=return_path))

class PigeonController(object):

    def __init__(self, pigeons, keymap):
        self._n = len(pigeons)
        self._pigeons = pigeons
        self._setup_keymap(keymap)

    def _setup_keymap(self, keymap):
        for i, p in enumerate(self._pigeons):
            keymap.add(p._key, lambda i=i: pcontroller.try_dive(i))
            keymap.add(p._key, lambda i=i: pcontroller.try_diversion_flap(i), mod=pygame.KMOD_SHIFT)

    def try_dive(self, i):
        # only one can dive at a time
        if any([p.isdiving() for p in self._pigeons]):
            return
        self._pigeons[i].start_dive()

    def try_diversion_flap(self, i):
        p = self._pigeons[i]
        if not p.isdiving():
            p.diversion_flap()

class World(object):

    def __init__(self, sprites):
        self._sprites = sprites
        self._just_simulated = []

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
        print "EVIL RULES"

class KeyMap(object):

    IGNORE_MOD = -1

    def __init__(self):
        self._map = {}

    def add(self, key, func, mod = IGNORE_MOD):
        if key not in self._map:
            self._map[key] = [(mod, func)]
        else:
            existing = self._map[key]
            at_i = len(existing) # default - put at the end
            # keep it sorted: most strict first
            if mod == self.IGNORE_MOD:
                at_i = 0
            elif mod == 0:
                # put after IGNORE_MOD
                at_i = 0
                for i, (e_mod, e_func) in enumerate(existing):
                    if e_mod == self.IGNORE_MOD:
                        at_i = i + 1
            existing.insert(at_i, (mod, func))
        print 'key %s -> %s' % (key, self._map[key])

    def onkey(self, key, mod):
        if key in self._map:
            for f_mod, func in self._map[key]:
                if f_mod == self.IGNORE_MOD or (not mod and not f_mod) or (mod & f_mod):
                    return func() # takes the first
        return None

def quit():
    print "Quitting.."
    sys.exit()

# Init pygame
pygame.init()
pygame.display.set_caption('Evil Pigeons')
pygame.mouse.set_visible(0)
clock = pygame.time.Clock()

# Build game parts
keymap = KeyMap()
keymap.add(pygame.K_ESCAPE, quit) # windows has mod == 4096, linux has mod == 0
keymap.add(pygame.K_ESCAPE, quit, mod=4096) # windows has mod == 4096, linux has mod == 0
world = World([])
pigeons = [Pigeon(world=world, **d) for d in pigeons_data]
pcontroller = PigeonController(pigeons=pigeons, keymap=keymap)
car = Car(world)
if '--showcar' in sys.argv:
    world.add_sprite(car)
else:
    world.add_just_simulated_sprite(car)
for p in pigeons:
    world.add_sprite(p)

if '--setpos' in sys.argv:
    print "Use Ctrl-<Num> to set pigeon position to mouse position"

    pos_recorder = g.PosRecorder()
    for i in xrange(len(pigeons)):
        keymap.add(num_to_numkey(i), lambda i=i: pos_recorder.set_bird_pos(i), pygame.KMOD_CTRL)
    keymap.add(ord('c'), pos_recorder.set_car_pos)
    keymap.add(ord('r'), pos_recorder.record_poses)

def main(argv):
    screen = pygame.display.set_mode(g.size)
    background = data.get_sprite('background.jpg')
    background_rect = background.get_rect()
    crosshair = Crosshair(world)
    world.add_sprite(crosshair)

    while True:
        # update location of shotgun crosshair
        crosshair.set_pos_from_mouse_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == KEYDOWN:
                print event.key, event.mod
                keymap.onkey(event.key, event.mod)
            elif event.type == MOUSEBUTTONDOWN:
                crosshair.shoot()
            elif event.type == MOUSEBUTTONUP:
                print "mouse up"

        # Draw
        #screen.fill(white)
        screen.blit(background, background_rect)
        world.simulate()
        world.blit(screen)
        #print ' | '.join([str(p._action) for p in pigeons])
        pygame.display.flip()

        # FPS for lamers
        #pygame.time.delay(g.dt)
        clock.tick(g.fps)

