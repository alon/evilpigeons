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

def splash(screen, filename):
    print "splash %s" % filename
    help_sprite = data.get_sprite(filename)
    help_rect = help_sprite.get_rect()
    screen.blit(help_sprite, help_rect)
    pygame.display.flip()
    for key, mod in iter_key_events():
        break


