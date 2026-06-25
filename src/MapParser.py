import sys
from zone import Zone
from connection import Connection
from network import Network


class MapParser:
    """
    Reads a map text file and builds a Network of Zone and Connection objects.

    File format example:
        nb_drones: 3
        start_hub: hub 0 0 [color=green]
        end_hub:   goal 10 10 [color=yellow]
        hub: roof1 3 4 [zone=restricted color=red]
        connection: hub-roof1
        connection: roof1-goal [max_link_capacity=2]
    """

    def __init__(self, filepath: str) -> None:
        """
        Args:
            filepath: path to the map text file
        """
        self.filepath = filepath
        self.nb_drones: int = 0
        self.start_hub: str = ""
        self.end_hub: str = ""
        self.network: Network = Network()
        self._seen_connections: set[str] = set()

    def parse(self) -> None:
        """Read the file line by line and fill self.network, self.nb_drones, etc."""
        try:
            with open(self.filepath, "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Error: file not found: {self.filepath}", file=sys.stderr)
            sys.exit(1)

        for line_number, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()

            if not line or line.startswith("#"):
                continue

            try:
                if line.startswith("nb_drones:"):
                    self._parse_nb_drones(line)

                elif line.startswith("start_hub:"):
                    self.start_hub = self._parse_zone_line(line)

                elif line.startswith("end_hub:"):
                    self.end_hub = self._parse_zone_line(line)

                elif line.startswith("hub:"):
                    self._parse_zone_line(line)

                elif line.startswith("connection:"):
                    self._parse_connection_line(line)

                else:
                    raise ValueError(f"unknown line format: '{line}'")

            except ValueError as error:
                print(f"Parse error on line {line_number}: {error}", file=sys.stderr)
                sys.exit(1)

        self._validate()

    def _validate(self) -> None:
        """Check that the parsed map is complete and valid."""
        if self.nb_drones <= 0:
            print("Error: nb_drones must be a positive integer.", file=sys.stderr)
            sys.exit(1)
        if not self.start_hub:
            print("Error: no start_hub defined.", file=sys.stderr)
            sys.exit(1)
        if not self.end_hub:
            print("Error: no end_hub defined.", file=sys.stderr)
            sys.exit(1)

    def _parse_nb_drones(self, line: str) -> None:
        """Parse 'nb_drones: 5' and store the number."""
        _, value_str = line.split(":", 1)
        try:
            value = int(value_str.strip())
        except ValueError:
            raise ValueError(f"nb_drones must be an integer, got: '{value_str.strip()}'")
        if value <= 0:
            raise ValueError(f"nb_drones must be positive, got: {value}")
        self.nb_drones = value

    def _parse_metadata(self, meta_str: str) -> dict[str, str]:
        """
        Parse '[zone=restricted color=red max_drones=2]' into a dictionary.

        Args:
            meta_str: the raw string including the brackets

        Returns:
            dict like {'zone': 'restricted', 'color': 'red', 'max_drones': '2'}
        """
        meta_str = meta_str.strip("[] ")
        result: dict[str, str] = {}
        for part in meta_str.split():
            if "=" in part:
                key, value = part.split("=", 1)
                result[key.strip()] = value.strip()
        return result

    def _parse_zone_line(self, line: str) -> str:
        """
        Parse a hub/start_hub/end_hub line, create a Zone, add it to the network.

        Args:
            line: e.g. 'hub: roof1 3 4 [zone=restricted color=red]'

        Returns:
            the zone name (str)
        """
        _, rest = line.split(":", 1)
        rest = rest.strip()

        meta: dict[str, str] = {}
        if "[" in rest:
            core_part, meta_part = rest.split("[", 1)
            meta = self._parse_metadata("[" + meta_part)
        else:
            core_part = rest

        parts = core_part.strip().split()
        if len(parts) < 3:
            raise ValueError(f"zone line needs at least name x y, got: '{line}'")

        name = parts[0]

        try:
            x = int(parts[1])
            y = int(parts[2])
        except ValueError:
            raise ValueError(f"zone x and y must be integers in: '{line}'")

        if name in self.network.zones:
            raise ValueError(f"duplicate zone name: '{name}'")

        zone_type = meta.get("zone", "normal")
        if zone_type not in Zone.VALID_TYPES:
            raise ValueError(
                f"invalid zone type '{zone_type}'. Must be one of: {Zone.VALID_TYPES}"
            )

        color = meta.get("color", None)

        try:
            max_drones = int(meta.get("max_drones", "1"))
            if max_drones <= 0:
                raise ValueError()
        except ValueError:
            raise ValueError(f"max_drones must be a positive integer in: '{line}'")

        zone = Zone(
            name=name,
            x=x,
            y=y,
            zone_type=zone_type,
            color=color,
            max_drones=max_drones,
        )
        self.network.add_zone(zone)
        return name

    def _parse_connection_line(self, line: str) -> None:
        """
        Parse 'connection: zoneA-zoneB [max_link_capacity=2]' and add to network.

        Args:
            line: the raw connection line
        """
        _, rest = line.split(":", 1)
        rest = rest.strip()

        meta: dict[str, str] = {}
        if "[" in rest:
            core_part, meta_part = rest.split("[", 1)
            meta = self._parse_metadata("[" + meta_part)
        else:
            core_part = rest

        core_part = core_part.strip()
        if "-" not in core_part:
            raise ValueError(f"connection must be zone1-zone2, got: '{core_part}'")

        zone1, zone2 = core_part.split("-", 1)
        zone1 = zone1.strip()
        zone2 = zone2.strip()

        if zone1 not in self.network.zones:
            raise ValueError(f"unknown zone '{zone1}' in connection")
        if zone2 not in self.network.zones:
            raise ValueError(f"unknown zone '{zone2}' in connection")

        pair_key = "-".join(sorted([zone1, zone2]))
        if pair_key in self._seen_connections:
            raise ValueError(f"duplicate connection between '{zone1}' and '{zone2}'")
        self._seen_connections.add(pair_key)

        try:
            capacity = int(meta.get("max_link_capacity", "1"))
            if capacity <= 0:
                raise ValueError()
        except ValueError:
            raise ValueError(f"max_link_capacity must be a positive integer in: '{line}'")

        conn = Connection(zone1, zone2, capacity)
        self.network.add_connection(conn)
