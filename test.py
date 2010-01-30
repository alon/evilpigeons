#!/usr/bin/python

import itertools
import sys, pygame
pygame.init()

size = width, height = 320, 240
speed = [2, 2]
black = 0, 0, 0

screen = pygame.display.set_mode(size)

ball = pygame.image.load("ball.png")
ballrect = ball.get_rect()

sizes = itertools.cycle([(50,50),(100,100)])

def once():
    global ballrect
    global ball
    #ballrect = ballrect.move(speed)
    import pdb; pdb.set_trace()
    ballrect.size = sizes.next()
    screen.fill(black)
    screen.blit(ball, ballrect)
    pygame.display.flip()

if __name__ == '__main__':
    import time
    while True:
        time.sleep(0.1)
        once()
        
