from point import Point

class BoatState(Point):
	def __init__(self, easting, northing, direction, speed, timestamp):
		
		Point.__init__(self, easting, northing)

		self.direction_ = direction / 10.0
		self.speed_ = speed / 10.0
		self.timestamp_ = timestamp

	def direction(self):
		return self.direction_

	def speed(self):
		return self.speed_

	def __str__(self):
		return Point.__repr__(self)

	def __repr__(self):
		return Point.__repr__(self)
