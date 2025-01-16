import pickle
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import networkx as nx
from django.http import JsonResponse

with open("/app/Routes_Finder/cheaper_route/directed_graph.pkl", "rb") as f:
    graph = pickle.load(f)

geolocator = Nominatim(user_agent="route_api")

VEHICLE_RANGE = 500 
FUEL_EFFICIENCY = 10


def find_cheapest_route(request):
    start_location = int(request.GET.get("start"))
    finish_location = int(request.GET.get("finish"))

    if not start_location or not finish_location:
        return JsonResponse({"error": "Start and finish locations are required as query parameters."}, status=400)

    try:    
        path = nx.shortest_path(graph, source=start_location, target=finish_location, weight="weight")
        total_cost = calculate_total_cost(path)
        route_details = [
            {
                "truckstop_id": node,
                "coordinates": graph.nodes[node]["coordinates"],
                "fuel_cost": graph.nodes[node]["fuel_cost"]
            }
            for node in path
        ]
        return JsonResponse({
            "route": route_details,
            "total_cost": total_cost,
            "start_coordinates": graph.nodes[start_location]["coordinates"],
            "finish_coordinates": graph.nodes[finish_location]["coordinates"]
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def calculate_total_cost(path):
    total_cost = 0

    for i in range(len(path) - 1):
        node1 = path[i]
        node2 = path[i + 1]
        distance = graph[node1][node2]["distance"]
        fuel_cost_per_mile = graph.nodes[node2]["fuel_cost"] / FUEL_EFFICIENCY
        total_cost += distance * fuel_cost_per_mile

    return round(total_cost, 2)