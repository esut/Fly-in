from models import Zone


class Graph:
    """
    The map of the simulation.
    Holds all zones and the connections between them.

    Example of what it looks like inside:
        zones      = { "A": Zone_A, "B": Zone_B, "C": Zone_C }
        neighbors  = { "A": ["B", "C"],
                       "B": ["A"],
                       "C": ["A"] }
    """

    def __init__(self) -> None:
        self.zones: dict[str, Zone] = {}
        self.neighbors: dict[str, list[str]] = {}

    def add_zone(self, zone: Zone) -> None:
        """Register a zone so the graph knows it exists."""
        self.zones[zone.name] = zone
        self.neighbors[zone.name] = []

    def add_connection(self, zone_a_name: str, zone_b_name: str) -> None:
        """Create a two-way link between two zones."""
        self.neighbors[zone_a_name].append(zone_b_name)
        self.neighbors[zone_b_name].append(zone_a_name)

    def get_neighbors(self, zone_name: str) -> list[str]:
        """Return the list of zones reachable from zone_name in one step."""
        return self.neighbors.get(zone_name, [])
