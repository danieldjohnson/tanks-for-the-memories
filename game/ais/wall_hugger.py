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

        N = self.get_N(x_pos,y_pos)
        E = self.get_E(x_pos,y_pos)
        W = self.get_W(x_pos,y_pos)
        S = self.get_S(x_pos,y_pos)

        if self.state == "begin":
            if not N:
                return self.get_return(self.go_north,tank_coords,x_pos,y_pos)
            else:
                self.state = "east"
                return self.get_return(self.no_move,tank_coords,x_pos,y_pos)
        elif self.state == "north":
            if not W:
                self.state = "west"
                return self.get_return(self.go_west,tank_coords,x_pos,y_pos)
            elif not N:
                return self.get_return(self.go_north,tank_coords,x_pos,y_pos)
            elif not E:
                self.state = "east"
                return self.get_return(self.go_east,tank_coords,x_pos,y_pos)
            else:
                self.state = "south"
                return self.get_return(self.go_south,tank_coords,x_pos,y_pos)

        elif self.state == "east":
            if not N:
                self.state = "north"
                return self.get_return(self.go_north,tank_coords,x_pos,y_pos)
            elif not E:
                return self.get_return(self.go_east,tank_coords,x_pos,y_pos)
            elif not S:
                self.state = "south"
                return self.get_return(self.go_south,tank_coords,x_pos,y_pos)
            else:
                self.state = "west"
                return self.get_return(self.go_west,tank_coords,x_pos,y_pos)
        elif self.state == "west":
            if not S:
                self.state = "south"
                return self.get_return(self.go_south,tank_coords,x_pos,y_pos)
            elif not W:
                return self.get_return(self.go_west,tank_coords,x_pos,y_pos)
            elif not N:
                self.state = "north"
                return self.get_return(self.go_north,tank_coords,x_pos,y_pos)
            else:
                self.state = "east"
                return self.get_return(self.go_east,tank_coords,x_pos,y_pos)
        elif self.state == "south":
            if not E:
                self.state = "east"
                return self.get_return(self.go_east,tank_coords)            
            elif not S:
                return self.get_return(self.go_south,tank_coords,x_pos,y_pos)
            elif not W:
                self.state = "west"
                return self.get_return(self.go_west,tank_coords)            
            else:
                self.state = "north"
                return self.get_return(self.go_north,tank_coords,x_pos,y_pos)
        else:
            return self.get_return(self.no_move,tank_coords,x_pos,y_pos)

    def get_return(self,dir,tank_coords,x_pos,y_pos):
        x_dir = tank_coords[0][1] - x_pos
        y_dir = tank_coords[0][2] - y_pos
        return [dir,True,[x_dir,y_dir]]

    def get_N(self,x_pos,y_pos):
        if ((self.board[y_pos-2][x_pos]==WALL) or (self.board[x_pos-1][y_pos-2]==WALL) or (self.board[y_pos-2][x_pos+1]==WALL)):
            return True
        else:
            return False

    def get_E(self,x_pos,y_pos):
        if ((self.board[y_pos][x_pos+2]==WALL) or (self.board[y_pos-1][x_pos+2]==WALL) or (self.board[y_pos+1][x_pos+2]==WALL)):
            return True
        else:
            return False

    def get_W(self,x_pos,y_pos):
        if ((self.board[y_pos][x_pos-2]==WALL) or (self.board[y_pos-1][x_pos-2]==WALL) or (self.board[y_pos+1][x_pos-2]==WALL)):
            return True
        else:
            return False

    def get_S(self,x_pos,y_pos):
        if ((self.board[y_pos+2][x_pos]==WALL) or (self.board[y_pos+2][x_pos-1]==WALL) or (self.board[y_pos+2][x_pos+1]==WALL)):
            return True
        else:
            return False


