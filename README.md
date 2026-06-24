*This project has been created as part of the 42 curriculum by mosiraj-.*

## Description

**Fly-in** is a drone routing simulation system. Given a network of connected zones and a fleet of drones, it computes optimal paths from a start hub to an end hub, routes all drones simultaneously, and outputs a step-by-step simulation log in the fewest possible turns.

Key features:
- Weighted A* pathfinding with zone type costs (normal=1, restricted=2, priority=1)
- Yen's k-shortest paths algorithm for multi-path drone distribution
- Zone and connection capacity enforcement
- Multi-turn transit mechanics for restricted zones
- Colored terminal output showing drone movements and zone states

## Instructions

### Requirements

- Python 3.10+
- `flake8` and `mypy` (installed via `make install`)

### Installation

```bash
make install
```

### Running the Simulation

```bash
make run MAP=maps/example.map
# or
python3 -m src.main <path_to_map>
```

### Debug Mode

```bash
make debug MAP=maps/example.map
```

### Linting

```bash
make lint          # flake8 + mypy standard
make lint-strict   # mypy --strict
```

### Cleanup

```bash
make clean
```

## Algorithm

### Pathfinding

The system uses **weighted A*** (A-star) with Manhattan distance as the heuristic and zone movement costs as edge weights. This finds the shortest-cost path while respecting blocked zones.

For multi-drone routing, **Yen's k-shortest paths** algorithm generates up to k distinct paths. Drones are distributed round-robin across these paths to maximize throughput and minimize bottlenecks.

Complexity:
- A*: O((V + E) log V) per query
- Yen's k-paths: O(k · V · (V + E) log V)
- Paths are computed once and cached — no per-turn recalculation

### Simulation Engine

Each turn proceeds in two phases:

1. **Transit resolution**: Drones mid-flight toward restricted zones tick their timer. Arriving drones are placed in the destination zone and cannot move again that same turn.
2. **Move scheduling**: Waiting drones attempt to advance one step. Zone and connection capacities are checked optimistically (departing drones free their slot on the same turn). Restricted-zone moves begin a 2-turn transit.

Deadlock prevention: drones wait rather than block — they retry each turn until capacity is available.

### Zone Types

| Type | Cost | Notes |
|------|------|-------|
| normal | 1 turn | Default |
| priority | 1 turn | Preferred in pathfinding |
| restricted | 2 turns | Drone occupies connection during transit |
| blocked | — | Inaccessible; excluded from all paths |

## Visual Representation

Terminal output uses ANSI colors:
- Each drone is assigned a distinct color for easy tracking
- Zone summary uses zone-type and metadata colors (red=restricted, green=priority, etc.)
- Bold headers separate sections

## Resources

- [Dijkstra's / A* algorithm](https://en.wikipedia.org/wiki/A*_search_algorithm)
- [Yen's k-shortest paths](https://en.wikipedia.org/wiki/Yen%27s_k-shortest_path_algorithm)
- [Python type hints — PEP 484](https://peps.python.org/pep-0484/)
- [PEP 257 — Docstring conventions](https://peps.python.org/pep-0257/)
- [flake8 documentation](https://flake8.pycqa.org/)
- [mypy documentation](https://mypy.readthedocs.io/)

**AI usage**: AI was used to assist with initial code scaffolding and docstring formatting. All algorithmic logic (A*, Yen's, simulation turn mechanics, capacity rules) was designed, reviewed, and validated manually.
