from network import Network
from drone import Drone


class Simulation:
    """
    Runs the drone routing simulation turn by turn.

    Each turn:
      1. Drones completing a 2-turn restricted-zone transit arrive at their destination.
      2. Drones not in transit try to move to their next zone.
         - Zone capacity (max_drones) is respected.
         - Link capacity (max_link_capacity) is respected.
         - Drones that leave a zone free up its space in the same turn.
      3. The turn's movements are printed in the required format.

    Output format per turn:  D1-zone1 D2-zone2 D3-zone1-zone2
      where D3-zone1-zone2 means D3 is mid-transit toward zone2 via the zone1-zone2 link.

    Simulation ends when all drones reach the end zone.
    """

    MAX_TURNS = 1000  # Safety limit to prevent infinite loops

    def __init__(
        self,
        network: Network,
        nb_drones: int,
        start_hub: str,
        end_hub: str,
        path: list[str],
    ) -> None:
        """
        Args:
            network: the map with all zones and connections
            nb_drones: how many drones to simulate
            start_hub: name of the starting zone
            end_hub: name of the ending zone
            path: the planned route (list of zone names) all drones will follow
        """
        self.network = network
        self.end_hub = end_hub

        # Create all drones and assign the path to each
        self.drones: list[Drone] = []
        for i in range(1, nb_drones + 1):
            drone = Drone(f"D{i}", start_hub)
            drone.set_path(path)
            self.drones.append(drone)

        # How many drones are currently in each zone (not counting in-transit drones)
        self.zone_occupancy: dict[str, int] = {z: 0 for z in network.zones}
        self.zone_occupancy[start_hub] = nb_drones

        # Store a snapshot of drone positions after each turn (for the visualizer)
        self.history: list[dict[str, str]] = []
        self._save_snapshot()

    def run(self) -> int:
        """
        Run the full simulation.

        Returns:
            total number of turns taken
        """
        turn = 1
        while not self._all_done():
            moves = self._run_one_turn()
            if moves:
                print(" ".join(moves))
            self._save_snapshot()
            turn += 1
            if turn > self.MAX_TURNS:
                print("Warning: simulation stopped (deadlock or too many turns).")
                break

        total_turns = turn - 1
        print(f"\nSimulation finished in {total_turns} turns.")
        return total_turns

    def _all_done(self) -> bool:
        """Return True when every drone has reached the end zone."""
        return all(drone.is_done(self.end_hub) for drone in self.drones)

    def _save_snapshot(self) -> None:
        """Record current drone positions for the visualizer."""
        snapshot: dict[str, str] = {}
        for drone in self.drones:
            if drone.in_transit:
                snapshot[drone.id] = drone.transit_destination
            else:
                snapshot[drone.id] = drone.current_zone
        self.history.append(snapshot)

    def _run_one_turn(self) -> list[str]:
        """
        Execute one simulation turn and return the list of move strings.

        Two phases are handled simultaneously:
          Phase A - drones completing their restricted-zone transit
          Phase B - drones starting a new move (normal or restricted)
        """
        moves: list[str] = []

        # --- Count how many transit drones will arrive at each zone this turn ---
        # (so Phase B can account for that space when checking capacity)
        transit_arrivals: dict[str, int] = {}
        for drone in self.drones:
            if drone.in_transit:
                dest = drone.transit_destination
                transit_arrivals[dest] = transit_arrivals.get(dest, 0) + 1

        # --- Phase B: decide which free drones can move ---
        # Track departures and new arrivals so we don't double-book capacity
        departures: dict[str, int] = {z: 0 for z in self.network.zones}
        new_arrivals: dict[str, int] = dict(transit_arrivals)
        link_usage: dict[str, int] = {}

        # List of moves to apply after all decisions are made
        planned: list[tuple[Drone, str, bool]] = []  # (drone, destination, is_restricted)

        for drone in self.drones:
            if drone.is_done(self.end_hub) or drone.in_transit:
                continue

            next_zone_name = drone.get_next_zone()
            if next_zone_name is None:
                continue

            next_zone = self.network.zones[next_zone_name]
            is_end_zone = (next_zone_name == self.end_hub)

            # Effective occupancy of next_zone considering moves already planned this turn
            effective_occ = (
                self.zone_occupancy.get(next_zone_name, 0)
                - departures.get(next_zone_name, 0)
                + new_arrivals.get(next_zone_name, 0)
            )

            has_zone_space = is_end_zone or (effective_occ < next_zone.max_drones)

            # Check link capacity
            conn = self.network.find_connection(drone.current_zone, next_zone_name)
            link_key = f"{min(drone.current_zone, next_zone_name)}-{max(drone.current_zone, next_zone_name)}"
            has_link_space = True
            if conn:
                used = link_usage.get(link_key, 0)
                if used >= conn.max_link_capacity:
                    has_link_space = False

            if not (has_zone_space and has_link_space):
                continue  # Drone waits this turn

            # This drone will move — reserve the space now
            departures[drone.current_zone] = departures.get(drone.current_zone, 0) + 1
            if conn:
                link_usage[link_key] = link_usage.get(link_key, 0) + 1

            is_restricted = (next_zone.zone_type == "restricted")
            if not is_restricted:
                # Drone arrives at destination this same turn
                new_arrivals[next_zone_name] = new_arrivals.get(next_zone_name, 0) + 1

            planned.append((drone, next_zone_name, is_restricted))

        # --- Apply Phase A: transit drones arrive ---
        for drone in self.drones:
            if drone.in_transit:
                dest = drone.transit_destination
                drone.complete_transit()
                moves.append(f"{drone.id}-{dest}")

        # --- Apply Phase B: planned moves execute ---
        for drone, destination, is_restricted in planned:
            from_zone = drone.current_zone
            if is_restricted:
                drone.start_transit_to(destination)
                # Output: D1-fromZone-toZone (the connection being traversed)
                moves.append(f"{drone.id}-{from_zone}-{destination}")
            else:
                drone.move_to(destination)
                moves.append(f"{drone.id}-{destination}")

        # --- Rebuild zone occupancy from scratch ---
        self.zone_occupancy = {z: 0 for z in self.network.zones}
        for drone in self.drones:
            if not drone.in_transit:
                z = drone.current_zone
                if z in self.zone_occupancy:
                    self.zone_occupancy[z] += 1

        return moves
