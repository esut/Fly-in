class Connection:
    """Represents a bidirectional path between two zones."""

    def __init__(self, zone1_name: str, zone2_name: str, max_link_capacity: int = 1) -> None:
        """
        Initialize a new Connection.

        Args:
            zone1_name (str): Name of the first zone.
            zone2_name (str): Name of the second zone.
            max_link_capacity (int): Maximum drones allowed on this link.
        """
        self.zone1_name = zone1_name
        self.zone2_name = zone2_name
        self.max_link_capacity = max_link_capacity
    def __str__(self) -> str:
        """
        Return a string representation of the Connection.
        """
        return f"Connection({self.zone1_name} <-> {self.zone2_name}, cap={self.max_link_capacity})"

