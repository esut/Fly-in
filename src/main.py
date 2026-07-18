from src.parser import parse_map
from src.simulation import Simulation
from src.models import Drone
from src.visualizer import print_turn
from parser import Parse ,ParseError

def main() -> None:
    """Entry point — usage: python main.py <map_file>"""
    if len(sys.argv) < 2:
        print("Usage: python main.py <map_file>")
        return

    map_file: str = sys.argv[1]


    try:
        parser = Parse(map_file)
        nb_drones, zones, start, end, connections = parser.parse()
    except ParseError as e:
        print(f"Error: {e}")
        return
    path = graph.shortest_path(start, end)  # same path for all drones (simple version)

    drones = [Drone(drone_id=i + 1, position=start, path=path[1:]) for i in range(nb_drones)]
    sim = Simulation(graph, drones, end)
    log = sim.run()

    for i, line in enumerate(log, start=1):
        print_turn(i, line)
    print(f"\nCompleted in {len(log)} turns.")


if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else "maps/easy_1.txt")