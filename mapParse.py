from models import Zone, Connection, ParseError
import sys


class MapParse:
    def __init__(self, path: str) -> None:
        self.path: str = path

    def clean_lines(self) -> list[str]:
        """Read the file and return lines without blanks or comments."""
        lines: list[str] = []
        try:
            with open(self.path, "r") as f:
                for row in f:
                    line = row.split("#")[0].strip()
                    if not line:
                        continue
                    lines.append(line)
        except FileNotFoundError as f:
            print(f"Error:{f}")
        except Exception as e:
            print(f"Error:{e}")

        return lines

    def parse_metadata(self, meta: str) -> dict[str, str]:
        """Parse metadata string "[color=red max_drones=3]" into a dict."""
        meta_dict: dict[str, str] = {}
        if not meta:
            return meta_dict
        clean = meta.replace("[", "").replace("]", "")
        for item in clean.split(" "):
            item = item.strip()
            if "=" in item:
                key, value = item.split("=", 1)
                meta_dict[key.strip()] = value.strip()
        return meta_dict

    def parse_nb_drones(self, line: str) -> int:
        """'nb_drones: 5' -> ["nb_drones", " 5"]"""
        try:
            return int(line.split(":")[1].strip())
        except (IndexError, ValueError, Exception):
            print(f"Invalid nb_drones line: {line!r}")
            sys.exit(1)

    def parse_zone(self, line: str) -> Zone:
        """'hub: corridorA 4 3 [color=red]' -> Zone('corridorA', 4, 3)"""
        try:
            body = line.split(":", 1)[1] # corridorA 4 3 [color=red]
            before_meta = body.split("[")[0] # corridorA 4 3
            name, x, y = before_meta.split() # name="corridorA", x=4, y=3
            meta_str = "[" + body.split("[")[1] if "[" in body else ""
            meta = self.parse_metadata(meta_str)
            zone_type = meta.get("zone", "normal")
            color = meta.get("color", None)
            max_drones = int(meta.get("max_drones", 1))
            if max_drones <= 0:
                raise ParseError("invalid max_drones values")
            if zone_type not in ["restricted", "normal", "priority", "blocked"]:
                raise ParseError("Invalid  zone type !!!!!")
            return Zone(name, int(x), int(y), zone_type, color, max_drones)
        except (IndexError, ValueError, Exception, ParseError):
            print(f"Invalid zone line: {line!r}")

    def parse_connection(self, line: str) -> Connection:
        """Parse a connection line into a Connection object."""
        try:
            body = line.split(":", 1)[1]
            before_meta = body.split("[")[0]
            a, b = before_meta.strip().split("-")
            meta_str = "[" + body.split("[")[1] if "[" in body else ""
            meta = self.parse_metadata(meta_str)
            capacity = int(meta.get("max_link_capacity", 1))
            if capacity <= 0:
                print("invalid capacity values")
                sys.exit(1)
            return Connection(a.strip(), b.strip(), capacity)
        except (IndexError, ValueError, Exception):
            print(f"Invalid connection line: {line!r}")

    def parse(self) -> tuple[int, dict[str, Zone], str, str, list[Connection]]:
        """Read all lines and return parsed data."""
        nb_drones: int = 0
        zones: dict[str, Zone] = {}
        start: str = ""
        end: str = ""
        connections: list[Connection] = []

        for line in self.clean_lines():
            if line.startswith("nb_drones:"):
                nb_drones = self.parse_nb_drones(line)
            elif line.startswith("start_hub"):
                zone = self.parse_zone(line)
                zones[zone.name] = zone
                start = zone.name
            elif line.startswith("end_hub"):
                zone = self.parse_zone(line)
                zones[zone.name] = zone
                end = zone.name
            elif line.startswith("hub:"):
                zone = self.parse_zone(line)
                zones[zone.name] = zone
            elif line.startswith("connection"):
                connections.append(self.parse_connection(line))

        return nb_drones, zones, start, end, connections
