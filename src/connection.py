class Connection:
    """A bidirectional link between two zones."""

    def __init__(
        self,
        zone1: str,
        zone2: str,
        max_link_capacity: int = 1,
    ) -> None:
        """
        Args:
            zone1: name of the first zone
            zone2: name of the second zone
            max_link_capacity: max drones that can use this link at the same time
        """
        self.zone1 = zone1
        self.zone2 = zone2
        self.max_link_capacity = max_link_capacity

    def connects(self, zone_name: str) -> bool:
        """Check if this connection touches the given zone."""
        return zone_name == self.zone1 or zone_name == self.zone2

    def other_end(self, zone_name: str) -> str:
        """Given one zone, return the zone on the other end of this connection."""
        if zone_name == self.zone1:
            return self.zone2
        return self.zone1

    def key(self) -> str:
        """A consistent string key for this connection (alphabetical order)."""
        a, b = sorted([self.zone1, self.zone2])
        return f"{a}-{b}"

    def __str__(self) -> str:
        return f"Connection({self.zone1} <-> {self.zone2}, cap={self.max_link_capacity})"
