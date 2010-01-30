import itertools

import pygame

from mathutil import interpolate

class Sprite(object):
    def __init__(self, location, filename):
        self._start_location = location
        self._sprite = pygame.image.load(filename)
        self._rect = self._sprite.get_rect()
        self.set_pos(*self._start_location)
        self._state = None
        self._action = self.do_nothing()

    def set_pos(self, x, y):
        self._rect.center = x, y

    def set_pos_from_mouse_pos(self):
        self._rect.center = pygame.mouse.get_pos()

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
    def do_path(self, path):
        for x, y in path:
            self.set_pos(x, y)
            yield 'movement'

    def do_quit(self):
        # yield the special "killme" code for pdump.World
        yield 'killme'

    def do_f(self, f):
        yield f()

    def do_nothing(self):
        self._state = 'nothing'
        while True:
            yield 'nothing'

class SpriteWorld(Sprite):

    def __init__(self, world, location, filename):
        super(SpriteWorld, self).__init__(location=location, filename=filename)
        self._world = world
    
    def general_shoot(self, projectile_class, location, target):
        self._world.add_sprite(projectile_class(location=location, target=target))

class Projectile(Sprite):
    def __init__(self, location, target, filename):
        super(Projectile, self).__init__(location = location, filename = filename)
        self._target = target
        self._projectile_path = interpolate(10, self._start_location, self._target)
        self._action = itertools.chain(
            self.do_path(self._projectile_path),
            self.do_quit())
 
