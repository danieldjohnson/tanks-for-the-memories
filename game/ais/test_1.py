#sample AI

# coordinates are defined as follows:

#      -y
#       |
# -x ---+--- +x
#       |
#      +y

# do_turn takes the following inputs, packed into a list called 'state':

#   tank_coords : coordinates of all tanks on the board in format: {{name_1, x_pos_1, y_pos_1},{name_2, x_pos_2, y_pos_2}, ... }
#   hp          : tank's current health
#   x_pos       : tank's x-coordinate [0-63]
#   y_pos       : tank's y-coordinate [0-63]
#   been_hit    : boolean variable describing whether the tank has been hit
#   aggressors  : all tanks that have shot you in the past turn, in format: {name1, name2, name3, ... }

# do_turn returns the following outputs, stored in a list of form:
#   {x_vel, y_vel, tx, ty}

#   x_vel, y_vel  : tank's velocity vector
#   tx, ty        : tank's turret vector
#   shoot         : whether the tank should shoot (in the direction of its turret) on the current turn

def do_turn (state):
    [tank_coords, hp, ammo, [x_pos, y_pos], aggressors] = state
    x_vel = 0 # movement direction
    y_vel = 0
    tx    = 0 # turret direction
    ty    = 0
    shoot = False
    return [[x_vel, y_vel], shoot, [tx, ty]]
