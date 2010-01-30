import math
from math import cos, sin

import pygame

from sprite import SpriteWorld, Projectile, Sprite
import globals as g

class Broom(Sprite):
    def __init__(self):
        super(Broom, self).__init__(location=g.unit_pos_to_screen_pos(*g.config.broom_position), filename='broom.png')

def edge_of_circle((x, y), angle, r):
    return x + r*cos(angle), y + r*sin(angle)

class Crosshair(SpriteWorld):

    def __init__(self, world):
        super(Crosshair, self).__init__(world=world, location=(0,0), filename='crosshair.png')
        self._steps_to_shoot = 0
        self._broom = Broom()
        self._broom_exit_point = self._broom._rect.center # will be replaced when mouse is moved first
        self._action = self.do_follow_mouse()
        self._world.add_sprite(self._broom)

    def do_follow_mouse(self):
        pigeons = self._world._pcontroller._pigeons
        for x in super(Crosshair, self).do_follow_mouse():
            cx, cy = self._rect.center
            rx, ry = self._broom._rect.center
            direction = math.atan2(cy - ry, cx - rx)
            self._broom.rotate(-direction - 0.6)
            self._broom_exit_point = edge_of_circle(self._broom._rect.center, angle=direction, r=170)
            # hide crosshair if it is over a pigeon
            if any([not p._state == 'diving' and p._rect.collidepoint(self._rect.center) for p in pigeons]):
                self.hide()
            else:
                self.show()
            if self._steps_to_shoot > 0:
                self._steps_to_shoot -= 1
            yield x

    def shoot(self):
        if self._steps_to_shoot > 0: return
        # make bullet appearance point look 3d, coming from behind
        self._steps_to_shoot = g.steps_to_shoot
        x, y = pygame.mouse.get_pos()
        self.general_shoot(projectile_class=Bullet, location=self._broom_exit_point, target=(x, y), done_callback=self._enable_shots)

    def _enable_shots(self):
        self._steps_to_shoot = g.steps_to_shoot

class Bullet(Projectile):

    def __init__(self, location, target, done_callback):
        super(Bullet, self).__init__(location=location, target=target, filename='bullet.png',
                final_size_ratio=0.5, shoot_sound=g.sounds['shot'], done_callback=done_callback)

