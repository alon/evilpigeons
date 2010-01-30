# Copyright Evil Pegions team Global Game Jam 2010:
#  Simon Reisman
#  Near Privman
#  Benny?
#  Omry
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
from eventhandler import EventHandler
from pygameutil import splash
import mathutil
import data

def quit():
    print "Quitting.."
    sys.exit()

def main(argv):
    # Init pygame
    pygame.init()
    if not '--window' in g.argv:
        pygame.display.set_mode((1024, 768), pygame.HWSURFACE | pygame.FULLSCREEN)
    print pygame.mixer.get_init()
    pygame.display.set_caption('Evil Pigeons')
    pygame.mouse.set_visible(0)
    g.load_sounds() # after mixer init
    clock = pygame.time.Clock()

    # Build game parts
    main_event_handler = EventHandler()
    keymap = main_event_handler._keymap
    keymap.add(pygame.K_ESCAPE, quit) # windows has mod == 4096, linux has mod == 0
    keymap.add(pygame.K_ESCAPE, quit, mod=4096) # windows has mod == 4096, linux has mod == 0
    EventHandler.active_handlers.add(main_event_handler)
    world = World()
    if '--setpos' in g.argv:
        print "Use Ctrl-<Num> to set pigeon position to mouse position"

    print "E-V-I-L Pigeons"
    print
    print "keys:"
    print keymap

    screen = pygame.display.set_mode(g.size)

    # Help screens (no menu system)
    for help_screen in ['help1.jpg', 'help2.jpg']:
        splash(screen, filename=help_screen)

    # Start game
    EventHandler.active_handlers.add(world) # overly complex..

    background = data.get_sprite('background.png')
    background_rect = background.get_rect()

    if not '--nomusic' in g.argv:
        pygame.mixer.music.load(os.path.join('data', 'music', 'background.ogg'))
        pygame.mixer.music.set_volume(0.3) # defaults to 0.99~ on linux
        pygame.mixer.music.play(-1)

    def inc_vol():
        pygame.mixer.music.set_volume(min(1.0, pygame.mixer.music.get_volume() + 0.1))
        print pygame.mixer.music.get_volume()

    def dec_vol():
        pygame.mixer.music.set_volume(max(0.0, pygame.mixer.music.get_volume() - 0.1))
        print pygame.mixer.music.get_volume()

    keymap.add(ord('['), dec_vol)
    keymap.add(ord(']'), inc_vol)

    active_handlers = EventHandler.active_handlers

    world.start_background_sound()

    while True:
        # update location of shotgun crosshair
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == KEYDOWN:
                print event.key, event.mod
                for handler in active_handlers:
                    handler.on_key_down(event.key, event.mod)
            elif event.type == MOUSEBUTTONDOWN:
                for handler in active_handlers:
                    handler.on_mouse_down()
            elif event.type == MOUSEBUTTONUP:
                pass

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

