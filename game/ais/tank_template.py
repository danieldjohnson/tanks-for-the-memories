# Notes on the restricted python environment:
# For security purposes, your code is run sandboxed. This means, among other things, that you
# can't have anything that starts with an underscore, and some imports are restricted.

# Coordinates are defined as follows:
#      -y
#       |
# -x ---+--- +x
#       |
#      +y

# Import useful game constants
import constants

class TankAI:

    def init(self,init_state):
        """
        init initializes the tank.
        init_state is a 2D array that represents the walls of the game board, where
          init_state[y][x] is the board object at x, y. It is one of

            constants.EMPTY        : an empty square
            constants.WALL         : a wall
            constants.HOSPITAL     : a hospital (staying here gains hp)

        """
        self.board = init_state

    def takeTurn(self,state):
        """
        takeTurn takes the following inputs, packed into a list called 'state', of form
          [tank_coords, hp, ammo, [x_pos, y_pos], aggressors]

              tank_coords : coordinates of all tanks on the board in format:
                                [[name_1, x_pos_1, y_pos_1],[name_2, x_pos_2, y_pos_2], ... ]
              hp          : tank's current health
              x_pos       : tank's x-coordinate [0-63]
              y_pos       : tank's y-coordinate [0-63]
              been_hit    : boolean variable describing whether the tank has been hit
              aggressors  : all tanks that have shot you in the past turn, in format:
                                [name1, name2, name3, ... ]

        takeTurn returns the following outputs, stored in a list of form:
          [x_vel, y_vel, tx, ty]

              x_vel, y_vel  : tank's velocity vector (capped at MAX_TANK_SPEED)
              tx, ty        : tank's turret vector (magnitude is ignored)
              shoot         : whether the tank should shoot (in the direction of its turret)
                                on the current turn

        """
        [tank_coords, hp, ammo, [x_pos, y_pos], aggressors] = state
        x_vel = 0 # movement direction
        y_vel = 0
        tx    = 0 # turret direction
        ty    = 0
        shoot = False
        return [[x_vel, y_vel], shoot, [tx, ty]]
