#
# A class to represent one Bullet in our Tank Wars Game
#
# MuddHacks 2015
#

import math
import copy
from constants import *

class Bullet:

    def __init__(self, ID, x_pos, y_pos, x_vel, y_vel):

        self.ID = ID

        self.x_pos = x_pos
        self.y_pos = y_pos

        speed = math.sqrt(x_vel**2 + y_vel**2)
        self.x_vel = x_vel*BULLET_SPEED/speed 
        self.y_vel = y_vel*BULLET_SPEED/speed

    def move(self, dt):
        """ updates the position of the bullet """
        self.x_pos += self.x_vel*dt
        self.y_pos += self.y_vel*dt

    def get_pixel_pos(self):
        """ rounds the x and y positions to get the relevant pixel """
        x = round(copy.deepcopy(self.x_pos))
        y = round(copy.deepcopy(self.y_pos))
        return [int(x),int(y)]

    
