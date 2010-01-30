import pygame

from sprite import SpriteWorld, Projectile
import globals as g

class Crosshair(SpriteWorld):

    def __init__(self, world):
        super(Crosshair, self).__init__(world=world, location=(0,0), filename='crosshair.png')
        self._action = self.do_follow_mouse()

    def shoot(self):
        # make bullet appearance point look 3d, coming from behind
        x, y = pygame.mouse.get_pos()
        self.general_shoot(projectile_class=Bullet, location=(g.width / 2, g.height), target=(x, y))

class Bullet(Projectile):

    def __init__(self, location, target):
        super(Bullet, self).__init__(location=location, target=target, filename='bullet.png', final_size_ratio=0.5, shoot_sound=g.sounds['shot'])

