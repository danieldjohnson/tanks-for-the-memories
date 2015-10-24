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

		for t in tanks:

			# move the tank
			t.move(dt)

			# check to see if the tank hits a wall
			positions = t.get_pixel_pos() # <-- actually 9 points
			for p in positions:
				x = p[0]
				y = p[1]
				if (self.board[x][y] == WALL):
					t.move(-1.0*dt)
					break

			# update the pixels on the board
			positions = t.get_pixel_pos() # <-- actually 9 points
			for p in positions:
				x = p[0]
				y = p[1]
				if (self.board[x][y] == BULLET):
					for b in bullets:
						b_pos = b.get_pixel_pos()
						b_x = b_pos[0]
						b_y = b_pos[1]

						if (x==b_x) and (y==b_y):
							t.
				self.board[x][y] = TANK




	# DRAWING THINGS

	def draw_board():
<<<<<<< HEAD
		for a in board:
			for b in a:
				print DEBUG_STRINGS[b],
			print "\n"
=======
		""" currently do nothing """

	def draw_bullet():
		""" currently do nothing """

	def draw_tank():
		""" currently do nothing """

>>>>>>> origin/master
