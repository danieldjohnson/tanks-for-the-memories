#
# A class to run our Tank Wars game
#
# MuddHacks 2015
#

from constants import *

class Game:

	def __init__(self, walls = []):
		""" if we want walls we give walls as a list of 2-element lists """
		self.walls = walls
		self.tanks = []
		self.bullets = []
		self.board = []
		for i in range(64):
			self.board.append([EMPTY]*64) # if we get a bug later check deepcopying
		for pos in self.walls:
			x = pos[0]
			y = pos[1]
			self.board[x][y] = WALL

	# UPDATING THINGS

	def real_time_update(dt):
		""" update positions, kill things, and ultimately run discrete turns """

		for b in bullets:
			b.move(dt)

		for t in tanks:
			t.move(dt)


	# DRAWING THINGS

	def draw_board():
		for a in board:
			for b in a:
				print DEBUG_STRINGS[b],
			print "\n"
