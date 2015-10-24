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

		self.recently_damaged = false
		self.damage_dirs = []

	def move(dt):
		""" updates the position of the tank"""
		self.x_pos += x_vel*dt
		self.y_pos += y_vel*dt

	def get_pixel_pos():
		""" returns a list of points """
		top = int(self.y_pos)
		bottom = int(self.y_pos + 1)
		left = int(self.x_pos)
		right = int(self.x_pos + 1)

		upper_left  = [int(self.x_pos)  , int(self.y_pos)  ]
		upper_right = [int(self.x_pos+1), int(self.y_pos)  ]
		lower_left  = [int(self.x_pos)  , int(self.y_pos+1)]
		lower_right = [int(self.x_pos+1), int(self.y_pos+1)]

		return [upper_left,upper_right,lower_left,lower_right]

	
