# Copyright Evil Pegions team Global Game Jam 2010:
#  Simon Reisman
#  Omer Nainudel
#  Ori Cohen
#  Alon Levy
#
# This code is licensed under the Creative Commons License. For further details,
# see the LICENSE

import sys
import os

import pygame

from sprite import Sprite

argv = sys.argv # to be program options..

################################################################################
# Simple Global Constants

dt = 50 # milliseconds. Time per frame. Determines movement per frame of pigeons, shit.
fps = int(1000.0 / dt)
#size = width, height = 640, 480 # screen size
size = width, height = 1024, 768 # screen size
sprite_design_size = sprite_width, sprite_height = 1024, 768
assert(width*sprite_height == height*sprite_width) # make sure aspect ratio is the same, avoid floating point for fun
sprite_load_zoom = 1 if sprite_width == width else float(width) / sprite_width
#size = width, height = 320, 240 # screen size

# mechanics
pigeon_steps_per_half_path = 24
steps_to_shoot = 10 # time after shot ended until next shot can be fired

# game points
car_hits_to_kill = 5
start_car_value = 5000
assert(start_car_value % car_hits_to_kill == 0)
car_value_reduction = start_car_value / car_hits_to_kill

# colors
black = 0, 0, 0
white = 255, 255, 255
yellow = 255, 255, 0

sounds = {}
def load_sounds():
    global sounds
    import pygame
    for key, filename in [
            ('shot', '44MAG.wav'),
            ('pigeon_hit', 'pigeon_hit.wav'),
            ('shit_splat', 'shit_splat.wav'),
            ('pigeon_background', 'pigeon_background.wav'),
            ('pigeon_flap', 'pigeon_flap.wav')
            ]:
        filepath = os.path.join('sound', filename)
        if not os.path.exists(filepath):
            print "Missing sound file %s" % filepath
            sys.exit(-1)
        sounds[key] = pygame.mixer.Sound(filepath)
        print '%s - %s seconds' % (key, sounds[key].get_length())

################################################################################
# keyboard (can customize for different devices)
pigeon_flight_keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0]
editing_keys = 'qwertyuiop'
quit_key = pygame.K_ESCAPE

################################################################################
# Utilities

def screen_pos_to_unit_pos(x, y):
    return float(x) / width, float(y) / height

def unit_pos_to_screen_pos(x, y):
    return int(x * width), int(y * height)

################################################################################
# Updatable configuration (when using --setpos)

PIGEONS_PATH_KEY_POINTS = 'pigeons_path_key_points'
CAR_START_POSITION = 'car_start_position'
BROOM_POSITION = 'broom_position'

try:
    import json
    json_loads = json.loads
except:
    if '--setpos' in argv:
        print "WARNING: no json - you won't be able to save config.param"
    print "using eval instead of json.loads"
    def json_loads(s):
        return eval(s)

class Config(object):

    FILENAME = 'config.json'
    DEFAULT = {PIGEONS_PATH_KEY_POINTS : [[(0.1, 0.1), (0.5, 0.5)],
        [(0.3, 0.1), (0.5, 0.5)],
        [(0.7, 0.1), (0.5, 0.5)],
        [(0.9, 0.1), (0.5, 0.5)]],
        CAR_START_POSITION : (0.5, 0.8),
        BROOM_POSITION : (0.9, 0.9)
        }

    def __init__(self):
        # Initial data - pigeons location, target (car) location, anything
        existing_data = None
        try:
            existing_data = json_loads(open(self.FILENAME).read())
            assert(set(existing_data.keys()) == set(self.DEFAULT.keys()))
        except (IOError, ValueError, AssertionError), e:
            print "missing / corrupt json file: %s" % e
            if existing_data:
                # just update added fields
                for key in self.DEFAULT.keys():
                    if not key in existing_data:
                        print "adding field %s" % key
                        existing_data[key] = self.DEFAULT[key]
                self._data = existing_data
            else:
                self._data = self.DEFAULT
            self.save()
        self._data = json_loads(open(self.FILENAME).read())

    def save(self):
        fd = open(self.FILENAME, 'w+')
        print "dumping %r" % self._data
        json.dump(self._data, fd)
        fd.close()

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value
        return self._data

    # Easy accessors
    def get_car_start_position(self):
        return self[CAR_START_POSITION]

    def get_pigeons_path_key_points(self):
        return self[PIGEONS_PATH_KEY_POINTS]

    def get_broom_position(self):
        return self[BROOM_POSITION]

    car_start_position = property(get_car_start_position)
    pigeons_path_key_points = property(get_pigeons_path_key_points)
    broom_position = property(get_broom_position)

config = Config()

class PosRecorder(object):

    def __init__(self, world):
        self.num = 0
        self._world = world
        self._pigeons_path_key_points = config[PIGEONS_PATH_KEY_POINTS]
        self._car = config[CAR_START_POSITION]
        self._path_sprites = [
            [Sprite(location=unit_pos_to_screen_pos(*point), filename='ball.png') for point in path]
                for path in self._pigeons_path_key_points]
        for pigeon_path_sprites in self._path_sprites:
            for sprite in pigeon_path_sprites:
                world.add_sprite(sprite)
        self._path_nums = [0]*len(self._pigeons_path_key_points)

    def reset_bird_path(self, num):
        print "reset path of %s (removing %s sprites)" % (num, len(self._path_sprites[num]))
        self._path_nums[num] = 0
        for sprite in self._path_sprites[num]:
            sprite.killed(None)
        self._path_sprites[num] = []

    def set_bird_pos(self, num):
        current_path = self._pigeons_path_key_points[num]
        print "bird %s: current points %s" % (num, len(current_path))
        screen_pos = pygame.mouse.get_pos()
        unit_pos = screen_pos_to_unit_pos(*screen_pos)
        current_path.append(unit_pos)
        self._path_sprites[num].append(Sprite(location=screen_pos, filename='ball.png'))
        self._world.add_sprite(self._path_sprites[num][-1])
        print "bird %s path is %s" % (num, self._pigeons_path_key_points[num])

    def set_car_pos(self):
        pos = pygame.mouse.get_pos()
        self._car = screen_pos_to_unit_pos(pos[0], pos[1])
        print "updating car position to %s" % (str(self._car))

    def record_poses(self):
        print "Recording pigeons_start_positions.json"
        config[PIGEONS_PATH_KEY_POINTS] = self._pigeons_path_key_points
        config[CAR_START_POSITION] = self._car
        config.save()


