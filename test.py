import sys, pygame
pygame.init()

size = width, height = 320, 240
speed = [2, 2]
black = 0, 0, 0

screen = pygame.display.set_mode(size)

ball = pygame.image.load("ball.png")
ballrect = ball.get_rect()

def once():
    global ballrect
    global ball
    #ballrect = ballrect.move(speed)
    screen.fill(black)
    screen.blit(ball, ballrect)
    pygame.display.flip()

