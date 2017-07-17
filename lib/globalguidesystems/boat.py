from boat_state import BoatState

class Boat:

	def __init__(self, boat_id, name, type_id, length, width, current_state):
		self.id_ = boat_id
		self.name_ = name
		self.type_id_ = type_id
		self.width_ = width
		self.length_ = length
		self.states_ = [current_state]

	def id(self):
		return self.id_

	def name(self):
		return self.name_

	def type_id(self):
		return self.type_id_

	def width(self):
		return self.width_

	def length(self):
		return self.length_
		
	def states(self):
		return self.states_

	def add_history(self, history):
		self.states_.extend(history)

	def __str__(self):
		string = "Id: " + str(self.id_) + ", Name: " + str(self.name_) + ", Type: " + str(self.type_id_) + ", Width: " + str(self.width_) + ", Length: " + str(self.length_) + ", States: "
		for state in self.states_:
			string = string + str(state) + ", "
		return string		

