COLOR_CODES = {"red": "\033[91m", "green": "\033[92m", "blue": "\033[94m",
               "yellow": "\033[93m", "gray": "\033[90m", "none": "\033[0m"}
RESET = "\033[0m"


def colorize(text: str, color: str) -> str:
    return f"{COLOR_CODES.get(color, RESET)}{text}{RESET}"


def print_turn(turn_number: int, line: str) -> None:
    print(colorize(f"[Turn {turn_number}] ", "blue") + line)