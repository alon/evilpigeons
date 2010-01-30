import itertools

import pygame

from sprite import SpriteWorld
from shit import Shit
import data
import globals as g
import mathutil

################################################################################
# Utils

def num_to_numkey(num):
    if num > 9 or num < 0:
        raise Exception("No numkey for num %s" % num)
    return [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0][num]

def second_key(num):
    """ for editing paths, a second key for each pegion """
    return map(ord, 'qwertyuiop')[num]

################################################################################
# Pigeon controller

class PigeonController(object):

    def __init__(self, world, keymap):
        self._world = world
        pigeons = self._create_pigeons()
        for p in pigeons:
            self._world.add_sprite(p)
        self._pigeons = pigeons
        self._n = len(pigeons)
        self._setup_keymap(keymap)

    def _create_pigeons(self):
        pigeons_data = []
        pigeons_path_key_points = g.config.pigeons_path_key_points
        steps = g.pigeon_steps_per_half_path
        for i, path in enumerate(pigeons_path_key_points):
            print path
            x, y = path[0]
            key = num_to_numkey(i)
            to_int = lambda points: [(int(_x*g.width), int(_y*g.height)) for _x, _y in points]
            dive_path = to_int(mathutil.path(n=steps, points=path))
            return_path = to_int(mathutil.path(n=steps, points=list(reversed(path))))
            pigeons_data.append(dict(location=(int(x*g.width), int(y*g.height)), key=key,
                                     dive_path=dive_path, return_path=return_path))
        pigeons = [Pigeon(world=self._world, **d) for d in pigeons_data]
        return pigeons

    def _setup_keymap(self, keymap):
        for i, p in enumerate(self._pigeons):
            keymap.add(p._key, lambda i=i: self.try_dive(i))
            keymap.add(p._key, lambda i=i: self.try_diversion_flap(i), mod=pygame.KMOD_SHIFT)
        # XXX: should we have to do this every time we restart the game?
        if '--setpos' in g.argv:
            pos_recorder = g.PosRecorder(self._world)
            for i in xrange(len(self._pigeons)):
                keymap.add(second_key(i), lambda i=i: pos_recorder.reset_bird_path(i))
                keymap.add(num_to_numkey(i), lambda i=i: pos_recorder.set_bird_pos(i), pygame.KMOD_CTRL)
            keymap.add(ord('c'), pos_recorder.set_car_pos)
            keymap.add(ord('s'), pos_recorder.record_poses)

    def try_dive(self, i):
        # only one can dive at a time
        if any([p.isdiving() for p in self._pigeons]):
            return
        self._pigeons[i].start_dive()

    def try_diversion_flap(self, i):
        p = self._pigeons[i]
        if not p.isdiving():
            p.diversion_flap()


class Pigeon(SpriteWorld):

    def __init__(self, world, location, key, dive_path, return_path):
        SpriteWorld.__init__(self, world=world, location=location, filename='pigeon_fly.jpg')
        self._key = key
        self._dive_path = dive_path # predetermined path (later - generated?)
        self._return_path = return_path
        self._target = g.unit_pos_to_screen_pos(*g.config.car_start_position)
        flap_steps = 3
        d = flap_delay_steps = 2
        flap_sprite = data.get_sprite('pigeon_flap.png')
        a, b = flap_sprite, self._sprite
        self._flap_sprites = sum([[(a, d), (b, d)] for i in xrange(flap_steps)], []) + [(self._sprite, 0)]

    def defecate(self):
        self.general_shoot(projectile_class=Shit, location=self._rect.midbottom, target=self._target)

    def isdiving(self):
        return self._state == 'diving'

    def is_unprotected_from_hit(self):
        return self.isdiving() # TODO - check if out of perch

    def start_dive(self):
        self._state = 'diving'
        self._action = itertools.chain(
            self.do_path(self._dive_path),
            self.do_f(self.defecate),
            self.do_path(self._return_path))

    def diversion_flap(self):
        self._state = 'diversion_flap'
        self._action = self.do_animate(self._flap_sprites)

    # die
    def onhit(self, hitter):
        from crosshair import Bullet
        if hitter.__class__ == Bullet and self.is_unprotected_from_hit():
            self.killed(killer=hitter)

