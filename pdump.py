# Copyright Evil Pegions team Global Game Jam 2010:
#  Simon Reisman
#  Near Privman
#  Benny?
#  Flash Guy
#  Ori #2
#  Ori
#  Alon Levy

import sys
from collections import defaultdict
import json

import pygame
from pygame.locals import *

from pigeon import Pigeon
from sprite import Sprite
from crosshair import Crosshair
import globals as g
import mathutil

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
PIGEONS_START_POSITIONS_JSON = 'pigeons_start_positions.json'
pigeons_start_positions = json.load(open(PIGEONS_START_POSITIONS_JSON))
for i, (x, y) in enumerate(pigeons_start_positions):
    key = num_to_numkey(i)
    to_int = lambda points: [(int(_x*g.width), int(_y*g.height)) for _x, _y in points]
    dive_path = to_int(mathutil.path(n=10, points=[(x, y), (0.5, 0.3)]))
    return_path = to_int(mathutil.path(n=10, points=[(0.3, 0.5), (x, y)]))
    pigeons_data.append(dict(location=(int(x*g.width), int(y*g.height)), key=key,
                             dive_path=dive_path, return_path=return_path))

# Init pygame
pygame.init()
pygame.display.set_caption('Evil Pigeons')
pygame.mouse.set_visible(0)
clock = pygame.time.Clock()

class PigeonController(object):

    def __init__(self, pigeons):
        self._n = len(pigeons)
        self._pigeons = pigeons

    def try_dive(self, i):
        # only one can dive at a time
        if any([p.isdiving() for p in self._pigeons]):
            return
        self._pigeons[i].start_dive()

class World(object):

    def __init__(self, sprites):
        self._sprites = sprites

    def add_sprite(self, sprite):
        self._sprites.append(sprite)



    def simulate(self):
        removed = []
        for i, s in enumerate(self._sprites):
            if s.simulate() == 'killme':
                removed.append(i)
        # Check for collision, kill collided stuff
        # O(n^2)..
        for i_src in xrange(len(self._sprites)):
            for i_dest in xrange(i_src, len(self._sprites)):
                src, dest = self._sprites[i_src], self._sprites[i_dest]
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

class KeyMap(object):

    def __init__(self):
        self._map = defaultdict(list)

    def add(self, key, func, mod = 0):
        self._map[key].append((mod, func))

    def onkey(self, key, mod):
        if key in self._map:
            for f_mod, func in self._map[key]:
                if not mod or (mod & f_mod):
                    return func() # takes the first
        return None

# Build game parts
keymap = KeyMap()
world = World([])
pigeons = [Pigeon(world=world, **d) for d in pigeons_data]
pcontroller = PigeonController(pigeons)
for i, p in enumerate(pigeons):
    keymap.add(p._key, lambda i=i: pcontroller.try_dive(i))

class BirdPosRecorder(object):
    def __init__(self):
        self.num = 0
        self._positions = pigeons_start_positions

    def set_bird_pos(self, num):
        pos = pygame.mouse.get_pos()
        self._positions[num] = float(pos[0]) / g.width, float(pos[1]) / g.height
        pigeons[num].set_pos(*pos)
        print "setting bird %s to pos %s (%s)" % (num, pos, self._positions[num])

    def record_poses(self):
        print "Recording pigeons_start_positions.json"
        fd = open(PIGEONS_START_POSITIONS_JSON, 'w+')
        json.dump(self._positions, fd)

if '--setpos' in sys.argv:
    print "Use Ctrl-<Num> to set pigeon position to mouse position"

    bird_pos_recorder = BirdPosRecorder()
    for i in xrange(len(pigeons)):
        keymap.add(num_to_numkey(i), lambda i=i: bird_pos_recorder.set_bird_pos(i), pygame.KMOD_CTRL)
    keymap.add(ord('r'), bird_pos_recorder.record_poses)

def quit():
    print "Quitting.."
    sys.exit()
keymap.add(pygame.K_ESCAPE, quit, 2**32 - 1) # windows has mod == 4096, linux has mod == 0. 2**32 - 1 should catch all
for p in pigeons:
    world.add_sprite(p)

def main(argv):
    screen = pygame.display.set_mode(g.size)
    background = pygame.image.load('background.jpg')
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

