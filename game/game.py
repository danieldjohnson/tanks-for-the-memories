#
# A class to run our Tank Wars game
#
# MuddHacks 2015
#

import copy
from constants import *

class Game:

	def __init__(self, walls = []):
		""" if we want walls we give walls as a list of 2-element lists """
		self.walls = walls
		self.tanks = []
		self.bullets = []
		self.board = copy.deepcopy(self.walls)

	# UPDATING THINGS

	def real_time_update(dt):
		""" update positions, kill things, and ultimately run discrete turns """


		self.board = copy.deepcopy(self.walls)

		for t in tanks:

			# move the tank
			old_positions = t.get_pixel_pos() # <-- actually 4 points
			t.move(dt)
			positions = t.get_pixel_pos() 
			for p in positions:
				x = p[0]
				y = p[1]
				if (self.board[x][y] == WALL):
					

		for b in bullets:

			# move the bullet
			b.move(dt)
			pos = b.get_pixel_pos()
			x = pos[0]
			y = pos[1]
			
			# kill the bullet if it hits a wall
			if (self.board[x][y] == WALL):
				bullets.remove(b)
			else:
				self.board[x][y] = BULLET


	# DRAWING THINGS

	def draw_board():
		""" currently do nothing """

	def draw_bullet():
		""" currently do nothing """

	def draw_tank():
		""" currently do nothing """

