from mapParse import MapParse
from graph import Graph
from pathfinder import Pathfinder
from simulation import Simulation
from models import Zone, Connection, ParseError
import sys


def build_graph(
        zones: dict[str, Zone],
        connections: list[Connection]
        ) -> Graph:
    """Create a Graph from the parsed zones and connections."""
    graph = Graph()
    for zone in zones.values():
        graph.add_zone(zone)
    for conn in connections:
        graph.add_connection(conn.zone_a, conn.zone_b)
    return graph


def main() -> None:
    """Entry point — usage: python main.py <map_file>"""
    if len(sys.argv) < 2:
        print("Usage: python main.py <map_file>")
        return

    map_file: str = sys.argv[1]

    try:
        parser = MapParse(map_file)
        nb_drones, zones, start, end, connections = parser.parse()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    if nb_drones <= 0:
        print("Error: Invalid number of drones (must be > 0).")
        sys.exit(1)
    if start is None:
        print("Parse error: missing start_hub definition.")
        sys.exit(1)
    if end is None:
        print("Parse error: missing end_hub definition.")
        sys.exit(1)
    if not connections or not zones:
        print("Parse error: missing connection or hub definition.")
        sys.exit(1)
    try:
        graph = build_graph(zones, connections)
        pathfinder = Pathfinder(graph)
        all_paths = pathfinder.find_all_paths(start, end)

        if not all_paths:
            print("No path found.")
            sys.exit(1)

        best_paths = all_paths[:min(2, len(all_paths))]

        drone_paths = [
            best_paths[i % len(best_paths)]
            for i in range(nb_drones)
        ]

        sim = Simulation(graph, drone_paths, nb_drones, connections)
        turns = sim.run()
    except (ParseError, Exception) as e:
        print(f"Error: {e}")
        sys.exit(1)
    print(f"\nTotal turns: {turns}")


if __name__ == "__main__":
    main()
