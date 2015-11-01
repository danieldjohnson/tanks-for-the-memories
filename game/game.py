#
# A class to run our Tank Wars game
#
# MuddHacks 2015
#

import curses
import copy
import time
import os
import select, sys
import binascii
import sys
import random
import select
import hashlib

from constants import *
from config import *
if OUTPUT_LED:
    import RPi.GPIO

from tank import Tank
from maps import *
from tank_ais import SandboxCodeExecutionFailed

class Game:

    def __init__(self, perma_board = []):
        """ if we want walls/hospital we give them in perma_board
            perma_board should be formatted as a 64x64 2D list of pixel values """

        # the set of things on the board which never change
        # currently includes HOSPITAL and WALL
        # formatted as a 64x64 2D list of pixel values
        self.perma_board = perma_board
        if len(self.perma_board) == 0:
            for i in range(64):
                self.perma_board += [[EMPTY]*64]

        # purely aesthetic features which never interact
        # includes EYE for instance
        # formatted as a 64x64 2D list of pixel values
        self.ghost_board = []
        for i in range(64):
            self.ghost_board += [[EMPTY]*64]

        self.board       = copy.deepcopy(self.perma_board)
        self.tanks       = self.load_test_tanks()
        self.bullets     = []
        self.t_minus     = TURN_RATE
        self.last_time_stamp = time.time()

        self.pending_tank_ids = []


    # ------ FUNCTIONS TO UPDATE THE GAME -------

    def update(self):
        """ update everything and deal with turns """

        # check to see how much time has passed
        new_time = time.time()
        dt = new_time - self.last_time_stamp
        self.last_time_stamp = new_time


        # if we haven't reached the next turn, just update everything
        if dt < self.t_minus:
            self.real_time_update(dt)

        # if we HAVE reached the next turn, run up until the turn
        # then do the turn
        # then run the remaining time
        else:

            self.real_time_update(self.t_minus)

            # add new tanks, if necessary
            for newid in self.pending_tank_ids:
                for i in range(len(self.tanks)):
                    if self.tanks[i] is not None and self.tanks[i].ID == newid:
                        self.tanks[i].reload_ai()
                        break
                else:
                    # Tank wasn't found! Add it if there is an AI
                    if not os.path.isfile("../data/"+newid+".py"):
                        break
                    for i in range(len(self.tanks)):
                        if self.tanks[i] is None:
                            # Found a space for our tank
                            try:
                                newtank = Tank(newid,
                                              "../data/"+newid+".py",
                                              copy.deepcopy(self.perma_board),
                                              random.randint(2,62),
                                              random.randint(2,62))
                            except SandboxCodeExecutionFailed:
                                # Couldn't create tank. Skip to next tank
                                break
                            else:
                                self.tanks[i] = newtank
                                # Move on to next tank
                                break
            self.pending_tank_ids = []

            # take the turns!
            # if the tanks shoot, add their bullets to the bulletlist
            tank_coords = []
            for t in self.tanks:
                if t:
                    tank_coords += [[t.ID,t.x_pos,t.y_pos]]
            for t in self.tanks:
                if t:
                    bullet = t.take_turn(tank_coords)
                    if bullet:
                        self.bullets += [bullet]
            for t in self.tanks:
                if t:
                    t.update_stat_file()

            self.real_time_update(dt - self.t_minus)
            self.t_minus = TURN_RATE


    def real_time_update(self, dt):
        """ update positions, kill things, in real time
            ASSUMES THAT self.t_minus >= dt
            that is, that no turn happens in the middle of dt"""

        self.t_minus -= dt

        # copy the permanent features before we add on tanks,bullets,etc
        self.board = copy.deepcopy(self.perma_board)

        # CURRENTLY WE CLEAR THE GHOST_BOARD EVERY FRAME
        # THIS MAY CHANGE IN THE FUTURE AS WE ADD MORE ANIMATIONS
        self.ghost_board = []
        for i in range(64):
            self.ghost_board += [[EMPTY]*64]

        # bullets move first thus if they get shot they can escape their mama tank
        for b in self.bullets:

            # move the bullet
            b.move(dt)
            pos = b.get_pixel_pos()
            x = pos[0]
            y = pos[1]

            # kill the bullet if it hits a wall
            if (x < 0) or (y < 0) or (x > 63) or (y > 63):
                self.bullets.remove(b)
            elif (self.board[y][x] == WALL):
                self.bullets.remove(b)
            else:
                self.board[y][x] = BULLET

        # then tanks move
        for i in range(len(self.tanks)):

            t = self.tanks[i]

            # some of our array entries may be null
            if t:

                t.move(dt)

                # check to see if the tank hits a wall
                positions = t.get_pixel_pos() # <-- actually 9 positions
                for p in positions:
                    x = p[0]
                    y = p[1]
                    # if you hit a wall or go off the edge of the screen, don't move
                    if (self.board[y][x] == WALL) or (self.board[y][x] < 10) or (x < 0) or (y < 0) or (x > 63) or (y > 63):
                        t.move(-1.0*dt)
                        break

                # update the pixels on the board
                positions = t.get_pixel_pos() # <-- actually 9 positions
                for p in positions:
                    x = p[0]
                    y = p[1]
                    # if you hit a bullet:
                    #   find the bullet, kill it, take damage, record your aggressor
                    if (self.board[y][x] == BULLET) and not t.is_dead():
                        for b in self.bullets:
                            b_pos = b.get_pixel_pos()
                            b_x = b_pos[0]
                            b_y = b_pos[1]

                            if (x==b_x) and (y==b_y):
                                bullet_id = b.ID
                                self.bullets.remove(b)
                                t.damage(BULLET_DM)
                                t.damage_IDs += [bullet_id]
                                if t.is_dead():
                                    self.tanks[i] = None
                                    for q in self.tanks:
                                        if q != None and q.ID == bullet_id:
                                            q.score += 1
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
                # according to the direction in the map below, which 
                # corresponds to the angle the tank is pointing
                #
                #     1 2 3
                #     0 x 4
                #     7 6 5
                #
                else:
                    t_angle_scaled = (int(round(math.atan2(t.y_vel,t.x_vel)*8/(2*math.pi)))+4)%8
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




    # ------ FUNCTIONS TO DRAW THE GAME -------



    def draw_board(self):

        # draw the board to STDOUT
        if OUTPUT_STDOUT:
            win.refresh()
            for i in range (0,len(self.board)):
                for j in range (0,len(self.board[0])):
                    n = self.board[i][j]
                    if n == 10 or n == 15:
                        color = 2
                    elif n == 11:
                        color = 2
                    elif n == 12:
                        color = 3
                    elif n == 13:
                        color = 4
                    else:
                        color = 5

                    win.addch(i,j,DEBUG_STRINGS[n],curses.color_pair(color))

        # draw the board to the LED matrix
        if OUTPUT_LED:
            assert len(self.board) == 64,    'Board width  not 64, update display output'
            assert len(self.board[0]) == 64, 'Board height not 64, update display output'
            mymap = [[(y*4,x*4,0) for x in range(64)] for y in range(64)]
            bytes_to_write = [0 for i in range(3*64*64)]
            for row in range(32/2):
                for col in range(64):
                    bytes_to_write[(    row *64+col)*3*2+0] = rev_bits_table[gamma_correction_table[COLORS[self.board[-(row+ 0)-1][-col-1]][0]]]
                    bytes_to_write[(    row *64+col)*3*2+1] = rev_bits_table[gamma_correction_table[COLORS[self.board[-(row+ 0)-1][-col-1]][1]]]
                    bytes_to_write[(    row *64+col)*3*2+2] = rev_bits_table[gamma_correction_table[COLORS[self.board[-(row+ 0)-1][-col-1]][2]]]

                    bytes_to_write[(    row *64+col)*3*2+3] = rev_bits_table[gamma_correction_table[COLORS[self.board[-(row+16)-1][-col-1]][0]]]
                    bytes_to_write[(    row *64+col)*3*2+4] = rev_bits_table[gamma_correction_table[COLORS[self.board[-(row+16)-1][-col-1]][1]]]
                    bytes_to_write[(    row *64+col)*3*2+5] = rev_bits_table[gamma_correction_table[COLORS[self.board[-(row+16)-1][-col-1]][2]]]

                    bytes_to_write[((16+row)*64+col)*3*2+0] = rev_bits_table[gamma_correction_table[COLORS[self.board[-(row+32)-1][-col-1]][0]]]
                    bytes_to_write[((16+row)*64+col)*3*2+1] = rev_bits_table[gamma_correction_table[COLORS[self.board[-(row+32)-1][-col-1]][1]]]
                    bytes_to_write[((16+row)*64+col)*3*2+2] = rev_bits_table[gamma_correction_table[COLORS[self.board[-(row+32)-1][-col-1]][2]]]

                    bytes_to_write[((16+row)*64+col)*3*2+3] = rev_bits_table[gamma_correction_table[COLORS[self.board[-(row+48)-1][-col-1]][0]]]
                    bytes_to_write[((16+row)*64+col)*3*2+4] = rev_bits_table[gamma_correction_table[COLORS[self.board[-(row+48)-1][-col-1]][1]]]
                    bytes_to_write[((16+row)*64+col)*3*2+5] = rev_bits_table[gamma_correction_table[COLORS[self.board[-(row+48)-1][-col-1]][2]]]
            reset_fpga()
            with open("/dev/spidev0.1", "wb") as spifile:
                while bytes_to_write:
                    spifile.write(bytearray(bytes_to_write[:spi_max_write_sz]))
                    bytes_to_write = bytes_to_write[spi_max_write_sz:]

    # ------ MISCELLANEOUS THINGS THE GAME NEEDS TO DO -------

    def load_test_tanks(self):

        tank_1 = Tank("penis",
                      "ais/test_1.py",
                      copy.deepcopy(self.perma_board),
                      27,27)
        tank_2 = Tank("dickbutt",
                      "ais/doctor.py",
                      copy.deepcopy(self.perma_board),
                      12,22)
        tank_3 = Tank("sex",
                      "ais/test_3.py",
                      copy.deepcopy(self.perma_board),
                      5,12)
        doctor = Tank("doc",
                      "ais/doctor.py",
                      copy.deepcopy(self.perma_board),
                      5,4)
        # hugger = Tank("hug",
        #               "ais/wall_hugger.py",
        #               copy.deepcopy(self.perma_board),
        #               19,10)
        #
        #               doctor,hugger,
        return [tank_1,tank_2,tank_3,None,None,None,None,None,None,None,None]

if OUTPUT_LED:
    def reset_fpga():
        RPi.GPIO.output(FPGA_RESET_PIN, 0)
        RPi.GPIO.output(FPGA_RESET_PIN, 1)
        

def preprocess_idnum(idnum):
    # Hash the id number so that it's not trivial to match students to their
    # ID numbers
    return hashlib.sha512(idnum).hexdigest()

if __name__ == "__main__":

    the_game = Game(walls_w_hosp)
    last_time_stamp = time.time()
    t_minus = 0.1
    if OUTPUT_STDOUT:
        stdscr = curses.initscr()
        curses.start_color()
        win = curses.newwin(65,65,0,0)
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE) #empty/eye
        curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_WHITE)  #wall
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_WHITE) #hospital
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_WHITE)  #bullet
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_WHITE)  #tank
    if OUTPUT_LED:
        # Toggle the FPGA's reset line
        RPi.GPIO.setmode(RPi.GPIO.BOARD)
        RPi.GPIO.setup(FPGA_RESET_PIN, RPi.GPIO.OUT)
        reset_fpga()

    buffered_input = ""
    try:
        while True:
            if select.select([sys.stdin,],[],[],0.0) == ([sys.stdin],[],[]):
                idnum = sys.stdin.readline()[2:-3]
                the_game.pending_tank_ids.append(preprocess_idnum(idnum))
            the_game.update()
            t_minus -= (time.time() - last_time_stamp)
            last_time_stamp = time.time()
            if t_minus < 0:
                the_game.draw_board()
                t_minus = 0.1
    finally:
        if OUTPUT_LED:
            RPi.GPIO.cleanup()
        if OUTPUT_STDOUT:
            curses.endwin()
