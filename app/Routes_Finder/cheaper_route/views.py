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
    """
    Finds the cheapest route between the start and finish locations.
    Expects 'start' and 'finish' as query parameters (e.g., ?start=City,State&finish=City,State).
    """
    start_location = request.GET.get("start")
    finish_location = request.GET.get("finish")

    if not start_location or not finish_location:
        return JsonResponse({"error": "Start and finish locations are required as query parameters."}, status=400)

    try:
        start_coords = geolocator.geocode(start_location)
        finish_coords = geolocator.geocode(finish_location)
        start_coords = (start_coords.latitude, start_coords.longitude)
        finish_coords = (finish_coords.latitude, finish_coords.longitude)
        start_node = find_closest_truckstop(start_coords)
        finish_node = find_closest_truckstop(finish_coords)

        path = nx.shortest_path(graph, source=start_node, target=finish_node, weight="weight")
        total_cost = calculate_total_cost(path)

        # Prepare response with details
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
            "start_coordinates": start_coords,
            "finish_coordinates": finish_coords
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def find_closest_truckstop(coords):
    """
    Finds the closest truck stop in the graph to the given coordinates.
    """
    closest_node = None
    min_distance = float("inf")

    for node in graph.nodes:
        truckstop_coords = graph.nodes[node]["coordinates"]
        distance = geodesic(coords, truckstop_coords).miles
        if distance < min_distance:
            min_distance = distance
            closest_node = node

    return closest_node


def calculate_total_cost(path):
    """
    Calculates the total fuel cost for the given path.
    """
    total_cost = 0

    for i in range(len(path) - 1):
        node1 = path[i]
        node2 = path[i + 1]
        distance = graph[node1][node2]["distance"]
        fuel_cost_per_mile = graph.nodes[node2]["fuel_cost"] / FUEL_EFFICIENCY
        total_cost += distance * fuel_cost_per_mile

    return round(total_cost, 2)
