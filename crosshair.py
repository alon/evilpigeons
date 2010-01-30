import pygame

from sprite import SpriteWorld, Projectile
import globals as g

class Crosshair(SpriteWorld):

    def __init__(self, world):
        super(Crosshair, self).__init__(world=world, location=(0,0), filename='crosshair.png')
        self._can_shoot = True
        self._action = self.do_follow_mouse()

    def shoot(self):
        if not self._can_shoot: return
        # make bullet appearance point look 3d, coming from behind
        self._can_shoot = False
        x, y = pygame.mouse.get_pos()
        self.general_shoot(projectile_class=Bullet, location=(g.width / 2, g.height), target=(x, y), done_callback=self._enable_shots)

    def _enable_shots(self):
        self._can_shoot = True

class Bullet(Projectile):

    def __init__(self, location, target, done_callback):
        super(Bullet, self).__init__(location=location, target=target, filename='bullet.png',
                final_size_ratio=0.5, shoot_sound=g.sounds['shot'], done_callback=done_callback)

