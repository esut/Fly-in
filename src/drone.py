class Drone:
    
    def __init__(self, drone_id: str, start_zone: str, path: list[str]) -> None:
     
        self.id = drone_id
        self.current_zone = start_zone
        self.path = path
        self.path_index = 0  

    def is_finished(self, end_zone: str) -> bool:
        return self.current_zone == end_zone

    def get_next_zone(self) -> str | None:
        if self.path_index + 1 < len(self.path):
            return self.path[self.path_index + 1]
        return None
        
    def move_forward(self) -> None:
        if self.get_next_zone():
            self.path_index += 1
            self.current_zone = self.path[self.path_index]