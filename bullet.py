#
# A class to represent one Bullet in our Tank Wars Game
#
# MuddHacks 2015
#


class Bullet:

	def __init__(self, x_pos, y_pos, x_vel, y_vel):

		self.x_pos = x_pos
		self.y_pos = y_pos
		self.x_vel = x_vel
		self.y_vel = y_vel

	def move(dt):
		""" updates the position of the bullet """
		self.x_pos += x_vel*dt
		self.y_pos += y_vel*dt

	
