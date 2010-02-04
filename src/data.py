"""
central place to load any data, does some caching
"""

import os

import pygame

sprites = {}
def get_sprite(filename):
    # all of the sprites are prebuilt for a certain size, we need to change then to the required size
    # proportionally.

    import globals as g

    global sprites
    path = filename
    if filename not in sprites:
        if not os.path.exists(path):
            path = os.path.join('images', filename)
        sprites[filename] = pygame.image.load(path) # .convert() - supposed to bring better performance - but makes alpha disappear..
        if g.sprite_load_zoom != 1:
            # make sure it is the right size
            sprites[filename] = pygame.transform.rotozoom(sprites[filename], 0, g.sprite_load_zoom)
        print "loaded %s from %s" % (sprites[filename], path)
    return sprites[filename]

