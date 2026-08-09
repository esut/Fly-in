from display import Display
from graph import Graph
from models import Connection


class Simulation:
    """Manages step-by-step drone routing execution in the terminal."""

    def __init__(
        self,
        graph: Graph,
        drone_paths: list[list[str]],
        nb_drones: int,
        connections: list[Connection],
    ) -> None:
        self.graph = graph
        self.drone_paths = drone_paths
        self.nb_drones = nb_drones
        self.connections = connections

        self.start_zone = drone_paths[0][0]
        self.end_zone = drone_paths[0][-1]
        self.display = Display(graph)

        self.turn = 0
        self.positions = [0] * nb_drones

        self.cooldowns = [0] * nb_drones
    def _zone_capacity(self, zone_name: str) -> int:
        if zone_name in (self.start_zone, self.end_zone):
            return 999999
        return self.graph.zones[zone_name].max_drones

    def _link_capacity(self, zone_a: str, zone_b: str) -> int:
        for conn in self.connections:
            if (conn.zone_a == zone_a and conn.zone_b == zone_b) or \
               (conn.zone_a == zone_b and conn.zone_b == zone_a):
                return conn.max_link_capacity
        return 1

    def all_arrived(self) -> bool:
        for drone_id in range(self.nb_drones):
            if self.positions[drone_id] < len(self.drone_paths[drone_id]) - 1:
                return False
        return True

    def _compute_turn(self) -> dict[int, str]:
        moves = {}
        zone_counts: dict[str, int] = {}

        for drone_id in range(self.nb_drones):
            curr_zone = self.drone_paths[drone_id][self.positions[drone_id]]
            zone_counts[curr_zone] = zone_counts.get(curr_zone, 0) + 1

        link_usage: dict[tuple[str, ...], int] = {}
        planned_arrivals: dict[str, int] = {}
        planned_departures: dict[str, int] = {}

        for drone_id in range(self.nb_drones):
            # --- ---
            if self.cooldowns[drone_id] > 0:
                self.cooldowns[drone_id] -= 1
                continue
            # --- ---
            curr_idx = self.positions[drone_id]
            path = self.drone_paths[drone_id]

            if curr_idx >= len(path) - 1:
                continue

            curr_zone = path[curr_idx]
            next_zone = path[curr_idx + 1]
            link = tuple(sorted((curr_zone, next_zone)))

            link_cap = self._link_capacity(curr_zone, next_zone)
            if link_usage.get(link, 0) >= link_cap:
                continue

            expected_drones = (
                zone_counts.get(next_zone, 0)
                - planned_departures.get(next_zone, 0)
                + planned_arrivals.get(next_zone, 0)
            )

            if expected_drones >= self._zone_capacity(next_zone):
                continue

            moves[drone_id] = next_zone
            link_usage[link] = link_usage.get(link, 0) + 1
            planned_arrivals[next_zone] = (
                planned_arrivals.get(next_zone, 0) + 1)
            planned_departures[curr_zone] = (
                planned_departures.get(curr_zone, 0) + 1)

            # -------------------------------------------------------------------------
            next_zone_cost = self.graph.zones[next_zone].entry_cost
            # -------------------------------------------------------------------------
            self.cooldowns[drone_id] = next_zone_cost - 1
            # -------------------------------------------------------------------------

        return moves

    def run(self) -> int:
        """Core execution entry point orchestrating
            routing setups in the terminal."""
        self.display.print_header(self.nb_drones)
        """=== FLY-IN SIMULATION ===
           Drones  : 4              """

        while not self.all_arrived():
            self.turn += 1

            was_witting = any(c > 0 for c in self.cooldowns)

            moves = self._compute_turn()

            if not moves and not self.all_arrived():
                if not was_witting:
                    print(
                        "\n[!] Simulation Deadlock: Drones are "
                        "stuck. Exiting to prevent infinite loop."
                    )
                    break

            for drone_id in moves:
                self.positions[drone_id] += 1

            self.display.print_turn(moves)

        return self.turn
