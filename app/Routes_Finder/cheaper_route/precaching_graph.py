import pandas as pd
import networkx as nx
from geopy.distance import geodesic
import pickle

FUEL_PRICES = pd.read_csv("/app/Routes_Finder/cheaper_route/fuel-prices-for-be-assessment.csv")
graph = nx.DiGraph()
MAX_DISTANCE = 500
FUEL_EFFICIENCY = 10 

def build_graph(df):
    # Add nodes to the graph
    for index, row in df.iterrows():
        truckstop_id = row['OPIS Truckstop ID']
        coords = (row['Latitude'], row['Longitude'])
        fuel_cost = row['Retail Price']
        graph.add_node(truckstop_id, coordinates=coords, fuel_cost=fuel_cost)
    
    # Add 2 edges with different directions between every 2 nodes with distance no more than the maximum allowed distance
    counter = 0
    for i, node1 in enumerate(graph.nodes):
        coords1 = graph.nodes[node1]['coordinates']
        fuel_cost_1 = graph.nodes[node1]['fuel_cost']
        
        for j, node2 in enumerate(list(graph.nodes)[i + 1:], start=i + 1):  # Start from the next index to avoid redundant checks
            coords2 = graph.nodes[node2]['coordinates']
            fuel_cost_2 = graph.nodes[node2]['fuel_cost']
            
            # Calculate distance only once for this pair
            distance = geodesic(coords1, coords2).miles
            if distance < MAX_DISTANCE:
                graph.add_edge(node1, node2, weight=(distance/FUEL_EFFICIENCY)*fuel_cost_2, distance=distance)
                graph.add_edge(node2, node1, weight=(distance/FUEL_EFFICIENCY)*fuel_cost_1, distance=distance)

        counter += 1
        print("Processed", counter, "nodes")

build_graph(FUEL_PRICES)
with open("/app/Routes_Finder/cheaper_route/directed_graph.pkl", "wb") as f:
    pickle.dump(graph, f)
print(f"Directed graph created with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges.")