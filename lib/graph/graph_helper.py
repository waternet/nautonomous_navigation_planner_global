
# Get the closest edge using point to line projection.
def closest_edge(waternet_graph, boat_position, last_edge):

	if last_edge is not None:
		total_distance = distance_to_edge(waternet_graph, boat_position, last_edge)
		if total_distance is not None:
			return last_edge, total_distance

	# Variables to keep track of the closest edge and its distance.
	closest_edge = None
	closest_distance = float("inf")

	for current_edge in waternet_graph.edges():
		total_distance = distance_to_edge(waternet_graph, boat_position, current_edge)

		if total_distance is None:
			continue
			
		# Set the closest edge and distance if the total distance is smaller than the current closest distance.
		if(total_distance < closest_distance):
			closest_edge = current_edge
			closest_distance = total_distance

	return closest_edge, closest_distance

def distance_to_edge(waternet_graph, boat_position, current_edge):
	# Get the easting and northing of the utm coordinate from the lat-lon position
	start_point = waternet_graph.vertex(current_edge.start_vertex_str()).point()
	destination_point = waternet_graph.vertex(current_edge.destination_vertex_str()).point()

	# Transposed coordinate of the route direction of the edge
	route_point = start_point - destination_point

	# Transposed coordinate of the goal location of the boat
	boat_point = boat_position - destination_point
	boat_point = boat_position - destination_point
	
	# Calculate the quotient for the projection (y dot u) / (u dot u)
	top_quotient_projection = boat_point.cross_product(route_point)
	bottom_quotient_projection = route_point.cross_product(route_point)

	# When the constraint of the projection is not onto the line, adjust the calculation.
	if top_quotient_projection < 0:
		# the point is projected under the line
		return None

	elif top_quotient_projection > bottom_quotient_projection:
		# the point is projected above the line
		return None

	# Calculate the quotient of the projection
	#quotient_projection = (top_quotient_projection / bottom_quotient_projection)

	# Project u to get projected y
	#projected_point = route_point.scale(quotient_projection)

	# The total distance is the distance from the boat_position to the destination point.
	return boat_point.length() 