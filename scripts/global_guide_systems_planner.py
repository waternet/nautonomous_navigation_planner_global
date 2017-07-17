
import sys
import os

import math

import rospy

import datetime

from boat_state import BoatState

from globalguidesystems import API

import astar_route
import graph_helper

import vaarkaart_loader

import matplotlib.pyplot as plt
import networkx as nx

class GlobalGuideSystemsPlanner:

    def __init__(self, routing_graph):
	self.vaarkaart_graph = routing_graph


    def path_regression(self):
        api = API()
        boats = api.requested_objects_history_request(30, ['244750262'])

        #find closest vaarkaart edge
        edge_clusters = self.find_closest_vaarkaart_edge(boats)
            
        #separate cluster into two sets based on direction/speed K-means
        first_direction_cluster, second_direction_cluster = self.vaarkaart_edge_to_path_cluster(edge_clusters)
        
        #Least Squares per set
        least_squares_paths = self.path_cluster_least_squares(first_direction_cluster, second_direction_cluster)

    def find_closest_vaarkaart_edge(self, boats):
        edge_clusters = {}


        for boat in boats:

            last_edge = None

            for boat_state in boat.states():

                # Only add boat states that have a valid speed
                if boat_state.speed() < 5.0:
                    continue

                # Find closest vaarkaart edge
                closest_edge, closest_distance = graph_helper.closest_edge(self.vaarkaart_graph, boat_state, last_edge)

                if closest_edge is None:
                    continue

                #if closest_edge.id() is not 101:
                #    continue

                # Create cluster per vaarkaart edge
                key = closest_edge.id()
                if key not in edge_clusters:
                    edge_clusters[key] = [boat_state]
                else:
                    edge_clusters[key].append(boat_state)

                last_edge = closest_edge
           
        print edge_clusters

        return edge_clusters

    def vaarkaart_edge_to_path_cluster(self, edge_clusters):
        direction_clusters = []

        # Prepare separate clusters
        first_directional_cluster = {}
        second_directional_cluster = {}

        for cluster_key in edge_clusters:

            # Separate cluster K-means
            sum_theta = 0
            for boat_state in edge_clusters[cluster_key]:
                sum_theta += boat_state.direction()

            n_elements = len(edge_clusters[cluster_key])
            average_theta = sum_theta / n_elements
            

            projected_edge = self.vaarkaart_graph.edge(cluster_key)
            start_vertex = self.vaarkaart_graph.vertex(projected_edge.start_vertex_str())
            destination_vertex = self.vaarkaart_graph.vertex(projected_edge.destination_vertex_str())

            edge_theta = math.degrees((start_vertex - destination_vertex).theta())
            if edge_theta < 0:
                edge_theta += 360

            first_bound_theta = 0 
            second_bound_theta = 0

            
            if edge_theta > 90 and edge_theta < 270:
                first_bound_theta = edge_theta - 90
                second_bound_theta = edge_theta + 90
            elif edge_theta < 90:
                first_bound_theta = edge_theta
                second_bound_theta = edge_theta + 180
            elif edge_theta > 270:
                first_bound_theta = edge_theta - 180
                second_bound_theta = edge_theta

            # Append separate clusters
            for boat_state in edge_clusters[cluster_key]:
                if projected_edge.metadata().directionality() == 1:
                    if cluster_key not in first_directional_cluster:
                        first_directional_cluster[cluster_key] = [boat_state]
                    else:
                        first_directional_cluster[cluster_key].append(boat_state)
                elif projected_edge.metadata().directionality() == 1:
                    if cluster_key not in second_directional_cluster:
                        second_directional_cluster[cluster_key] = [boat_state]
                    else:
                        second_directional_cluster[cluster_key].append(boat_state)
                elif boat_state.direction() >= first_bound_theta and boat_state.direction() < second_bound_theta:
                    if cluster_key not in first_directional_cluster:
                        first_directional_cluster[cluster_key] = [boat_state]
                    else:
                        first_directional_cluster[cluster_key].append(boat_state)
                else:
                    if cluster_key not in second_directional_cluster:
                        second_directional_cluster[cluster_key] = [boat_state]
                    else:
                        second_directional_cluster[cluster_key].append(boat_state)
        
        return first_directional_cluster, second_directional_cluster

    def path_cluster_least_squares(self, first_direction_cluster, second_directional_cluster):
        least_squares_paths = []

        # Create a visualization graph using nx.
        visualization_graph_red = nx.Graph()

        # Creates the nodes from the waternet graph
        for cluster_key in first_direction_cluster:
            for boat_state in first_direction_cluster[cluster_key]:
                visualization_graph_red.add_node(str(boat_state), pos = (boat_state.x(), boat_state.y()))

        pos_red = nx.get_node_attributes(visualization_graph_red, 'pos')
        nx.draw_networkx_nodes(visualization_graph_red, pos = pos_red, node_color = 'r', node_size = 15)


        visualization_graph_green = nx.Graph()

        for cluster_key in second_directional_cluster:
            for boat_state in second_directional_cluster[cluster_key]:
                visualization_graph_green.add_node(str(boat_state), pos = (boat_state.x(), boat_state.y()))
        
        pos_green = nx.get_node_attributes(visualization_graph_green, 'pos')
        nx.draw_networkx_nodes(visualization_graph_green, pos = pos_green, node_color = 'g', node_size = 15)
        
        # Create a visualization graph using nx.
        visualization_graph = nx.Graph()

        # Creates the nodes from the waternet graph
        for vertex in self.vaarkaart_graph.vertices():
            visualization_graph.add_node(str(vertex), pos = (vertex.x(), vertex.y()))

        # Creates the edges from the waternet graph
        for edge in self.vaarkaart_graph.edges():
            visualization_graph.add_edge(edge.start_vertex_str(), edge.destination_vertex_str())    
        
        # Prepare the graph
        pos = nx.get_node_attributes(visualization_graph, 'pos')

        # Draw the graph
        nx.draw_networkx_nodes(visualization_graph, pos = pos, node_color = 'b', node_size = 30)
        nx.draw_networkx_edges(visualization_graph, pos = pos)

        plt.show()
        #for direction_cluster in direction_clusters:
            #Linear regression
            
        return least_squares_paths

def is_close(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)