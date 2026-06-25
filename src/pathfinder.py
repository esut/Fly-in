import heapq
from typing import Optional
from network import Network


class Pathfinder:
    """
    Finds the shortest path between two zones using Dijkstra's algorithm.

    Zone movement costs:
        normal     -> 1 turn
        priority   -> 0.9 turns (preferred over normal, same real cost)
        restricted -> 2 turns
        blocked    -> cannot enter (skipped)
    """

    def __init__(self, network: Network) -> None:
        """
        Args:
            network: the map network with all zones and connections
        """
        self.network = network

    def find_path(self, start: str, end: str) -> Optional[list[str]]:
        """
        Find the lowest-cost path from start zone to end zone.

        Args:
            start: name of the starting zone
            end: name of the destination zone

        Returns:
            list of zone names from start to end (inclusive), or None if no path exists
        """
        if start not in self.network.zones:
            return None
        if end not in self.network.zones:
            return None

        # Each entry in the heap: (accumulated_cost, zone_name, path_so_far)
        heap: list[tuple[float, str, list[str]]] = [(0.0, start, [start])]

        # Remember the best cost found to reach each zone
        best_cost: dict[str, float] = {}

        while heap:
            cost, current_zone, path = heapq.heappop(heap)

            # Skip if we already found a cheaper way to this zone
            if current_zone in best_cost:
                continue
            best_cost[current_zone] = cost

            # Found the destination
            if current_zone == end:
                return path

            # Look at all reachable neighbors
            for neighbor_name, _conn in self.network.get_neighbors(current_zone):
                if neighbor_name in best_cost:
                    continue

                neighbor_zone = self.network.zones[neighbor_name]

                if neighbor_zone.is_blocked():
                    continue

                # Cost to step into the neighbor zone
                if neighbor_zone.zone_type == "restricted":
                    step_cost = 2.0
                elif neighbor_zone.zone_type == "priority":
                    step_cost = 0.9  # Slightly cheaper so priority zones are preferred
                else:
                    step_cost = 1.0

                new_cost = cost + step_cost
                new_path = path + [neighbor_name]
                heapq.heappush(heap, (new_cost, neighbor_name, new_path))

        return None  # No path found
