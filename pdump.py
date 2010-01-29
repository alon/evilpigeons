#!/usr/bin/python
import sys

import pygame
from pygame.locals import *

from pigeon import Pigeon
import globals as g
import mathutil

# Constants
black = 0, 0, 0
white = 255, 255, 255

pigeons_data = []
for (x, y), key, in [
    ( (0.1, 0.4), pygame.K_1 ),
    ( (0.1, 0.8), pygame.K_2 ),
    ( (0.9, 0.8), pygame.K_3 ),
    ( (0.9, 0.4), pygame.K_4 )
    ]:
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
        for i in reversed(removed):
            del self._sprites[i]

    def blit(self, screen):
        for s in self._sprites:
            screen.blit(s._sprite, s._rect)

# Build game parts
world = World([])
pigeons = [Pigeon(world=world, **d) for d in pigeons_data]
pcontroller = PigeonController(pigeons)
keymap = dict([(p._key, lambda i=i: pcontroller.try_dive(i)) for i, p in enumerate(pigeons)])
def quit():
    print "Quitting.."
    sys.exit()
keymap[pygame.K_ESCAPE] = quit
for p in pigeons:
    world.add_sprite(p)

def main(argv):
    screen = pygame.display.set_mode(g.size)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == KEYDOWN:
                keymap.get(event.key, lambda: None)()
            elif event.type == MOUSEBUTTONDOWN:
                # TODO
                print "mouse down"
            elif event.type == MOUSEBUTTONUP:
                print "mouse up"

        # Draw
        screen.fill(white)
        world.simulate()
        world.blit(screen)
        #print ' | '.join([str(p._action) for p in pigeons])
        pygame.display.flip()

        # FPS for lamers
        #pygame.time.delay(g.dt)
        clock.tick(g.fps)


if __name__ == '__main__':
    main(sys.argv)

