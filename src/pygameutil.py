# Copyright Evil Pegions team Global Game Jam 2010:
#  Simon Reisman
#  Omer Nainudel
#  Ori Cohen
#  Alon Levy
#
# This code is licensed under the Creative Commons License. For further details,
# see the LICENSE

import time
import pygame
from pygame.locals import *

import data

def iter_key_events():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == KEYDOWN:
                yield event.key, event.mod

def iter_all_events():
    """ all means mouse and keyboard """
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == KEYDOWN:
                yield event.key, event.mod
            elif event.type == MOUSEBUTTONDOWN:
                yield event

def splash(screen, filename, min_timeout=0.0):
    print "splash %s" % filename
    help_sprite = data.get_sprite(filename)
    help_rect = help_sprite.get_rect()
    screen.blit(help_sprite, help_rect)
    pygame.display.flip()
    start = time.time()
    for event in iter_all_events():
        if time.time() - start >= min_timeout:
            break


