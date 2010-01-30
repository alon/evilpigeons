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

    def killed(self, killer):
        print "%s was killed by %s" % (self, killer)
        self._state = 'dying'
        self._action = self.do_quit()

    def do_quit(self):
        # yield the special "killme" code for pdump.World
        yield 'killme'

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

    def onhit(self, dest):
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

    def __init__(self, location, target, filename, final_size_ratio = 1.0):
        super(Projectile, self).__init__(location = location, filename = filename)
        self._target = target
        self._projectile_path = interpolate(10, list(self._start_location)+[1.0], list(self._target) + [final_size_ratio])
        self._action = itertools.chain(
            self.do_path_with_size(self._projectile_path),
            self.do_quit())
 
