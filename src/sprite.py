# Copyright Evil Pegions team Global Game Jam 2010:
#  Simon Reisman
#  Omer Nainudel
#  Ori Cohen
#  Alon Levy
#
# This code is licensed under the Creative Commons License. For further details,
# see the LICENSE

from math import pi, atan2
import itertools

import pygame

from mathutil import interpolate
import data

class Sprite(object):
    def __init__(self, location, filename):
        self._start_location = location
        self._sprite = self._orig_sprite = data.get_sprite(filename)
        if self._sprite is None:
            import pdb; pdb.set_trace()
        self._rect = self._sprite.get_rect()
        self._orig_rect = self._rect
        self.set_pos(*self._start_location)
        self._state = None
        self._action = self.do_nothing()
        self._active_path = None # do_path uses this, and do_path_size
        self._active_i = 0
        self._visible = True

    def visible(self):
        return self._visible

    def hide(self):
        self._visible = False

    def show(self):
        self._visible = True
    
    def set_pos(self, x, y):
        self._rect.center = x, y

    def set_pos_from_mouse_pos(self):
        self._rect.center = pygame.mouse.get_pos()

    # Sprite helpers
    def set_sprite(self, sprite):
        """ sets current sprite but keeps self._orig_sprite as is """
        #print "setting to %s" % str(sprite)
        center = self._rect.center
        self._sprite = sprite
        self._rect = self._sprite.get_rect()
        self._rect.center = center

    def replace_sprite(self, sprite):
        """ set_sprite, but also change self._orig_sprite """
        self.set_sprite(sprite)
        self._orig_sprite = sprite

    def scale(self, factor):
        center = self._rect.center
        start_width, start_height = self._orig_rect.size
        target_size = (int(start_width * factor), int(start_height * factor))
        self._sprite = pygame.transform.scale(self._orig_sprite, target_size)
        self._rect = self._sprite.get_rect()
        self._rect.center = center

    def rotate(self, angle):
        angle = angle * 180 / pi
        center = self._rect.center
        self._sprite = pygame.transform.rotate(self._orig_sprite, angle)
        self._rect = self._sprite.get_rect()
        self._rect.center = center

    # The event system: self._action is a generator, that does stuff
    # the simulate function simply lets it run until the next yield.

    def simulate(self):
        # The simulate function works like this:
        # self._action is always a generator. It may yield anything,
        # which is ignored unless it is a callable. In that case,
        # that callable is used to replace the current generator.
        try:
            next = self._action.next()
            if callable(next):
                self._action = next()
        except StopIteration:
            next = self._action = self.do_nothing()
        return next # used to say "we are done", i.e. to delete bombs

    # Some default actions
    def do_path(self, path, sprite_iter = None):
        def iter_current_orig_sprite():
            while True:
                print "BLA %s" % str(self._orig_sprite)
                yield self._orig_sprite
        if sprite_iter == None:
            sprite_iter = iter_current_orig_sprite()
        last_x = self._rect.center[0]
        for (x, y), sprite in zip(path, sprite_iter):
            # turn sprite to the right direction. We assume the images are always facing left
            if x > last_x:
                #print "flipped"
                sprite = pygame.transform.flip(sprite, True, False) # flip_x, flip_y
            self.set_sprite(sprite)
            self.set_pos(x, y)
            yield 'movement'

    def do_path_with_size(self, path, rotate=False):
        """ path and change size with path and do rotation according to path direction"""
        self._active_path = path
        self._active_i = 0
        start_size = start_width, start_height = self._rect.size
        angle = 0.0
        if rotate:
            ex, ey, ration = path[-1]
            sx, sy = self._rect.center
            # we assume the angle of the projectile is constant, according to start and end points of path
            angle = (pi - atan2(sy - ey, sx - ex)) * 180.0 / pi
        for i, (x, y, size_ratio) in enumerate(path):
            self._active_i = i
            #target_size = (int(start_width * size_ratio), int(start_height * size_ratio))
            self._sprite = pygame.transform.rotozoom(self._orig_sprite, angle, size_ratio)
            self._rect = self._sprite.get_rect()
            self.set_pos(x, y)
            yield 'movement'
        self._rect.size = start_size

    def do_follow_mouse(self):
        while True:
            self.set_pos_from_mouse_pos()
            yield 'follow_mouse'

    def isdead(self):
        return self._state == 'dying'

    def killed(self, killer):
        print "%s was killed by %s" % (self, killer)
        self._state = 'dying'
        self._action = self.do_quit()

    def do_quit(self):
        # yield the special "killme" code for pdump.World
        yield 'killme'

    def do_sound(self, sound):
        yield 'playing_sound'
        sound.play()

    def do_animate(self, sprites):
        """ animate in place - hopefully the sprites are the same size, but we don't care """
        for sprite, delay_steps in sprites:
            self._sprite = sprite
            yield 'animate'
            for i in xrange(delay_steps):
                yield 'animate_delay'

    def do_f(self, f):
        yield f()

    def do_end(self, gen, end):
        for x in gen:
            yield x
        end()

    def do_nothing(self):
        self._state = 'nothing'
        while True:
            yield 'nothing'

    def onhit(self, hitter):
        """ default onhit - reimplement """
        pass

class SpriteWorld(Sprite):

    def __init__(self, world, location, filename):
        super(SpriteWorld, self).__init__(location=location, filename=filename)
        self._world = world
    
    def general_shoot(self, projectile_class, location, target, **dict):
        """ dict is passed to the projectile_class, for final_size_ratio for example """
        self._world.add_sprite(projectile_class(location=location, target=target, **dict))

class Projectile(Sprite):

    def __init__(self, location, target, filename, final_size_ratio = 1.0, shoot_sound = None, end_sound = None,
            done_callback=lambda: None, eternal=False, rotate=False):
        super(Projectile, self).__init__(location = location, filename = filename)
        self._target = target
        self._rotate = rotate
        self._projectile_path = interpolate(10, list(self._start_location)+[1.0], list(self._target) + [final_size_ratio])
        gens = []
        print done_callback
        def action_gen():
            for x in self.do_path_with_size(self._projectile_path, rotate=self._rotate): yield x
            if end_sound: end_sound.play()
            done_callback()
            if not eternal:
                for x in self.do_quit(): yield x
        if shoot_sound: shoot_sound.play()
        self._action = action_gen()
 
