#
# A class to run our Tank Wars game
#
# MuddHacks 2015
#


class Game:

	def __init__(self, walls = []):
		""" if we want walls we give walls as a list of 2-element lists """
		self.walls = walls
		self.tanks = []
		self.bullets = []

	# UPDATING THINGS

	def real_time_update(dt):
		""" update positions, kill things, and ultimately run discrete turns """

	# DRAWING THINGS

	def draw_board():
		""" currently do nothing """

	def draw_bullet():
		""" currently do nothing """

	def draw_tank():
		""" currently do nothing """
