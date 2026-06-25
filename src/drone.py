from typing import Optional


class Drone:
    """
    Represents a single drone flying through the map.

    A drone follows a pre-planned path zone by zone.
    When the next zone is 'restricted', entering it takes 2 turns:
        Turn 1: drone leaves current zone, enters the link (in_transit = True)
        Turn 2: drone arrives at the restricted zone (in_transit = False)
    """

    def __init__(self, drone_id: str, start_zone: str) -> None:
        """
        Args:
            drone_id: unique identifier like 'D1', 'D2', etc.
            start_zone: name of the zone where this drone starts
        """
        self.id = drone_id
        self.current_zone = start_zone
        self.path: list[str] = []
        self.path_index: int = 0

        # These two fields are only used when crossing a restricted zone
        self.in_transit: bool = False
        self.transit_destination: str = ""

    def set_path(self, path: list[str]) -> None:
        """
        Assign a path to this drone and reset its position to the start.

        Args:
            path: ordered list of zone names from start to end
        """
        self.path = path
        self.path_index = 0

    def is_done(self, end_zone: str) -> bool:
        """Return True if the drone has reached the end zone (and is not mid-transit)."""
        return self.current_zone == end_zone and not self.in_transit

    def get_next_zone(self) -> Optional[str]:
        """Return the name of the next zone in the path, or None if already at the end."""
        next_index = self.path_index + 1
        if next_index < len(self.path):
            return self.path[next_index]
        return None

    def start_transit_to(self, destination: str) -> None:
        """
        Begin a 2-turn move toward a restricted zone.
        The drone leaves its current zone but has not yet arrived at destination.

        Args:
            destination: name of the restricted zone being entered
        """
        self.in_transit = True
        self.transit_destination = destination

    def complete_transit(self) -> None:
        """Finish the 2-turn move — the drone arrives at its transit destination."""
        self.in_transit = False
        self.path_index += 1
        self.current_zone = self.transit_destination
        self.transit_destination = ""

    def move_to(self, destination: str) -> None:
        """
        Instantly move to the next zone (1-turn normal move).

        Args:
            destination: the zone name to move to
        """
        self.path_index += 1
        self.current_zone = destination

    def __str__(self) -> str:
        status = f"transit→{self.transit_destination}" if self.in_transit else self.current_zone
        return f"Drone({self.id} at {status})"
