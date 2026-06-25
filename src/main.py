import sys
from MapParser import MapParser
from pathfinder import Pathfinder
from simulation import Simulation
from visualizer import Visualizer


def main() -> None:
    """
    Entry point for the Fly-in drone routing simulation.

    Usage:
        python main.py <map_file>

    Example:
        python main.py ../maps/easy/01_linear_path.txt
    """
    if len(sys.argv) != 2:
        print("Usage: python main.py <map_file>", file=sys.stderr)
        sys.exit(1)

    map_file = sys.argv[1]

    # Step 1: Parse the map file
    parser = MapParser(map_file)
    parser.parse()

    print(f"Map loaded: {parser.nb_drones} drones, "
          f"start='{parser.start_hub}', end='{parser.end_hub}'")
    print(f"Zones: {len(parser.network.zones)}, "
          f"Connections: {len(parser.network.connections)}\n")

    # Step 2: Find the best path from start to end
    finder = Pathfinder(parser.network)
    path = finder.find_path(parser.start_hub, parser.end_hub)

    if path is None:
        print("Error: no valid path found from start to end.", file=sys.stderr)
        sys.exit(1)

    print(f"Path found ({len(path) - 1} steps): {' -> '.join(path)}\n")

    # Step 3: Run the simulation
    sim = Simulation(
        network=parser.network,
        nb_drones=parser.nb_drones,
        start_hub=parser.start_hub,
        end_hub=parser.end_hub,
        path=path,
    )
    sim.run()

    # Step 4: Show the animated visualizer
    try:
        vis = Visualizer(parser.network, sim.history)
        vis.animate()
    except Exception as e:
        print(f"Visualizer could not run: {e}")


if __name__ == "__main__":
    main()
