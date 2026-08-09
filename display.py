from graph import Graph

class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"

    MAP = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "gray": "\033[90m",
        "grey": "\033[90m",
        "orange": "\033[38;5;208m",
    }

    @staticmethod
    def paint(text: str, color: str) -> str:
        code = Color.MAP.get(color.lower(), "")
        return f"{code}{text}{Color.RESET}" if code else text

    @staticmethod
    def bold(text: str) -> str:
        return f"{Color.BOLD}{text}{Color.RESET}"


class Display:
    def __init__(self, graph) -> None:
        self.graph = graph

    def _zone_label(self, zone_name: str) -> str:
        zone = self.graph.zones.get(zone_name)

        if zone and zone.color:
            return Color.paint(zone_name, zone.color)

        return zone_name

    def print_header(self, nb_drones: int) -> None:
        print(Color.bold("\n=== FLY-IN SIMULATION ==="))
        print(f"Drones  : {nb_drones}")
        print(Color.bold("─" * 40))

    def print_turn(self, moves: dict[int, str]) -> None:
        if not moves:
            return

        parts = []

        for drone_id, zone in sorted(moves.items()):
            drone = Color.paint(f"D{drone_id + 1}", "cyan")
            parts.append(f"{drone}-{self._zone_label(zone)}")

        print(f"{' '.join(parts)}")

    def print_footer(self, turns: int) -> None:
        print(Color.bold("─" * 40))
        print(f"{Color.bold('Total turns:')} {Color.paint(str(turns), 'green')}")