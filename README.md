*This project has been created as part of the 42 curriculum by mosiraj-.*

# Fly-in — Drone Routing Simulation

## Description

Fly-in is a drone routing simulation system written in Python 3.10+.

The goal is to move a fleet of drones from a start zone to an end zone through a network of connected zones, in the **fewest possible simulation turns**, while respecting strict movement and capacity constraints.

The system reads a map file defining zones and connections, finds the optimal path using a **BFS pathfinding algorithm**, then simulates the movement of all drones turn by turn with a **snapshot-based collision engine**.

---

## Features

- Map parser supporting zones, connections, and metadata (`color`, `zone type`, `max_drones`, `max_link_capacity`)
- BFS pathfinding to find the shortest route
- Turn-based simulation engine with capacity enforcement (zone and link)
- Colored terminal output showing drone movements per turn
- Fully type-annotated codebase (compatible with `mypy`)
- `flake8`-compliant code style

---

## Project Structure

```
Fly-in_v3/
├── main.py          # Entry point
├── mapParse.py      # Map file parser
├── models.py        # Zone, Connection, Drone classes
├── graph.py         # Graph data structure
├── pathfinder.py    # BFS pathfinding algorithm
├── simulation.py    # Turn-based simulation engine
├── display.py       # Colored terminal output
├── maps/            # Provided map files (easy / medium / hard)
├── Makefile
└── README.md
```

---

## Instructions

### Requirements

- Python 3.10 or later
- `flake8` and `mypy` (installed via `make install`)

### Installation

```bash
make install
```

### Run

```bash
make run
# or with a specific map:
python3 main.py maps/hard/01_maze_nightmare.txt
```

### Debug

```bash
make debug
```

### Lint

```bash
make lint
```

### Clean

```bash
make clean
```

---

## Output Format

Each simulation turn is printed as one line listing all drone movements:

```
D1-roof1 D2-corridorA
D1-roof2 D2-tunnelB
D1-goal D2-goal
```

- `D<ID>` — unique drone identifier
- `<zone>` — destination zone name
- Drones that do not move in a given turn are omitted
- Drones that reach the end zone are no longer tracked

Terminal output is color-coded:
- Zone names appear in their map-defined color (green, blue, red, etc.)
- Drone IDs are displayed in cyan
- Turn numbers are displayed in gray

---

## Algorithm

### Pathfinding — BFS (Breadth-First Search)

The system uses **BFS** to find the shortest path (fewest zones) from the start hub to the end hub.

BFS explores all zones reachable in 1 step before exploring zones reachable in 2 steps, and so on. This guarantees the first path found is always the shortest.

```
queue = [["start"]]

Turn 1: explore neighbors of "start" → add ["start", "A"]
Turn 2: explore neighbors of "A"     → add ["start", "A", "B"], ["start", "A", "C"]
...
When current_zone == end → return path
```

### Simulation — Snapshot Approach

At each turn:

1. **Snapshot** — record how many drones are in each zone
2. **Plan** — for each drone, check if it can move:
   - Is the link capacity available?
   - Is the destination zone capacity available? (accounting for drones already planned to leave that zone this turn)
3. **Commit** — apply all valid moves simultaneously

This prevents the sequential-update bug where a drone that already moved in the current turn blocks another drone from entering the zone it just vacated.

### Zone and Link Capacity

- `max_drones=N` — at most N drones can occupy a zone simultaneously (default: 1)
- `max_link_capacity=N` — at most N drones can traverse a connection per turn (default: 1)
- **Start** and **end** zones have unlimited capacity

---

## Visual Representation

The terminal output uses ANSI escape codes to color-code the simulation:

| Element | Color |
|---------|-------|
| Zone names | As defined in map file |
| Drone IDs (D1, D2...) | Cyan |
| Turn counter | Gray |
| Total turns | Green |

Example output:
```
=== FLY-IN SIMULATION ===
Drones  : 5
Path    : start → corridorA → tunnelB → goal
Steps   : 3
────────────────────────────────────────
[Turn   1]  D1-corridorA D2-corridorA
[Turn   2]  D1-tunnelB D2-tunnelB D3-corridorA
[Turn   3]  D1-goal D2-goal D3-tunnelB
────────────────────────────────────────
Total turns: 5
```

---

## Resources

### References

- [BFS Algorithm — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Python `collections.deque` — Official Docs](https://docs.python.org/3/library/collections.html#collections.deque)
- [ANSI Escape Codes — Wikipedia](https://en.wikipedia.org/wiki/ANSI_escape_code)
- [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/)
- [mypy — Static Type Checker](https://mypy.readthedocs.io/)
- [flake8 — Style Guide Enforcement](https://flake8.pycqa.org/)

### AI Usage

AI (Claude) was used during this project for the following tasks:

- **Explaining concepts**: BFS algorithm, graph data structures, simulation mechanics
- **Debugging**: identifying the infinite-loop bug in the sequential simulation approach, fixing syntax errors in `mapParse.py`
- **Code review**: suggesting the snapshot-based approach for the simulation engine
- **Documentation**: generating explanation files for each module

All AI-generated code was reviewed, tested, and understood before being integrated into the project. The core logic, architecture decisions, and debugging were done collaboratively with full understanding of each component.
