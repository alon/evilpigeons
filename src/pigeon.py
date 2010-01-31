# Copyright Evil Pegions team Global Game Jam 2010:
#  Simon Reisman
#  Omer Nainudel
#  Ori Cohen
#  Alon Levy
#
# This code is licensed under the Creative Commons License. For further details,
# see the LICENSE

import itertools
from math import pi, cos, sin

import pygame
from mathutil import linspace

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
        self._pigeons_hit = 0

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
        pigeons = [Pigeon(controller=self, **d) for d in pigeons_data]
        return pigeons

    def _setup_keymap(self, keymap):
        for i, p in enumerate(self._pigeons):
            keymap.add(p._key, lambda i=i, self=self: self.try_dive(i))
            keymap.add(p._key, lambda i=i, self=self: self.try_diversion_flap(i), mod=pygame.KMOD_SHIFT)
        # XXX: should we have to do this every time we restart the game?
        if '--setpos' in g.argv:
            pos_recorder = g.PosRecorder(self._world)
            for i in xrange(len(self._pigeons)):
                keymap.add(second_key(i), lambda i=i, pos_recorder=pos_recorder: pos_recorder.reset_bird_path(i))
                keymap.add(num_to_numkey(i), lambda i=i, pos_recorder=pos_recorder: pos_recorder.set_bird_pos(i), pygame.KMOD_CTRL)
            keymap.add(ord('c'), pos_recorder.set_car_pos)
            keymap.add(ord('s'), pos_recorder.record_poses)

    def try_dive(self, i):
        # only one can dive at a time
        if any([not p.isdead() and p.isdiving() for p in self._pigeons]):
            return
        self._pigeons[i].start_dive()

    def try_diversion_flap(self, i):
        p = self._pigeons[i]
        if not p.isdiving():
            p.diversion_flap()

    def pigeon_hit(self, pigeon):
        print "hit +1"
        self._pigeons_hit += 1
        if self._pigeons_hit == len(self._pigeons):
            print "%s == %s" % (self._pigeons_hit, len(self._pigeons))
            self._world.pigeons_dead_long_live_the_car()

class Pigeon(SpriteWorld):

    def __init__(self, controller, location, key, dive_path, return_path):
        SpriteWorld.__init__(self, world=controller._world, location=location, filename='pigeon_sit.png')
        if self._rect.center[0] < g.width / 2:
            self.replace_sprite(pygame.transform.flip(self._sprite, True, False))
        self._controller = controller
        self._key = key
        self._dive_path = dive_path # predetermined path (later - generated?)
        self._return_path = return_path
        self._target = g.unit_pos_to_screen_pos(*g.config.car_start_position)
        flap_steps = 3
        d = flap_delay_steps = 2
        self._flap_sprites = [data.get_sprite(sprite) for sprite in ['pigeon_flap_up.png', 'pigeon_flap_down.png']]
        self._flap_sprite_iter = itertools.cycle(self._flap_sprites)
        a, b = self._flap_sprites
        self._diversion_flap_sprites = sum([[(a, d), (b, d)] for i in xrange(flap_steps)], []) + [(self._sprite, 0)]

    def defecate(self):
        self.general_shoot(projectile_class=Shit, location=self._rect.midbottom, target=self._target)

    def isdiving(self):
        return self._state == 'diving'

    def is_unprotected_from_hit(self):
        return self.isdiving() # TODO - check if out of perch

    def _start_flap_sound(self):
        c = g.sounds['pigeon_flap'].play()
        if c is None:
            print "STRANGE BUG #1 - g.sounds['pigeon_flap'].play() returned None"
            return None
        c.set_volume(2.0) # default 1.0
        return c

    def start_dive(self):
        if self.isdead(): return
        self._state = 'diving'
        channel = self._start_flap_sound()
        self._action = self.do_end(itertools.chain(
            self.do_path(self._dive_path, sprite_iter = self._flap_sprite_iter),
            self.do_f(self.defecate),
            self.do_path(self._return_path, sprite_iter = self._flap_sprite_iter)),
            end=lambda self=self, channel=channel: (self.set_sprite(self._orig_sprite), channel.stop()))

    def diversion_flap(self):
        print self._flap_sprites
        self._state = 'diversion_flap'
        if self._rect.center[0] < g.width / 2:
            sprites = [pygame.transform.flip(sprite, True, False) for sprite in self._flap_sprites]
        else:
            sprites = list(self._flap_sprites)
        sprites.append(self._orig_sprite)
        channel = self._start_flap_sound()
        flap_animation_gen = self.do_animate([(x, 0) for x in sprites]*3)
        if channel is None: # can happen if we run out of channels, max defaults to 8
            print "Warning: ran out of channels"
            self._action = flap_animation_gen
        else:
            self._action = self.do_end(flap_animation_gen, end=lambda channel=channel: channel.stop())

    # die
    def onhit(self, hitter):
        from crosshair import Bullet
        if not hitter.__class__ == Bullet or not self.is_unprotected_from_hit() or self._state == 'dying': return
        def explode_animation():
            # create a bunch of sprites of moving trianagles to outside
            s = pygame.Surface(size=(500,500))
            s.set_colorkey((0,0,0))
            self._rect = rect = s.get_rect()
            rect.center = self._rect.center
            m = 100
            l = 200
            for r in linspace(100, 300, 5):
                for angle in [0, pi/2, pi, pi*3/2, 2*pi]:
                    sa, ca = sin(angle), cos(angle)
                    pygame.draw.polygon(s, g.black, [
                        (ca*r, sa*r),
                        (ca*(r + l) + sa*m, ca*(r + m) + sa*l),
                        (ca*(r + l) - sa*m, ca*(r - m) - sa*l)])
                self._orig_sprite = self._sprite = s
                print "explode"
                yield 'explode'
            self.hide()
        # explode animation
        # TODO: make explosion work
        #self._action = explode_animation()

        self.killed(killer=hitter)
        print "PIGEON DOWN! PIGEON DOWN!"
        g.sounds['pigeon_hit'].play()
        print g.sounds['pigeon_hit'].get_length()
        self._controller.pigeon_hit(self)


