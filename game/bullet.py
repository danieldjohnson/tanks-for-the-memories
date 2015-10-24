#
# A class to represent one Bullet in our Tank Wars Game
#
# MuddHacks 2015
#

import math

class Bullet:

    def __init__(self, x_pos, y_pos, x_vel, y_vel):

        self.x_pos = x_pos
        self.y_pos = y_pos

        speed = math.sqrt(self.x_vel**2 + self.y_vel**2)
        self.x_vel = x_vel*BULLET_SPEED/speed 
        self.y_vel = y_vel*BULLET_SPEED/speed

    def move(self, dt):
        """ updates the position of the bullet """
        self.x_pos += x_vel*dt
        self.y_pos += y_vel*dt

    def get_pixel_pos(self):
        """ rounds the x and y positions to get the relevant pixel """
        x = round(self.x_pos)
        y = round(self.y_pos)
        return [x,y]

    
