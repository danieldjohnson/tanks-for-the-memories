#
# A class to run our Tank Wars game
#
# MuddHacks 2015
#

import copy
import time
import select, sys
from tank import Tank
from constants import *
from maps import *

class Game:

    def __init__(self, perma_board = []):
        """ if we want walls we give walls as a list of 2-element lists """

        self.perma_board = perma_board # <-- a list of lists of pixel values
        if len(self.perma_board) == 0:
            for i in range(32): #64
                self.perma_board += [[10]*64]

        self.ghost_board = [] # <-- a list of lists of pixel values
        for i in range(32): #64
            self.ghost_board += [[10]*64]

        self.board       = copy.deepcopy(self.perma_board)
        self.tanks       = self.load_test_tanks()
        self.bullets     = []
        self.t_minus     = TURN_RATE
        self.last_time_stamp = time.time()

    # UPDATING THINGS

    def update(self):
        """ update everything and deal with turns """

        new_time = time.time()

        dt = new_time - self.last_time_stamp
        self.last_time_stamp = new_time

        # if we've reached the next turn, run up until the turn
        # then do the turn
        # then run the remaining time
        if dt > self.t_minus:

            self.real_time_update(self.t_minus)

            # take the turns! if the tanks shoot, add them to the list
            tank_coords = []
            for t in self.tanks:
                if t:
                    tank_coords += [[t.ID,t.x_pos,t.y_pos]]
            for t in self.tanks:
                if t:
                    bullet = t.take_turn(tank_coords)
                    if bullet:
                        self.bullets += [bullet]

            self.real_time_update(dt - self.t_minus)
            self.t_minus = TURN_RATE

        # otherwise just run the whole time
        else:
            self.real_time_update(dt)


    def real_time_update(self, dt):
        """ update positions, kill things, in real time
            ASSUMES THAT self.t_minus >= dt"""

        self.t_minus -= dt
        self.board = copy.deepcopy(self.perma_board)
        self.ghost_board = []
        for i in range(32): #64
            self.ghost_board += [[10]*64]

        # bullets move first thus if they get shot they can escape their mama tank
        for b in self.bullets:

            # move the bullet
            b.move(dt)
            pos = b.get_pixel_pos()
            x = pos[0]
            y = pos[1]

            # kill the bullet if it hits a wall
            if (x < 0) or (y < 0) or (x > 63) or (y > 31): #63
                self.bullets.remove(b)
            elif (self.board[y][x] == WALL):
                self.bullets.remove(b)
            else:
                self.board[y][x] = BULLET

        # then tanks move
        for i in range(len(self.tanks)):

            t = self.tanks[i]

            if t:
                # move the tank
                t.move(dt)

                # check to see if the tank hits a wall
                positions = t.get_pixel_pos() # <-- actually 9 points
                for p in positions:
                    x = p[0]
                    y = p[1]
                    # if you hit a wall or go off the edge of the screen, don't move
                    if (self.board[y][x] == WALL) or (self.board[y][x] < 10) or (x < 0) or (y < 0) or (x > 63) or (y > 31): #63
                        t.move(-1.0*dt)
                        break

                # update the pixels on the board
                positions = t.get_pixel_pos() # <-- actually 9 points
                for p in positions:
                    x = p[0]
                    y = p[1]
                    # if you hit a bullet, find the bullet, kill it, take damage
                    if (self.board[y][x] == BULLET) and not t.is_dead():
                        for b in self.bullets:
                            b_pos = b.get_pixel_pos()
                            b_x = b_pos[0]
                            b_y = b_pos[1]

                            if (x==b_x) and (y==b_y):
                                t.damage(BULLET_DM)
                                t.damage_IDs += [b.ID]
                                self.bullets.remove(b)
                                if t.is_dead():
                                    self.tanks[i] = None
                                    break
                    # if you're on the hospital, heal yourself
                    elif (self.board[y][x] == HOSPITAL) and (not t.recently_healed):
                        t.heal(HOSPITAL_RATE, dt)
                        t.recently_healed = True
                    # finally set the pixel to be a tank
                    self.board[y][x] = i

                # once the tank is done moving, reset so it can be healed next update
                t.recently_healed = False

                # if t died, reset any pixels that were written before the tank died
                if t.is_dead():
                    for p in positions:
                        if self.board[y][x] == i:
                            self.board[y][x] = EMPTY
                # otherwise add the "eye" of the tank to the ghost_board
                else:
                    t_angle_scaled = (int(round(math.atan2(t.y_vel,t.x_vel)*8/(2*math.pi)))+4)%8
                    #
                    # adds a ghost eye acording to the direction according to the map
                    #
                    #     1 2 3
                    #     0 x 4
                    #     7 6 5
                    #
                    # corresponding to the normal geometric angle
                    #
                    eye_x = int(round(t.x_pos))
                    eye_y = int(round(t.y_pos))
                    if t_angle_scaled == 0:
                        eye_x -= 1
                    elif t_angle_scaled == 1:
                        eye_x -= 1
                        eye_y -= 1
                    elif t_angle_scaled == 2:
                        eye_y -= 1
                    elif t_angle_scaled == 3:
                        eye_y -= 1
                        eye_x += 1
                    elif t_angle_scaled == 4:
                        eye_x += 1
                    elif t_angle_scaled == 5:
                        eye_x += 1
                        eye_y += 1
                    elif t_angle_scaled == 6:
                        eye_y += 1
                    elif t_angle_scaled == 7:
                        eye_x -= 1
                        eye_y += 1

                    self.ghost_board[eye_y][eye_x] = EYE

        # finally draw the ghost board over the regular board
        for y in range(len(self.board)):
            for x in range(len(self.board[y])):
                ghost = self.ghost_board[y][x]
                if ghost != EMPTY:
                    self.board[y][x] = ghost









    # DRAWING THINGS

    def draw_board(self):
        for a in self.board:
            for b in a:
                print DEBUG_STRINGS[b],
            print ""

    # TESTING THINGS

    def load_test_tanks(self):

        tank_1 = Tank("penis",
                      "ais/test_1.py",
                      copy.deepcopy(self.perma_board),
                      27,27)
        tank_2 = Tank("dickbutt",
                      "ais/test_2.py",
                      copy.deepcopy(self.perma_board),
                      12,22)
        tank_3 = Tank("sex",
                      "ais/test_3.py",
                      copy.deepcopy(self.perma_board),
                      24,10)
        doctor = Tank("doc",
                      "ais/doctor.py",
                      copy.deepcopy(self.perma_board),
                      5,15)
        hugger = Tank("hug",
                      "ais/wall_hugger.py",
                      copy.deepcopy(self.perma_board),
                      19,10)
        return [tank_1,tank_2,tank_3,None,None,None,None,None,None,None,None]


if __name__ == "__main__":

    the_game = Game(walls_w_hosp_32)
    last_time_stamp = time.time()
    t_minus = 0.1
    while True:
        if select.select([sys.stdin,],[],[],0.0)[0]:
            print("sdfsdf")
        the_game.update()
        t_minus -= (time.time() - last_time_stamp)
        last_time_stamp = time.time()
        if t_minus < 0:
            the_game.draw_board()
            t_minus = 0.1
