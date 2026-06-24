from zone import Zone 
from connection import Connection
from network import Network

class MapParser:
    """Parses the map text file into Zone and Connection objects."""

    def __init__(self, filepath: str)->None:
        self.filepath = filepath
        self.nb_drones: int = 0
        self.start_hub: str = ""
        self.end_hub: str = "" 
        self.network: Network = Network()
    def parse(self) -> None:
        """
        Read the file line by line and extract the map data.
        """
        try:
            with open(self.filepath,'r') as file:
                lines = file.readlines()
            
            for line in lines:
                line = line.strip()

                if not line or line.startswith('#'):
                    continue
                
                if line.startswith('nb_drones'):
                    parts = line.split(':')
                    self.nb_drones = int(parts[1].strip())
                    print(f"find  drone:{self.nb_drones}")

                elif line.startswith('start_hub:'):
                    self.start_hub = self.parse_zone_line(line, default_type="normal")
                elif line.startswith('end_hub:'):
                    self.end_hub = self.parse_zone_line(line, default_type="normal")

                elif line.startswith('hub:'):
                    self.parse_zone_line(line, default_type="normal")

                elif line.startswith('connection:'):
                    self.parse_connection_line(line)

        except FileNotFoundError:
            print(f"Error: Could not find the file {self.filepath}")
        except Exception as e:
            print(f"Parsing Error:{e}")
    
    def parse_zone_line(self, line: str, default_type: str = "normal") -> None:
        """
        Extract zone details from a text line and create a Zone object.

        Args:
            line (str): The raw text line.
            default_type (str): Fallback zone type if none is provided.
        """
        prefix, rest_of_line = line.split(':', 1)
        rest_of_line = rest_of_line.strip()
        
        metadata_str = ""
        if '[' in rest_of_line:
            core_info, meta_info = rest_of_line.split('[', 1)
            metadata_str = "[" + meta_info 
        else:
            core_info = rest_of_line
            
        data_parts = core_info.split()
        
        if len(data_parts) < 3:
            raise ValueError(f"error: {line}")
            
        name = data_parts[0]
        x = int(data_parts[1]) 
        y = int(data_parts[2])
        
        new_zone = Zone(name=name, x=x, y=y, zone_type=default_type)
        
        self.network.add_zone(new_zone)
        print(f" add new zone :{name}, X={x}, Y={y}")
        
        return name

    def parse_metadata(self, meta_str: str) -> dict[str, str]:
        """
        Convert metadata inside brackets into a dictionary.

        Args:
            meta_str (str): The string containing metadata.

        Returns:
            dict[str, str]: The extracted key-value pairs.
        """
        meta_str = meta_str.strip(" []")
        if not meta_str:
            return {}
            
        meta_dict = {}
        parts = meta_str.split()

        for part in parts:
            if '=' in part:
                key, value = part.split('=', 1)
                meta_dict[key] = value
                
        return meta_dict

    def parse_connection_line(self, line: str) -> None:

        prefix, rest_of_line = line.split(':', 1)
        rest_of_line = rest_of_line.strip()

        meta_dict = {}

        if '[' in rest_of_line:
            core_info, meta_info = rest_of_line.split('[', 1)

            meta_dict = self.parse_metadata("[" + meta_info)
        else:
            core_info = rest_of_line

        core_info = core_info.strip()
        try:
            zone1, zone2 = core_info.split('-')
        except ValueError:
            raise ValueError(f"  error  zone1-zone2: {line}")

        capacity = int(meta_dict.get('max_link_capacity', 1))
        new_conn = Connection(zone1, zone2, capacity)
        self.network.add_connection(new_conn)
        print(f" done {zone1} and {zone2} capacity {capacity}")

if __name__ == "__main__":
    from pathfinder import Pathfinder

    parser = MapParser("../maps/hard/03_ultimate_challenge.txt")
    parser.parse()

    print("\n--- Pathfinding Test ---")
    if parser.start_hub and parser.end_hub:
    
        finder = Pathfinder(parser.network)
        
        
        path = finder.find_shortest_path_bfs(parser.start_hub, parser.end_hub)
        
        if path:
            print(f"✅ : {' -> '.join(path)}")
        else:
            print("❌ !")