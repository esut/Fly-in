from zone import Zone
from connection import Connection

class Network:
    """Represents the graph of zones and their connections."""

    def __init__(self) -> None:
        """Initialize an empty network."""
        self.zones: dict[str, Zone] = {}
        # القاموس السحري: يربط اسم المنطقة بقائمة الروابط الخاصة بها
        self.adjacency_list: dict[str, list[Connection]] = {}

    def add_zone(self, zone: Zone) -> None:
        """
        Add a zone to the network.
        """
        self.zones[zone.name] = zone
        if zone.name not in self.adjacency_list:
            self.adjacency_list[zone.name] = []

    def add_connection(self, conn: Connection) -> None:
        """
        Add a bidirectional connection between two zones.
        """
        if conn.zone1_name in self.adjacency_list:
            self.adjacency_list[conn.zone1_name].append(conn)
            
        if conn.zone2_name in self.adjacency_list:
            self.adjacency_list[conn.zone2_name].append(conn)

    def get_neighbors(self, zone_name: str) -> list[Connection]:
        """
        Get all connections connected to a specific zone.
        Args:
            zone_name (str): The name of the zone.  
        Returns:
            list[Connection]: A list of connections for this zone.
        """
        return self.adjacency_list.get(zone_name, [])