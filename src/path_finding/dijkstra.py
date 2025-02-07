import pickle

import pandas as pd
from collections import defaultdict
import heapq
import networkx as nx
import os


# # Build the graph from the timetables CSV file
# def build_graph(timetables_path):
#     graph = defaultdict(dict)
#     timetables_df = pd.read_csv(timetables_path, sep='\t')
#
#     for _, row in timetables_df.iterrows():
#         try:
#             stations = row['trajet'].split(' - ')
#             duration = int(row['duree'])  # Ensure duration is an integer
#             if len(stations) == 2:
#                 source, destination = stations
#                 graph[source][destination] = duration
#                 graph[destination][source] = duration  # Assume bidirectional travel
#         except Exception as e:
#             print(f"Error processing row: {row}, {e}")
#
#     return dict(graph)
#
# # Map cities to their corresponding stations, ignoring case
# def map_cities_to_stations(stations_path):
#     city_to_stations = defaultdict(list)
#     stations_df = pd.read_excel(stations_path, engine='openpyxl')
#
#     for _, row in stations_df.iterrows():
#         city = row['COMMUNE'].strip().upper()  # Normalize to uppercase
#         station = row['LIBELLE'].strip()
#         city_to_stations[city].append(station)
#
#     return city_to_stations
#
# # Implement Dijkstra's algorithm to find the shortest path between two stations
# def dijkstra(graph, start, end):
#     if start not in graph or end not in graph:
#         return None, None  # Ensure stations exist in the graph
#
#     priority_queue = []
#     heapq.heappush(priority_queue, (0, start))
#
#     distances = {node: float('inf') for node in graph}
#     distances[start] = 0
#     previous_nodes = {node: None for node in graph}
#
#     while priority_queue:
#         current_distance, current_node = heapq.heappop(priority_queue)
#
#         if current_node == end:
#             break
#
#         for neighbor, weight in graph[current_node].items():
#             distance = current_distance + weight
#             if distance < distances[neighbor]:
#                 distances[neighbor] = distance
#                 previous_nodes[neighbor] = current_node
#                 heapq.heappush(priority_queue, (distance, neighbor))
#
#     path = []
#     current = end
#     while current is not None:
#         path.insert(0, current)
#         current = previous_nodes[current]
#
#     return path, distances[end] if distances[end] != float('inf') else None
#
# # Find the best stations in a city (all possible stations)
# def find_stations(city, city_to_stations):
#     city = city.strip().upper()  # Normalize input to uppercase
#     stations = city_to_stations.get(city, [])
#     if not stations:
#         raise ValueError(f"No stations found for city: {city}")
#     return stations  # Return all stations in the city
#
# # Function to execute the full path-finding process
# def run_path_finding(timetables_path, stations_path, start_city, end_city):
#     """
#     Runs the shortest path calculation from a start city to an end city.
#     """
#     print("Loading data...")
#
#     city_to_stations = map_cities_to_stations(stations_path)
#     graph = build_graph(timetables_path)
#
#     try:
#         start_stations = find_stations(start_city, city_to_stations)
#         end_stations = find_stations(end_city, city_to_stations)
#     except ValueError as e:
#         print(f"Error: {e}")
#         return
#
#     print(f"Possible departure stations: {start_stations}")
#     print(f"Possible arrival stations: {end_stations}")
#
#     # Try to find a direct connection
#     best_path = None
#     best_duration = float('inf')
#
#     for start_station in start_stations:
#         for end_station in end_stations:
#             shortest_path, total_duration = dijkstra(graph, start_station, end_station)
#
#             if shortest_path and total_duration is not None and total_duration < best_duration:
#                 best_path = shortest_path
#                 best_duration = total_duration
#
#     if best_path:
#         print(f"Shortest path: {' → '.join(best_path)}")
#         print(f"Total duration: {best_duration} minutes")
#     else:
#         print("No valid direct path found. Looking for alternative routes...")
#         find_alternative_route(graph, start_stations, end_stations)
#
# # Function to find an alternative route via a third station
# def find_alternative_route(graph, start_stations, end_stations):
#     """
#     If no direct route exists, this function attempts to find an alternative path
#     by introducing an intermediate station.
#     """
#     best_path = None
#     best_duration = float('inf')
#
#     for start_station in start_stations:
#         for intermediate in graph.keys():  # Test all possible intermediate stations
#             if intermediate in start_stations or intermediate in end_stations:
#                 continue  # Skip if it's already a start or end station
#
#             for end_station in end_stations:
#                 path1, duration1 = dijkstra(graph, start_station, intermediate)
#                 path2, duration2 = dijkstra(graph, intermediate, end_station)
#
#                 if path1 and path2 and duration1 is not None and duration2 is not None:
#                     total_duration = duration1 + duration2
#                     combined_path = path1[:-1] + path2  # Merge paths
#
#                     if total_duration < best_duration:
#                         best_duration = total_duration
#                         best_path = combined_path
#
#     if best_path:
#         print(f"Alternative path found: {' → '.join(best_path)}")
#         print(f"Total duration: {best_duration} minutes")
#     else:
#         print("No valid alternative route found.")

def load_and_merge_data():
    train_types = ["tgv", "ter", "intercites"]

    # Charger et concaténer les fichiers pour chaque type de train
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    raw_data_path = os.path.join(project_root, 'data', 'gares')

    stops = pd.concat([pd.read_csv(os.path.join(raw_data_path, train, "stops.csv")) for train in train_types]).drop_duplicates()
    stop_times = pd.concat([pd.read_csv(os.path.join(raw_data_path, train, "stop_times.csv")) for train in train_types]).drop_duplicates()
    trips = pd.concat([pd.read_csv(os.path.join(raw_data_path, train, "trips.csv")) for train in train_types]).drop_duplicates()
    routes = pd.concat([pd.read_csv(os.path.join(raw_data_path, train, "routes.csv")) for train in train_types]).drop_duplicates()
    calendar_dates = pd.concat([pd.read_csv(os.path.join(raw_data_path, train, "calendar_dates.csv")) for train in train_types]).drop_duplicates()

    commune_stations = pd.read_csv(os.path.join(raw_data_path, "liste-des-gares (3).csv"), sep=";")
    commune_stations["LIBELLE"] = commune_stations["LIBELLE"].str.replace("-", " ")

    # convertir les horaires en secondes
    def time_to_seconds(time_str):
        h, m, s = map(int, time_str.split(":"))
        return h * 3600 + m * 60 + s

    stop_times["arrival_time"] = stop_times["arrival_time"].apply(
        lambda x: time_to_seconds(x) if isinstance(x, str) else x)
    stop_times["departure_time"] = stop_times["departure_time"].apply(
        lambda x: time_to_seconds(x) if isinstance(x, str) else x)

    return stops, stop_times, trips, routes, calendar_dates, commune_stations


def build_graph(stops, stop_times, trips, routes):
    """Construit un graphe dirigé des trajets ferroviaires."""
    G = nx.DiGraph()

    # Ajouter les gares au graphe
    for _, row in stops.iterrows():
        G.add_node(row["stop_id"], name=row["stop_name"])

    # Trier les stop_times pour respecter l'ordre des trajets
    stop_times = stop_times.sort_values(by=["trip_id", "stop_sequence"])
    previous_stop = None

    for _, row in stop_times.iterrows():
        stop_id = row["stop_id"]
        trip_id = row["trip_id"]
        arrival_time = row["arrival_time"]
        departure_time = row["departure_time"]
        stop_sequence = row["stop_sequence"]

        if previous_stop and previous_stop["trip_id"] == trip_id:
            if previous_stop["stop_sequence"] < stop_sequence:
                travel_time = arrival_time - previous_stop["departure_time"]
                if travel_time > 0:
                    route_id = trips.loc[trips["trip_id"] == trip_id, "route_id"].values[0]
                    train_number = routes.loc[routes["route_id"] == route_id, "route_long_name"].values[0]
                    G.add_edge(previous_stop["stop_id"], stop_id, weight=travel_time, trip_id=trip_id, train_number=train_number, transfer=0)
        else:
            if previous_stop:
                route_id = trips.loc[trips["trip_id"] == trip_id, "route_id"].values[0]
                train_number = routes.loc[routes["route_id"] == route_id, "route_long_name"].values[0]
                G.add_edge(previous_stop["stop_id"], stop_id, weight=max(0, arrival_time - previous_stop["departure_time"]), trip_id=previous_stop["trip_id"], train_number="Correspondance : "+train_number, transfer=1)

        previous_stop = {
            "stop_id": stop_id,
            "trip_id": trip_id,
            "departure_time": departure_time,
            "stop_sequence": stop_sequence,
        }

    return G


def calculate_total_travel_time(G, path):
    """Calcule le temps total de trajet en tenant compte des correspondances."""
    total_time = 0
    correspondences = []
    previous_stop = None
    previous_trip = None

    for stop in path:
        if previous_stop:
            edge_data = G.get_edge_data(previous_stop, stop)
            travel_time = edge_data["weight"]
            trip_id = edge_data["trip_id"]

            # Vérifier s'il y a une correspondance (changement de train)
            if previous_trip and previous_trip != trip_id:
                correspondences.append(f"Correspondance : {previous_trip} → {trip_id}")
                total_time += 600  # Ajouter 10 minutes de correspondance

            total_time += travel_time
            previous_trip = trip_id

        previous_stop = stop

    return total_time, correspondences


def get_best_route(G, departure_id, arrival_id):
    """Trouve le trajet le plus rapide avec Dijkstra et affiche les détails du trajet."""
    try:
        # shortest_path = nx.shortest_path(G, source=departure_id, target=arrival_id, weight=lambda u, v, d: d["weight"] + (d["transfer"] * 600))
        # shortest_time = sum(G[u][v]["weight"] for u, v in zip(shortest_path[:-1], shortest_path[1:]))
        # shortest_time = nx.shortest_path_length(G, source=departure_id, target=arrival_id, weight="weight")
        shortest_path = nx.shortest_path(G, source=departure_id, target=arrival_id, weight="weight")
        total_time, correspondences = calculate_total_travel_time(G, shortest_path)

        # Convertir le temps total en HH:MM:SS
        hours, remainder = divmod(total_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_str = f"{hours:02}:{minutes:02}:{seconds:02}"

        # Récupérer les numéros de train et correspondances
        trip_details = []
        for i in range(len(shortest_path) - 1):
            stop_a = shortest_path[i]
            stop_b = shortest_path[i + 1]
            edge_data = G.get_edge_data(stop_a, stop_b)
            trip_id = edge_data.get("trip_id", "Inconnu")
            train_number = edge_data.get("train_number", "Train Inconnu")
            trip_details.append(f"{train_number}: {G.nodes[stop_a]['name']} → {G.nodes[stop_b]['name']}")

        return {
            "Itineraire": " → ".join([G.nodes[stop]["name"] for stop in shortest_path]),
            "Duree_totale": duration_str,
            "Correspondances": trip_details
        }
    except nx.NetworkXNoPath:
        return {"Erreur": "Aucun chemin trouvé."}


def get_stations_for_city(commune_stations, city_name, G):
    """Retourne les gares associées à une commune donnée en utilisant liste-des-gares.csv."""
    city_stations = commune_stations[commune_stations["COMMUNE"].str.lower() == city_name.lower()]
    # print(city_stations["LIBELLE"] + " | " + city_stations["COMMUNE"])
    # print("--------------")
    valid_stations = [stop_id for stop_name in city_stations["LIBELLE"] for stop_id, data in G.nodes(data=True) if stop_name.lower() in data["name"].lower()]
    # print(valid_stations)
    # print(valid_stations == [])
    if not valid_stations:
        # print("Ville non trouvée dans la liste des gares. Recherche par nom de commune.")
        valid_stations = [stop_id for stop_name in city_stations["COMMUNE"] for stop_id, data in G.nodes(data=True) if stop_name.lower() in data["name"].lower()]
        # print(valid_stations)
    return valid_stations if valid_stations else None


def get_fastest_route_for_city(G, commune_stations, departure_city, arrival_city):
    """Trouve le meilleur trajet parmi toutes les gares disponibles dans la ville."""
    departure_stations = get_stations_for_city(commune_stations, departure_city, G)
    arrival_stations = get_stations_for_city(commune_stations, arrival_city, G)

    if not departure_stations:
        return {"Erreur": f"Aucune gare trouvée pour {departure_city}"}
    if not arrival_stations:
        return {"Erreur": f"Aucune gare trouvée pour {arrival_city}"}

    best_route = None
    shortest_time = float("inf")

    for dep in departure_stations:
        for arr in arrival_stations:
            route = get_best_route(G, dep, arr)
            if "Duree_totale" in route:
                time_in_seconds = int(route["Duree_totale"][:2]) * 3600 + int(route["Duree_totale"][3:5]) * 60
                if time_in_seconds < shortest_time:
                    shortest_time = time_in_seconds
                    best_route = route

    return best_route if best_route else {"Erreur": "Aucun itinéraire trouvé."}

def save_graph(G, filename="train_graph.pkl"):
    """Sauvegarde le graphe dans un fichier pickle."""
    with open(filename, "wb") as f:
        pickle.dump(G, f)
    print(f"Graphe sauvegardé dans {filename}")

def load_graph(filename="train_graph.pkl"):
    """Charge un graphe depuis un fichier pickle."""
    with open(filename, "rb") as f:
        G = pickle.load(f)
    print(f"Graphe chargé depuis {filename}")
    return G

# Example execution
if __name__ == "__main__":
    graph_filename = os.path.join(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")), 'data', 'gares'), "train_graph.pkl")

    stops, stop_times, trips, routes, calendar_dates, commune_stations = load_and_merge_data()

    print("Building the graph...")
    if os.path.exists(graph_filename):
        G_all = load_graph(graph_filename)
    else:
        G_all = build_graph(stops, stop_times, trips, routes)
        save_graph(G_all, graph_filename)
    # G_all = build_graph(stops, stop_times, trips, routes)

    # Example: Find shortest path between two cities
    start_city = "briouze"  # Test with lowercase input
    end_city = "paris"

    print("Calculating fastest route...")
    result = get_fastest_route_for_city(G_all, commune_stations, start_city, end_city)
    print(result)
