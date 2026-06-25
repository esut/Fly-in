from typing import Optional


class Zone:
    """A single location on the map that drones can visit."""

    VALID_TYPES = ["normal", "restricted", "priority", "blocked"]

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        zone_type: str = "normal",
        color: Optional[str] = None,
        max_drones: int = 1,
    ) -> None:
        """
        Args:
            name: unique name of this zone (no dashes allowed)
            x: x coordinate on the map
            y: y coordinate on the map
            zone_type: 'normal', 'restricted', 'priority', or 'blocked'
            color: optional display color (e.g. 'red', 'blue')
            max_drones: how many drones can be here at once (default 1)
        """
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.color = color
        self.max_drones = max_drones

    def movement_cost(self) -> int:
        """How many simulation turns it costs a drone to enter this zone."""
        if self.zone_type == "restricted":
            return 2
        return 1

    def is_blocked(self) -> bool:
        """Drones cannot enter blocked zones at all."""
        return self.zone_type == "blocked"

    def __str__(self) -> str:
        return f"Zone({self.name}, type={self.zone_type}, max_drones={self.max_drones})"
