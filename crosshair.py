import pygame

from sprite import SpriteWorld, Projectile
import globals as g

class Crosshair(SpriteWorld):

    def __init__(self, world):
        super(Crosshair, self).__init__(world=world, location=(0,0), filename='crosshair.png')

    def shoot(self):
        # make bullet appearance point look 3d, coming from behind
        x, y = pygame.mouse.get_pos()
        xs = x + 100 if x < g.width / 2 else x - 100
        ys = y + 100 if y < g.height / 2 else y - 100
        self.general_shoot(projectile_class=Bullet, location=(xs, ys), target=(x, y))

class Bullet(Projectile):

    def __init__(self, location, target):
        super(Bullet, self).__init__(location=location, target=target, filename='bullet.png')

