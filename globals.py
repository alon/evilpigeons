import json
import sys

argv = sys.argv # to be program options..

################################################################################
# Simple Global Constants

dt = 50 # milliseconds. Time per frame. Determines movement per frame of pigeons, shit.
fps = int(1000.0 / dt)
size = width, height = 1024, 768 # screen size
#size = width, height = 320, 240 # screen size

# mechanics
pigeon_steps_per_half_path = 20

# game points
car_hits_to_kill = 2

# colors
black = 0, 0, 0
white = 255, 255, 255

################################################################################
# Utilities

def screen_pos_to_unit_pos(x, y):
    return float(x) / width, float(y) / height

def unit_pos_to_screen_pos(x, y):
    return int(x * width), int(y * height)

################################################################################
# Updatable configuration (when using --setpos)

PIGEONS_START_POSITIONS = 'pigeons_start_positions'
CAR_START_POSITION = 'car_start_position'
PIGEON_START_POSITION = 'pigeon_start_position'

class Config(object):

    FILENAME = 'data/config.json'
    DEFAULT = {PIGEONS_START_POSITIONS : [(0.1, 0.1), (0.3, 0.1), (0.7, 0.1), (0.9, 0.1)],
        CAR_START_POSITION : (0.5, 0.8),
        PIGEON_START_POSITION : (0.5, 0.5)}

    def __init__(self):
        # Initial data - pigeons location, target (car) location, anything
        existing_data = None
        try:
            existing_data = json.load(open(self.FILENAME))
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
        self._data = json.load(open(self.FILENAME))

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

    def get_pigeon_dive_position(self):
        return self[PIGEON_START_POSITION]

    car_start_position = property(get_car_start_position)
    pigeon_dive_position = property(get_pigeon_dive_position)

config = Config()

class PosRecorder(object):
    def __init__(self):
        self.num = 0
        self._positions = config[PIGEONS_START_POSITIONS]
        self._car = config[CAR_START_POSITION]

    def set_bird_pos(self, num):
        pos = pygame.mouse.get_pos()
        self._positions[num] = g.screen_pos_to_unit_pos(pos[0], pos[1])
        pigeons[num].set_pos(*pos)
        print "setting bird %s to pos %s (%s)" % (num, pos, self._positions[num])

    def set_car_pos(self):
        pos = pygame.mouse.get_pos()
        self._car = g.screen_pos_to_unit_pos(pos[0], pos[1])

    def record_poses(self):
        print "Recording pigeons_start_positions.json"
        config[PIGEONS_START_POSITIONS] = self._positions
        config[CAR_START_POSITION] = self._car
        config.save()


