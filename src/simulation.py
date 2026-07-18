# simulation.py
from src.models import Drone, ZoneType
from src.graph import Graph


class Simulation:
    def __init__(self, graph: Graph, drones: list[Drone], end_zone: str) -> None:
        self.graph = graph
        self.drones = drones
        self.end_zone = end_zone
        self.turn = 0
        self.log: list[str] = []

    def run(self) -> list[str]:
        while not all(d.delivered for d in self.drones):
            self._step()
        return self.log

    def _step(self) -> None:
        self.turn += 1
        moves_this_turn: list[str] = []

        # Track occupancy changes this turn to allow same-turn swaps
        zone_leaving: dict[str, int] = {}
        zone_arriving: dict[str, int] = {}
        link_usage: dict[frozenset[str], int] = {}

        for drone in self.drones:
            if drone.delivered:
                continue

            # Finish a 2-turn restricted move
            if drone.in_transit_turns_left > 0:
                drone.in_transit_turns_left -= 1
                if drone.in_transit_turns_left == 0:
                    dest = drone.path[drone.step_index]
                    drone.position = dest
                    drone.step_index += 1
                    moves_this_turn.append(f"D{drone.drone_id}-{dest}")
                    if dest == self.end_zone:
                        drone.delivered = True
                continue

            if drone.step_index >= len(drone.path):
                drone.delivered = True
                continue

            next_zone_name = drone.path[drone.step_index]
            next_zone = self.graph.zones[next_zone_name]
            conn = self.graph.get_connection(drone.position, next_zone_name)
            link_key = frozenset((drone.position, next_zone_name))

            current_occupants = sum(
                1 for d in self.drones if d.position == next_zone_name and not d.delivered
            )
            leaving_count = zone_leaving.get(next_zone_name, 0)
            arriving_count = zone_arriving.get(next_zone_name, 0)
            link_count = link_usage.get(link_key, 0)

            zone_has_room = (current_occupants - leaving_count - arriving_count) < next_zone.capacity()
            link_has_room = link_count < conn.max_link_capacity

            if zone_has_room and link_has_room:
                zone_leaving[drone.position] = zone_leaving.get(drone.position, 0) + 1
                zone_arriving[next_zone_name] = arriving_count + 1
                link_usage[link_key] = link_count + 1

                if next_zone.zone_type == ZoneType.RESTRICTED:
                    drone.in_transit_turns_left = 1  # arrives next turn
                    moves_this_turn.append(f"D{drone.drone_id}-{drone.position}{next_zone_name}")
                else:
                    drone.position = next_zone_name
                    drone.step_index += 1
                    moves_this_turn.append(f"D{drone.drone_id}-{next_zone_name}")
                    if next_zone_name == self.end_zone:
                        drone.delivered = True
            # else: drone waits, contributes nothing to this line

        if moves_this_turn:
            self.log.append(" ".join(moves_this_turn))