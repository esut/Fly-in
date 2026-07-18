from dataclasses import dataclass, field
from enum import Enum


class ZoneType(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"

    @property
    def cost(self) -> int:
        return {"normal": 1, "priority": 1, "restricted": 2, "blocked": -1}[self.value]


@dataclass
class Zone:
    name: str
    x: int
    y: int
    zone_type: ZoneType = ZoneType.NORMAL
    color: str = "none"
    max_drones: int = 1
    is_start: bool = False
    is_end: bool = False

    def capacity(self) -> int:
        # start/end zones have unlimited capacity
        if self.is_start or self.is_end:
            return 10 ** 9
        return self.max_drones


@dataclass
class Connection:
    zone_a: str
    zone_b: str
    max_link_capacity: int = 1

    def other(self, zone_name: str) -> str:
        return self.zone_b if zone_name == self.zone_a else self.zone_a


@dataclass
class Drone:
    drone_id: int
    position: str
    path: list[str] = field(default_factory=list)   # precomputed route
    step_index: int = 0
    delivered: bool = False
    in_transit_turns_left: int = 0                    # for restricted zones