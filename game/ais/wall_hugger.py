#sample AI

# coordinates are defined as follows:

#      -y
#       |
# -x ---+--- +x
#       |
#      +y

# do_turn takes the following inputs, packed into a list called 'state':

#   tank_coords : coordinates of all tanks on the board in format: [[name_1, x_pos_1, y_pos_1],[name_2, x_pos_2, y_pos_2], ... ]
#   hp          : tank's current health
#   x_pos       : tank's x-coordinate [0-63]
#   y_pos       : tank's y-coordinate [0-63]
#   been_hit    : boolean variable describing whether the tank has been hit
#   aggressors  : all tanks that have shot you in the past turn, in format: [name1, name2, name3, ... ]

# do_turn returns the following outputs, stored in a list of form:
#   [x_vel, y_vel, tx, ty]

#   x_vel, y_vel  : tank's velocity vector
#   tx, ty        : tank's turret vector
#   shoot         : whether the tank should shoot (in the direction of its turret) on the current turn

EMPTY = 10
WALL  = 11
HOSPITAL = 12
MAX_TANK_SPEED  = 1

class TankAI:

    def init(self,init_state):
        self.board = init_state
        self.state = "begin"
        self.no_move  = [ 0, 0]
        self.go_north = [ 0,-1]
        self.go_east  = [ 1, 0]
        self.go_west  = [-1, 0]
        self.go_south = [ 0, 1]

    def takeTurn(self,state):
        [tank_coords, hp, ammo, [x_pos, y_pos], aggressors] = state

        N = self.N()
        E = self.E()
        W = self.W()
        S = self.S()


        if self.state == "begin":
            if not N:
                return get_return(self.go_north)
            else:
                self.state = "east"
                return get_return(self.no_move)

        elif self.state == "north":
            if not W:
                self.state = "west"
                return get_return(self.go_west)
            elif not N:
                return get_return(self.go_north)
            elif not E:
                self.state = "east"
                return get_return(self.go_east)
            else:
                self.state = "south"
                return get_return(self.go_south)

        elif self.state == "east":
            if not N:
                self.state = "north"
                return get_return(self.go_north)
            elif not E:
                return get_return(self.go_east)
            elif not S:
                self.state = "south"
                return get_return(self.go_south)
            else:
                self.state = "west"
                return get_return(self.go_west)

        elif self.state == "west":
            if not S:
                self.state = "south"
                return get_return(self.go_south)
            elif not W:
                return get_return(self.go_west)
            elif not N:
                self.state = "north"
                return get_return(self.go_north)
            else:
                self.state = "east"
                return get_return(self.go_east)

        elif self.state == "south":
            if not E:
                self.state = "east"
                return get_return(self.go_east)
            elif not S:
                return get_return(self.go_south)
            elif not W:
                self.state = "west"
                return get_return(self.go_west)
            else:
                self.state = "north"
                return get_return(self.go_north)

        else:
            return get_return(self.no_move)


    def get_return(dir):
        x_dir = tank_coords[0][1] - x_pos
        y_dir = tank_coords[0][2] - y_pos
        return [dir,True,[x_dir,y_dir]]

    def N(self):
        return ((self.board[x_pos  ,y_pos-2]==WALL) or (self.board[x_pos-1,y_pos-2]==WALL) or (self.board[x_pos+1,y_pos-2]==WALL))

    def E(self):
        return ((self.board[x_pos+2,y_pos  ]==WALL) or (self.board[x_pos+2,y_pos-1]==WALL) or (self.board[x_pos+2,y_pos+1]==WALL))

    def W(self):
        return ((self.board[x_pos-2,y_pos  ]==WALL) or (self.board[x_pos-2,y_pos-1]==WALL) or (self.board[x_pos-2,y_pos+1]==WALL))

    def S(self):
        return ((self.board[x_pos  ,y_pos+2]==WALL) or (self.board[x_pos-1,y_pos+2]==WALL) or (self.board[x_pos+1,y_pos+2]==WALL))
