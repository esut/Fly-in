from zone import Zone
from connection import Connection


class Network:
    """Holds all zones and connections that make up the map."""

    def __init__(self) -> None:
        """Start with an empty network."""
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []

    def add_zone(self, zone: Zone) -> None:
        """Add a zone to the network."""
        self.zones[zone.name] = zone

    def add_connection(self, conn: Connection) -> None:
        """Add a connection (link) between two zones."""
        self.connections.append(conn)

    def get_neighbors(self, zone_name: str) -> list[tuple[str, Connection]]:
        """
        Return all zones reachable from zone_name, along with the connection used.

        Returns:
            list of (neighbor_name, connection) pairs
        """
        result: list[tuple[str, Connection]] = []
        for conn in self.connections:
            if conn.connects(zone_name):
                neighbor = conn.other_end(zone_name)
                result.append((neighbor, conn))
        return result

    def find_connection(self, zone_a: str, zone_b: str) -> Connection | None:
        """Find the connection between two zones, or None if none exists."""
        for conn in self.connections:
            if conn.connects(zone_a) and conn.connects(zone_b):
                return conn
        return None
