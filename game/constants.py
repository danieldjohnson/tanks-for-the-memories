#
# Stores constants for our Tank Wars game
#
# MuddHacks 2015
#
DEBUG           = True
EMPTY           = 0
WALL            = 1
TANK            = 2
BULLET          = 3
HOSPITAL        = 4

MAX_TANK_SPEED  = 4 # <-- pixels/second
MAX_TANK_RADIUS = math.sqrt(2) # <-- cornerlength IF WE GET WEIRD BUGS CHECK THIS
BULLET_DM       = 1
BULLET_SPEED    = 15 # <-- pixels/second
HOSPITAL_RATE   = 1  # <-- hp/second
TURN_RATE       = 1  # <-- turns/second

DEBUG_STRINGS   = [" ","#","@","*","O"]
