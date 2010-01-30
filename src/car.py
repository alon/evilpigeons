from sprite import SpriteWorld
import globals as g

class Car(SpriteWorld):

    def __init__(self, world):
        super(Car, self).__init__(world=world, location=g.config.car_start_position, filename='car.png')
        # we never add the Car to the world, so it won't be displayed
        # the car png is just for collision (even though it is just a rectangle, so it
        # isn't accurate. Should have a polygon
        self._hits_allowed = g.car_hits_to_kill
        from shit import Shit
        self._kill_class = Shit
        self._rect.center = g.unit_pos_to_screen_pos(*g.config.car_start_position)
        self._already_hit = set() # a little ugly - we get hits in repeated rounds

    def onhit(self, hitter):
        if hitter in self._already_hit:
            return
        self._already_hit.add(hitter)
        if hitter.__class__ == self._kill_class:
            self._hits_allowed -= 1
            print "Car Hit - left = %s" % self._hits_allowed
            self._world.update_car_value(self._world._car_value - g.car_value_reduction) # should be kept in car
        if self._hits_allowed <= 0:
            self._world.car_is_dead_long_live_the_pigeons()

