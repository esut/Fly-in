from typing import Optional 

class Zone:
    """Represents a single zone in the map network."""
    COLORS = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "gray": "\033[90m",
        "reset": "\033[0m" 
    }
    def __init__(self,name:str, x: int, y: int, zone_type: str = "normal",
                 color: Optional[str]= None, max_drones: int = 1)-> None:
        """
        Initialize a new Zone.

        Args:
            name (str): The unique name of the zone.
            x (int): The X coordinate.
            y (int): The Y coordinate.
            zone_type (str): The type of the zone (normal, restricted, etc.).
            color (Optional[str]): The visual color of the zone.
            max_drones (int): Maximum capacity of drones.
        """
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.color = color
        self.max_drones = max_drones

    def __str__(self) -> str:
        """
        Return a string representation of the Zone.
        """
        return f"Zone({self.name}, type={self.zone_type}, max={self.max_drones})"
