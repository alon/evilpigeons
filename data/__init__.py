"""
central place to load any data, does some caching
"""

import os

import pygame

sprites = {}
def get_sprite(filename):
    global sprites
    path = filename
    if filename not in sprites:
        if not os.path.exists(path):
            path = os.path.join('data', 'images', filename)
        sprites[filename] = pygame.image.load(path)
        print "loaded %s from %s" % (sprites[filename], path)
    return sprites[filename]
