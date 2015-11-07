#
# A class to represent one Tank in our Tank Wars Game
#
# MuddHacks 2015
#

import math
from constants import *
from tank_ais import AIManager
from bullet import Bullet
import json
import copy
from config import *
if USE_SIMULATOR:
    import js

class Tank:

    def __init__(self, ID, AIpath, perma_board_copy, x_pos, y_pos,
                       x_vel = 0,
                       y_vel = 0,
                       hp    = MAX_TANK_HP,
                       ammo  = 100000):
        self.perma_board_copy = perma_board_copy
        self.AIpath = AIpath
        self.AI = AIManager(AIpath, [perma_board_copy,ID])
        self.ID    = ID
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.score = 0
        self.age = 0

        self.hp = hp
        self.ammo = ammo

        self.recently_healed = False
        self.damage_IDs = []

    def take_turn(self, tank_coords):

        state = [tank_coords, self.hp, self.ammo, [int(round(self.x_pos)), int(round(self.y_pos))], self.damage_IDs]
        turn_info = self.AI.takeTurn(state)

        self.age += 1

        # set the tanks speed
        new_x_vel = turn_info[0][0]
        new_y_vel = turn_info[0][1]
        speed = math.sqrt(new_x_vel**2 + new_y_vel**2)
        if speed > MAX_TANK_SPEED:
            new_x_vel = new_x_vel*MAX_TANK_SPEED/speed
            new_y_vel = new_y_vel*MAX_TANK_SPEED/speed
        self.x_vel = new_x_vel
        self.y_vel = new_y_vel

        # make a bullet if necessary
        if turn_info[1] and self.ammo > 0:
            self.ammo -= 1
            b_x_vel = turn_info[2][0]
            b_y_vel = turn_info[2][1]
            speed = math.sqrt(b_x_vel**2 + b_y_vel**2)
            if speed != 0:
                b_x_pos = self.x_pos + b_x_vel*MAX_TANK_RADIUS/speed
                b_y_pos = self.y_pos + b_y_vel*MAX_TANK_RADIUS/speed
                return Bullet(self.ID,b_x_pos,b_y_pos,b_x_vel,b_y_vel)

    def is_dead(self):
        """ tells you if the tank is dead """
        return self.hp <= 0

    def damage(self,dm):
        """ damages the tank """
        self.hp -= dm

    def heal(self,rate,dt):
        """ heals the tank if its standing on the hospital """
        self.hp += rate*dt
        if self.hp > MAX_TANK_HP:
            self.hp = MAX_TANK_HP

    def move(self,dt):
        """ updates the position of the tank"""
        self.x_pos += self.x_vel*dt
        self.y_pos += self.y_vel*dt

    def get_center(self):
        """ rounds the x and y positions to get the relevant pixel """
        x = round(self.x_pos)
        y = round(self.y_pos)
        return [int(x),int(y)]

    def get_pixel_pos(self):
        """ returns a list of points in the order

                     -y
                      |
                -x ---+--- +x
                      |
                     +y


                    0 1 2
                    3 4 5
                    6 7 8   """

        c = self.get_center()

        zeroth  = [c[0]-1 , c[1]-1 ]
        first   = [c[0]   , c[1]-1 ]
        second  = [c[0]+1 , c[1]-1 ]
        third   = [c[0]-1 , c[1]   ]
        fourth  = [c[0]   , c[1]   ]
        fifth   = [c[0]+1 , c[1]   ]
        sixth   = [c[0]-1 , c[1]+1 ]
        seventh = [c[0]   , c[1]+1 ]
        eighth  = [c[0]+1 , c[1]+1 ]


        return [zeroth, first, second, third, fourth, fifth, sixth, seventh, eighth]

    def reload_ai(self):
        try:
            newai = AIManager(self.AIpath, self.perma_board_copy)
        except SandboxCodeExecutionFailed:
            # Bad AI! Ignore it
            pass
        else:
            self.AI = newai

    def cleanup(self):
        self.update_stat_file()

    def update_stat_file(self):
        """ updates the status file, which is shown in the web portal """
        logfile = "../data/{}_stat.json".format(self.ID)
        statobj = {
            'hp': self.hp,
            'max_hp': MAX_TANK_HP,
            'ammo': self.ammo,
            'score': self.score,
            'age': self.age,
            'alive': not self.is_dead(),
            'color': TANK_COLORS[self.color],
        }
        if USE_SIMULATOR:
            js.globals.handle_stat(self.ID, json.dumps(statobj))
        else:
            with open(logfile, 'w') as f:
                f.write(json.dumps(statobj))
