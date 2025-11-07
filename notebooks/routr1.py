import geopandas
import osmnx as ox
import networkx as nx
import numpy as np
import heapq as hq
import streamlit as st
import folium 
import streamlit_folium as sf


def city_collector():
    location = str(input("Enter your City and State:"))
    if ',' in location:
        location_list = location.split(sep = ',')
        return location_list[0], location_list[1].lstrip(' ')
    else:
        location_list = location.split(sep = ' ')
        return location_list[0], location_list[1]

class CyclewayGraph:
    
    def __init__(self, city, state, route_pref = 'bike-focused'):
        self.id = f"{city}, {state}"

        self.city = city
        self.state = state

        self.route_pref = route_pref

        self.graph = ox.graph_from_place(query = self.id, network_type= 'bike')

        self.nodes = self.graph.nodes

        # cycleway_edges_unsort = self.bike_gdf_edges.loc[self.bike_gdf_edges.loc[:,'highway']=='cycleway']

        # self.graph = bike_data

        

    def create_path_list(self, start_node, end_node, previous_nodes, node_distances, path_distance = False):
        """Uses the get_shortest_path function's inputs & outputs of previous_nodes & node_distances to return a list of the nodes to be traversed.
            Has the option of including the distances for each edge to traverse if specified.  

        Args:
            start_node (int): the beginning node to navigate from.
            end_node (int): the end node destination desired.
            previous_nodes (dict): a dictionary of nodes and the node to travel from along the shorest path to each node.
            node_distances (dict): a dictionary of each node and the shortest distance required to reach each node.
            path_distance (bool, optional): if True will provide a separate list the distance of each edge traversed. Defaults to False.

        Returns:
            list: a list of shortest path of nodes that should be traversed, in order from start to finish.
        """

        shortest_path = list()
        shortest_path_dists = list()
        closest_node = end_node

        if path_distance == True:
            total_path_length = node_distances[closest_node]
            while previous_nodes[closest_node]:
                shortest_path.append(closest_node)
                
                edge_end_dist = node_distances[closest_node] #cumulative distance along the path to the END of the edge
                edge_start_dist = node_distances[previous_nodes[closest_node]] #cumulative distance along the path to the START of the edge, gathered once reassigned
                current_edge_length = edge_end_dist - edge_start_dist
                shortest_path_dists.append(current_edge_length)
                if previous_nodes[closest_node] == start_node:
                    shortest_path.append(start_node)
                    return shortest_path[::-1], shortest_path_dists[::-1]
            
                closest_node = previous_nodes[closest_node]
                        
        else:
            while previous_nodes[closest_node]:
                shortest_path.append(closest_node)
                if previous_nodes[closest_node] == start_node:
                    shortest_path.append(start_node)
                    return shortest_path[::-1]
                
                closest_node = previous_nodes[closest_node]

    def edge_calculator(self, edge_data, preference):
        """Uses nested if statements with multipliers to weight the user's route towards their path preferences  

        Args:
            edge_data (dict): The edge dictionary accessed by indexing the edge's start node, end node, and edge index to the graph.
            preference (str): One of the available routing preferences selectable ("safest", "bike-focused", or "quickest").

        Returns:
            np.float64: the weighted edge length based off of the user's preferences.
        """ 
        
        highway_type = edge_data['highway']
        edge_length = edge_data['length']

        #Would converting the lists to sets be faster? probably unnecessary...

        if preference == 'safest':
            if 'cycleway' in highway_type or 'path' in highway_type:
                weighted_length = edge_length * 0.7
                return weighted_length
            
            elif ('residential' in highway_type) or ('service' in highway_type) or (('track') in highway_type):
                weighted_length = edge_length * 0.85
                return weighted_length
            
            else:
                weighted_length = edge_length * 1.2
                return weighted_length
            
        elif preference == 'bike-focused':
            if 'cycleway' in highway_type or 'path' in highway_type:
                weighted_length = edge_length * 0.8
                return weighted_length
            
            elif ('residential' in highway_type) or ('service' in highway_type) or (('track') in highway_type):
                weighted_length = edge_length * 0.9
                return weighted_length
            
            else:
                weighted_length = edge_length * 1.1
                return weighted_length
            
        else:
            # shortest/default option
            return edge_length


    def find_shortest_path_queue(self, start_node, end_node, path_distance = False, override_pref = False):
        """This function implements a priority queue, using heapq, to find the shortest path between two nodes in a NetworkX MultiDiGraph.

        Args:
            start_node (int): the beginning node to navigate from.
            end_node (int): the end node destination desired.
            path_distance (bool, optional): If True will provide a separate list the distance of each edge traversed. Defaults to False.

        Returns:
            list: a list of shortest path of nodes that should be traversed, in order from start to finish.
        """
        
        node_distances = {node : float('inf') for node in list(self.nodes)}
        node_distances[start_node] = 0
        previous_nodes = dict()
        shortest_path = list()
        shortest_path_dists = list() #length will be different, because it returns the distance per edge, while shortest_path is a list of all nodes

        unvisited_nodes = [(value, node) for node, value in node_distances.items()]
        hq.heapify(unvisited_nodes)

        while len(unvisited_nodes) != 0:
            closest_node_dist, closest_node = hq.heappop(unvisited_nodes)

            if closest_node == end_node:
                return self.create_path_list(start_node, end_node, previous_nodes, node_distances, path_distance)

            for neighbor_node in self.graph[closest_node]: #This index provides the adjacent nodes to the current closest node

                edge_option = min(self.graph[closest_node][neighbor_node], key = lambda edge_id: self.graph[closest_node][neighbor_node].get(edge_id)['length'] )
                
                edge_data = self.graph[closest_node][neighbor_node][edge_option]

                # edge_length = self.graph[closest_node][neighbor_node][edge_option]['length'] #NEED TO LOOK AT EACH EDGE WITHIN THE PREVIOUS NODES, currently assuming 0
                if override_pref:
                    edge_length = self.edge_calculator(edge_data, preference = override_pref) 
                else:
                    edge_length = self.edge_calculator(edge_data, preference = self.route_pref)
                
                alt_path_length = closest_node_dist + edge_length

                if node_distances[neighbor_node] == alt_path_length:
                    continue

                if node_distances[neighbor_node] > alt_path_length:
                    node_distances[neighbor_node] = alt_path_length
                    previous_nodes[neighbor_node] = closest_node
                    hq.heappush(unvisited_nodes, (alt_path_length, neighbor_node))


city, state = city_collector()


msn_bike_graph = CyclewayGraph(city,state)