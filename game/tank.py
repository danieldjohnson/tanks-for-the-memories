#
# A class to represent one Tank in our Tank Wars Game
#
# MuddHacks 2015
#


class Tank:

	def __init__(self, x_pos, y_pos, x_vel = 0,
									 y_vel = 0,
		 							 hp = 30,
		                             ammo = 100):

		self.x_pos = x_pos
		self.y_pos = y_pos
		self.x_vel = x_vel
		self.y_vel = y_vel
		self.hp = hp
		self.ammo = ammo

	def move(dt):
		""" updates the position of the tank"""
		self.x_pos += x_vel*dt
		self.y_pos += y_vel*dt

	
