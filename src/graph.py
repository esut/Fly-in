import heapq
from src.models import Zone, Connection, ZoneType


class Graph:
    def __init__(self) -> None:
        self.zones: dict[str, Zone] = {}
        self.connections: dict[frozenset[str], Connection] = {}
        self.adjacency: dict[str, list[str]] = {}

    def add_zone(self, zone: Zone) -> None:
        self.zones[zone.name] = zone
        self.adjacency.setdefault(zone.name, [])

    def add_connection(self, conn: Connection) -> None:
        key = frozenset((conn.zone_a, conn.zone_b))
        self.connections[key] = conn
        self.adjacency[conn.zone_a].append(conn.zone_b)
        self.adjacency[conn.zone_b].append(conn.zone_a)

    def get_connection(self, a: str, b: str) -> Connection:
        return self.connections[frozenset((a, b))]

    def shortest_path(self, start: str, end: str) -> list[str]:
        """Dijkstra: cheapest path by cumulative zone-entry cost."""
        dist: dict[str, float] = {start: 0}
        prev: dict[str, str] = {}
        visited: set[str] = set()
        heap: list[tuple[float, str]] = [(0, start)]

        while heap:
            d, node = heapq.heappop(heap)
            if node in visited:
                continue
            visited.add(node)
            if node == end:
                break

            for neighbor in self.adjacency[node]:
                zone = self.zones[neighbor]
                if zone.zone_type == ZoneType.BLOCKED:
                    continue
                new_dist = d + zone.zone_type.cost
                if new_dist < dist.get(neighbor, float("inf")):
                    dist[neighbor] = new_dist
                    prev[neighbor] = node
                    heapq.heappush(heap, (new_dist, neighbor))

        # reconstruct path
        path = [end]
        while path[-1] != start:
            path.append(prev[path[-1]])
        return list(reversed(path))