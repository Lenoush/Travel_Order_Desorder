import pickle
import pandas as pd
import heapq
import networkx as nx
import os


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
    graphique = nx.DiGraph()

    # Ajouter les gares au graphe
    for _, row in stops.iterrows():
        graphique.add_node(row["stop_id"], name=row["stop_name"])

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
                    graphique.add_edge(previous_stop["stop_id"], stop_id, weight=travel_time, trip_id=trip_id, train_number=train_number, transfer=0)
        else:
            if previous_stop:
                route_id = trips.loc[trips["trip_id"] == trip_id, "route_id"].values[0]
                train_number = routes.loc[routes["route_id"] == route_id, "route_long_name"].values[0]
                graphique.add_edge(previous_stop["stop_id"], stop_id, weight=max(0, arrival_time - previous_stop["departure_time"]), trip_id=previous_stop["trip_id"], train_number="Correspondance : "+train_number, transfer=1)

        previous_stop = {
            "stop_id": stop_id,
            "trip_id": trip_id,
            "departure_time": departure_time,
            "stop_sequence": stop_sequence,
        }

    return graphique


def calculate_total_travel_time(G, path):
    """Calcule le temps total de trajet en tenant compte des correspondances."""
    total_time = 0
    previous_stop = None
    previous_trip = None

    for stop in path:
        if previous_stop:
            edge_data = G.get_edge_data(previous_stop, stop)
            travel_time = edge_data["weight"]
            trip_id = edge_data["trip_id"]

            # Vérifier s'il y a une correspondance (changement de train)
            if previous_trip and previous_trip != trip_id:
                total_time += 600  # Ajouter 10 minutes de correspondance

            total_time += travel_time
            previous_trip = trip_id

        previous_stop = stop

    return total_time


def get_best_route(G, departure_id, arrival_id):
    """Trouve le trajet le plus rapide avec Dijkstra et affiche les détails du trajet."""
    try:
        shortest_path = nx.shortest_path(G, source=departure_id, target=arrival_id, weight="weight")
        total_time = calculate_total_travel_time(G, shortest_path)

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
            train_number = edge_data.get("train_number", "Train Inconnu")
            trip_details.append(f"{train_number}: {G.nodes[stop_a]['name']} → {G.nodes[stop_b]['name']}")

        return {
            "Itineraire": " → ".join([G.nodes[stop]["name"] for stop in shortest_path]),
            "Duree_totale": duration_str,
            "Correspondances": trip_details
        }
    except nx.NetworkXNoPath:
        return None


def get_stations_for_city(commune_stations, city_name, G):
    """Retourne les gares associées à une commune donnée en utilisant liste-des-gares.csv."""
    city_stations = commune_stations[commune_stations["COMMUNE"].str.lower() == city_name.lower()]
    valid_stations = [stop_id for stop_name in city_stations["LIBELLE"] for stop_id, data in G.nodes(data=True) if stop_name.lower() in data["name"].lower()]
    if not valid_stations:
        valid_stations = [stop_id for stop_name in city_stations["COMMUNE"] for stop_id, data in G.nodes(data=True) if stop_name.lower() in data["name"].lower()]
    return valid_stations if valid_stations else None


def get_fastest_route_for_city(G, commune_stations, departure_city, arrival_city):
    """Trouve le meilleur trajet parmi toutes les gares disponibles dans la ville."""
    departure_stations = get_stations_for_city(commune_stations, departure_city, G)
    arrival_stations = get_stations_for_city(commune_stations, arrival_city, G)

    best_route = None
    error = None
    shortest_time = float("inf")

    if not departure_stations or not arrival_stations:
        error = f"Aucune gare trouvée pour {departure_city if not departure_stations else arrival_city}"
        return best_route, error

    for dep in departure_stations:
        for arr in arrival_stations:
            route = get_best_route(G, dep, arr)
            if route:
                time_in_seconds = int(route["Duree_totale"][:2]) * 3600 + int(route["Duree_totale"][3:5]) * 60
                if time_in_seconds < shortest_time:
                    shortest_time = time_in_seconds
                    best_route = route

    if not best_route:
        error = "Aucun trajet trouvé."

    return best_route, error

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
