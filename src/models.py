from typing import Optional


class Connection:

    def __init__(
        self, zone_a: str, zone_b: str, max_link_capacity: int = 1
    ) -> None:
        self.zone_a: str = zone_a
        self.zone_b: str = zone_b
        self.max_link_capacity: int = max_link_capacity


class Zone:

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        zone_type: str = "normal",
        color: Optional[str] = None,
        max_drones: int = 1,
    ) -> None:
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.zone_type: str = zone_type
        self.color: Optional[str] = color
        self.max_drones: int = max_drones

        if zone_type == "restricted":
            self.entry_cost: int = 2
        else:
            self.entry_cost = 1


class Drone:

    def __init__(self, name: str) -> None:
        self.name: str = name