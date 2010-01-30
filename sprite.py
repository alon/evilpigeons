from math import pi
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

    def set_pos(self, x, y):
        self._rect.center = x, y

    def set_pos_from_mouse_pos(self):
        self._rect.center = pygame.mouse.get_pos()

    # Sprite helpers
    def set_sprite(self, sprite):
        self._sprite = sprite
        self._rect = self._sprite.get_rect()

    def scale(self, factor):
        center = self._rect.center
        start_width, start_height = self._orig_rect.size
        target_size = (int(start_width * factor), int(start_height * factor))
        self._sprite = pygame.transform.scale(self._orig_sprite, target_size)
        self._rect = self._sprite.get_rect()
        self._rect.center = center
        print self._rect

    def rotate(self, angle):
        angle = angle * 180 / pi
        center = self._rect.center
        self._sprite = pygame.transform.rotate(self._orig_sprite, angle)
        self._rect = self._sprite.get_rect()
        print self._rect
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
        if sprite_iter == None:
            sprite_iter = itertools.repeat(self._sprite)
        last_x = self._rect.center[0]
        for (x, y), sprite in zip(path, sprite_iter):
            # turn sprite to the right direction. We assume the images are always facing left
            if x > last_x:
                print "flipped"
                sprite = pygame.transform.flip(sprite, True, False) # flip_x, flip_y
            self.set_sprite(sprite)
            self.set_pos(x, y)
            yield 'movement'

    def do_path_with_size(self, path):
        start_sprite = self._sprite
        start_size = start_width, start_height = self._rect.size
        for x, y, size_ratio in path:
            target_size = (int(start_width * size_ratio), int(start_height * size_ratio))
            self._sprite = pygame.transform.scale(start_sprite, target_size)
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
            done_callback=lambda: None):
        super(Projectile, self).__init__(location = location, filename = filename)
        self._target = target
        self._projectile_path = interpolate(10, list(self._start_location)+[1.0], list(self._target) + [final_size_ratio])
        gens = []
        print done_callback
        def action_gen():
            for x in self.do_path_with_size(self._projectile_path): yield x
            if end_sound: end_sound.play()
            done_callback()
            for x in self.do_quit(): yield x
        if shoot_sound: shoot_sound.play()
        self._action = action_gen()
 
