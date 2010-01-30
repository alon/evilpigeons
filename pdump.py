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

from pigeon import PigeonController
from sprite import Sprite
from crosshair import Crosshair
import globals as g
from keymap import KeyMap
from world import World
import mathutil
import data

def quit():
    print "Quitting.."
    sys.exit()

def main(argv):
    # Init pygame
    pygame.init()
    pygame.display.set_caption('Evil Pigeons')
    pygame.mouse.set_visible(0)
    clock = pygame.time.Clock()

    # Build game parts
    keymap = KeyMap()
    keymap.add(pygame.K_ESCAPE, quit) # windows has mod == 4096, linux has mod == 0
    keymap.add(pygame.K_ESCAPE, quit, mod=4096) # windows has mod == 4096, linux has mod == 0
    world = World(keymap=keymap)
    if '--setpos' in g.argv:
        print "Use Ctrl-<Num> to set pigeon position to mouse position"

    print "E-V-I-L Pigeons"
    print
    print "keys:"
    print keymap

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

