from collections import deque
from typing import Optional
from graph import Graph


class Pathfinder:

    def __init__(self, network: Graph) -> None:
        self.network: Graph = network

    def calculate_cost(self, path):
        """Calculate the total entry cost of a given path."""
        total = 0
        for zone in path:
            total += self.network.zones[zone].entry_cost
        return total

    def find_all_paths(self, start: str, end: str) -> list[list[str]]:
        """
        Find all simple paths from start to end using BFS.
        Returns a list of paths sorted by length (shortest first).
        """
        all_paths: list[list[str]] = []
        queue: deque[list[str]] = deque([[start]])

        while queue:
            path = queue.popleft()
            current = path[-1]

            if current == end:
                all_paths.append(path)
                continue

            for neighbor in self.network.get_neighbors(current):
                if neighbor not in path:
                    if self.network.zones[neighbor].zone_type != "blocked":
                        queue.append(path + [neighbor])

        return sorted(all_paths, key=self.calculate_cost)
