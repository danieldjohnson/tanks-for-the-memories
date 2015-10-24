#
# Stores constants for our Tank Wars game
#
# MuddHacks 2015
#
import math

DEBUG           = True
TANK_COLORS     = []
# first 10 codes are devoted to 10 possible tanks
EMPTY           = 10
WALL            = 11
HOSPITAL        = 12
BULLET          = 13
AMMO            = 14
EYE             = 15

MAX_TANK_SPEED  = 4    # <-- pixels/second
MAX_TANK_RADIUS = 2    # <-- cornerlength IF WE GET WEIRD BUGS CHECK THIS
MAX_TANK_HP     = 30
BULLET_DM       = 1
BULLET_SPEED    = 15   # <-- pixels/second
HOSPITAL_RATE   = 0.1  # <-- hp/second
TURN_RATE       = 1    # <-- turns/second

DEBUG_STRINGS   = ["@","@","@","@","@","@","@","@","@","@"," ","#","H","*","A","o"]