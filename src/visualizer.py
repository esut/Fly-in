import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from network import Network


# Map zone types to background colors for the visualizer
ZONE_TYPE_COLORS: dict[str, str] = {
    "normal": "lightblue",
    "restricted": "salmon",
    "priority": "lightgreen",
    "blocked": "dimgray",
}


class Visualizer:
    """
    Draws the map and animates drone movements turn by turn using matplotlib.

    Each zone is shown as a colored circle.
    Drones are shown as blue diamonds that move between circles.
    """

    def __init__(self, network: Network, history: list[dict[str, str]]) -> None:
        """
        Args:
            network: the map with all zones and connections
            history: list of snapshots, one per turn.
                     Each snapshot is {drone_id: zone_name}.
        """
        self.network = network
        self.history = history

    def animate(self) -> None:
        """Draw the network and animate the drones through all recorded turns."""
        plt.ion()
        fig, ax = plt.subplots(figsize=(12, 8))

        # Draw connections as arrows (only once, they don't change)
        self._draw_connections(ax)

        # Draw zones as circles (only once, they don't change)
        self._draw_zones(ax)

        ax.grid(True, linestyle="--", alpha=0.4)
        ax.set_facecolor("#f8f9fa")
        ax.margins(0.25)
        plt.axis("equal")

        # Animate: redraw drone markers each turn
        drone_markers: list[object] = []

        for turn, snapshot in enumerate(self.history):
            # Remove old drone markers
            for marker in drone_markers:
                marker.remove()  # type: ignore
            drone_markers.clear()

            # Draw each drone at its current zone
            for drone_id, zone_name in snapshot.items():
                zone = self.network.zones.get(zone_name)
                if zone is None:
                    continue

                # Slight offset so drones don't all stack at the exact same point
                drone_number = int(drone_id[1:])
                offset_x = (drone_number % 3 - 1) * 0.12
                offset_y = (drone_number % 2) * 0.12

                scatter = ax.scatter(
                    zone.x + offset_x,
                    zone.y + offset_y,
                    s=500,
                    c="royalblue",
                    marker="D",
                    edgecolors="gold",
                    linewidths=1.5,
                    zorder=4,
                )
                label = ax.text(
                    zone.x + offset_x,
                    zone.y + offset_y,
                    drone_id,
                    color="white",
                    ha="center",
                    va="center",
                    fontsize=7,
                    fontweight="bold",
                    zorder=5,
                )
                drone_markers.append(scatter)
                drone_markers.append(label)

            ax.set_title(f"Fly-in Simulation  —  Turn {turn}", fontsize=14, fontweight="bold")
            plt.draw()
            plt.pause(0.6)

        plt.ioff()
        plt.show()

    def _draw_connections(self, ax: plt.Axes) -> None:  # type: ignore
        """Draw bidirectional arrows for each connection."""
        drawn: set[str] = set()
        for zone_name in self.network.zones:
            for neighbor_name, conn in self.network.get_neighbors(zone_name):
                pair = conn.key()
                if pair in drawn:
                    continue
                drawn.add(pair)

                z1 = self.network.zones[zone_name]
                z2 = self.network.zones[neighbor_name]

                arrow = FancyArrowPatch(
                    (z1.x, z1.y),
                    (z2.x, z2.y),
                    arrowstyle="<|-|>",
                    color="gray",
                    mutation_scale=15,
                    linewidth=1.5,
                    zorder=1,
                )
                ax.add_patch(arrow)

                # Show link capacity if more than 1
                if conn.max_link_capacity > 1:
                    mid_x = (z1.x + z2.x) / 2
                    mid_y = (z1.y + z2.y) / 2
                    ax.text(mid_x, mid_y, f"cap={conn.max_link_capacity}",
                            fontsize=7, color="purple", ha="center")

    def _draw_zones(self, ax: plt.Axes) -> None:  # type: ignore
        """Draw each zone as a colored circle with its name."""
        for name, zone in self.network.zones.items():
            # Use the zone's own color if set, otherwise use the type color
            if zone.color:
                color = zone.color
            else:
                color = ZONE_TYPE_COLORS.get(zone.zone_type, "lightblue")

            ax.scatter(zone.x, zone.y, s=4000, c=color,
                       edgecolors="black", linewidths=2, zorder=2)
            ax.text(zone.x, zone.y, name,
                    ha="center", va="center",
                    fontsize=9, fontweight="bold", zorder=3)
