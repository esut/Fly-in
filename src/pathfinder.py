from collections import deque
from typing import Optional
from network import Network

class Pathfinder:
    """ Pathfinder"""

    def __init__(self, network: Network) -> None:
        """   """
        self.network = network

    def find_shortest_path_bfs(self, start_name: str, end_name: str)-> Optional[list[str]]:
        if start_name not in self.network.zones or end_name not in self.network.zones:
            return None

        queue: deque[tuple[str, list[str]]] = deque([(start_name, [start_name])])
        
        visited: set[str] = set([start_name])

        while queue:
            current_zone, current_path = queue.popleft()

            if current_zone == end_name:
                return current_path

            neighbors = self.network.get_neighbors(current_zone)
            
            for conn in neighbors:
                if conn.zone1_name == current_zone:
                    neighbor_name = conn.zone2_name
                else:
                    neighbor_name = conn.zone1_name

                neighbor_zone = self.network.zones.get(neighbor_name)

                if neighbor_zone and neighbor_name not in visited:
                    if neighbor_zone.zone_type == "blocked":
                        continue  
                        
                    
                    visited.add(neighbor_name)            
                    new_path = list(current_path)        
                    new_path.append(neighbor_name)        
                    queue.append((neighbor_name, new_path)) 

        return None