# 🗺️ Fly-in Project — One Day Implementation Plan

> **Goal:** Build a drone routing simulation from scratch in one structured day.
> **Language:** Python 3.10+  |  **Style:** Object-Oriented, type-safe (mypy + flake8)

---

## 📋 How to Use This Plan

- Work **top to bottom** — each phase builds on the previous one.
- When you see a 🔬 **Research Checkpoint**, **stop and study** before coding.
  You must understand the concept before using it.
- When you see a ✅ **Test**, run it and verify it passes before moving on.
- Each task has an estimated time — adjust to your pace, but respect the order.
- Check boxes as you go: `- [ ]` → `- [x]`

---

## ⏰ Day Schedule Overview

| Time        | Phase                          | What you build              |
|-------------|--------------------------------|-----------------------------|
| 08:00–09:00 | Phase 0 — Setup & Analysis     | Environment + understanding |
| 09:00–10:30 | Phase 1 — Data Models          | Zone, Connection, Network   |
| 10:30–12:00 | Phase 2 — Map Parser           | MapParser                   |
| 12:00–13:00 | 🥗 Lunch Break                  | —                           |
| 13:00–14:30 | Phase 3 — Pathfinding          | Pathfinder (Dijkstra)       |
| 14:30–16:30 | Phase 4 — Simulation           | Drone, Simulation           |
| 16:30–17:30 | Phase 5 — Visual Output        | Visualizer + terminal color |
| 17:30–18:30 | Phase 6 — Main & Makefile      | main.py + Makefile          |
| 18:30–19:30 | Phase 7 — Testing & Lint       | All maps + mypy + flake8    |

---

## Phase 0 — Setup & Analysis (08:00–09:00)
### الهدف: فهم المشروع كاملاً قبل كتابة أي كود

---

### 0.1 — Read the Subject
- [ ] Read the PDF subject fully (focus on Chapter V, VI, VII)
- [ ] Write down in your own words (in a comment or notes):
  - What is a Zone? What types exist? (normal / restricted / priority / blocked)
  - What is a Connection? What is `max_link_capacity`?
  - What is `max_drones`?
  - What does a simulation "turn" mean?
  - What is the output format? (e.g. `D1-zone1 D2-zone2`)
  - What is a restricted zone's special behavior? (2 turns)

> 📝 **Note:** If you cannot explain each concept above in one sentence,
> re-read that section before continuing.

---

### 0.2 — Environment Setup
- [ ] Create and activate a virtual environment:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
  > **What is venv?** (ما هو الـ virtual environment؟)
  > It's an isolated Python installation for your project so packages
  > you install don't conflict with other projects on your machine.

- [ ] Install required tools:
  ```bash
  pip install mypy flake8 matplotlib
  ```

- [ ] Verify installation:
  ```bash
  python3 -c "import matplotlib; print('matplotlib OK')"
  mypy --version
  flake8 --version
  ```

---

### 0.3 — Read the Sample Maps
- [ ] Open and read these files manually:
  - `maps/easy/01_linear_path.txt`
  - `maps/easy/02_simple_fork.txt`
  - `maps/medium/03_priority_puzzle.txt`
- [ ] Sketch the graph on paper (circles = zones, lines = connections)
- [ ] Answer: How many drones? Where do they start? Where do they go?

✅ **Exit check for Phase 0:**
You can draw the `02_simple_fork.txt` map on paper and explain
what a valid simulation output would look like.

---

## Phase 1 — Data Models (09:00–10:30)
### الهدف: بناء الكلاسات الأساسية التي تمثل بيانات الخريطة

These are "dumb" classes — they only hold data, no logic yet.
Build them one by one, test each before moving on.

---

### 1.1 — Create `src/zone.py`

**What it represents:** A single location on the map (a node in the graph).
**يمثل:** موقع واحد على الخريطة (عقدة في الغراف).

- [ ] Create `src/zone.py`
- [ ] Define class `Zone` with these attributes:
  ```
  name: str          — unique zone name (e.g. "hub", "roof1")
  x: int             — X coordinate (for drawing)
  y: int             — Y coordinate (for drawing)
  zone_type: str     — "normal" | "restricted" | "priority" | "blocked"
  color: str | None  — display color (optional)
  max_drones: int    — max drones allowed here at once (default: 1)
  ```
- [ ] Add a class-level constant: `VALID_TYPES = ["normal", "restricted", "priority", "blocked"]`
- [ ] Add method `movement_cost(self) -> int`:
  - returns `2` if `zone_type == "restricted"`, else `1`
- [ ] Add method `is_blocked(self) -> bool`:
  - returns `True` if `zone_type == "blocked"`
- [ ] Add `__str__` method for easy printing

> 🔬 **Research Checkpoint — Type Hints (مدة: 10 دقائق)**
> Search: "Python type hints Optional" — understand:
> - What does `Optional[str]` mean? (str OR None)
> - Why do we write `-> None` on `__init__`?
> - What is `from typing import Optional`?
> Make sure you can explain this before continuing.

✅ **Test 1.1** — run this in a Python shell:
```python
from zone import Zone
z = Zone("roof1", 3, 4, zone_type="restricted", color="red")
print(z)                     # Zone(roof1, type=restricted, max_drones=1)
print(z.movement_cost())     # 2
print(z.is_blocked())        # False
z2 = Zone("wall", 0, 0, zone_type="blocked")
print(z2.is_blocked())       # True
```

---

### 1.2 — Create `src/connection.py`

**What it represents:** A bidirectional link (edge) between two zones.
**يمثل:** طريق ثنائي الاتجاه بين منطقتين.

- [ ] Create `src/connection.py`
- [ ] Define class `Connection` with:
  ```
  zone1: str              — name of first zone
  zone2: str              — name of second zone
  max_link_capacity: int  — max drones on this link at once (default: 1)
  ```
- [ ] Add method `connects(self, zone_name: str) -> bool`
  - returns `True` if this connection involves `zone_name`
- [ ] Add method `other_end(self, zone_name: str) -> str`
  - given one zone, returns the zone on the other end
- [ ] Add method `key(self) -> str`
  - returns a consistent string like `"hub-roof1"` (alphabetical order)
  - use `"-".join(sorted([self.zone1, self.zone2]))`
- [ ] Add `__str__`

> 🔬 **Research Checkpoint — sorted() and join() (مدة: 5 دقائق)**
> What does `sorted(["roof1", "hub"])` return? Why?
> What does `"-".join(["hub", "roof1"])` return?
> These two together make a consistent unique key for any pair.

✅ **Test 1.2:**
```python
from connection import Connection
c = Connection("hub", "roof1", max_link_capacity=2)
print(c.connects("hub"))        # True
print(c.connects("goal"))       # False
print(c.other_end("hub"))       # roof1
print(c.other_end("roof1"))     # hub
print(c.key())                  # hub-roof1
```

---

### 1.3 — Create `src/network.py`

**What it represents:** The full map — a container for all zones and connections.
**يمثل:** الخريطة كاملة — مجموعة كل المناطق والروابط.

- [ ] Create `src/network.py`
- [ ] Import `Zone` and `Connection`
- [ ] Define class `Network` with:
  ```
  zones: dict[str, Zone]          — zone name → Zone object
  connections: list[Connection]   — all connections
  ```
- [ ] Add method `add_zone(self, zone: Zone) -> None`
- [ ] Add method `add_connection(self, conn: Connection) -> None`
- [ ] Add method `get_neighbors(self, zone_name: str) -> list[tuple[str, Connection]]`
  - loops through ALL connections
  - if the connection touches `zone_name`, add `(other_end, connection)` to result
  - returns the list
- [ ] Add method `find_connection(self, zone_a: str, zone_b: str) -> Connection | None`
  - returns the connection between two zones, or `None`

> 🔬 **Research Checkpoint — dict and list comprehension (مدة: 10 دقائق)**
> Understand: `{z: 0 for z in network.zones}` — what does this do?
> This creates a dictionary from zone names to zeros in ONE line.
> You will use this pattern in the simulation.

✅ **Test 1.3:**
```python
from zone import Zone
from connection import Connection
from network import Network

net = Network()
net.add_zone(Zone("hub", 0, 0))
net.add_zone(Zone("goal", 3, 0))
net.add_connection(Connection("hub", "goal"))

neighbors = net.get_neighbors("hub")
print(neighbors)   # [("goal", Connection(hub <-> goal, cap=1))]

conn = net.find_connection("hub", "goal")
print(conn)        # Connection(hub <-> goal, cap=1)
print(net.find_connection("hub", "nowhere"))  # None
```

✅ **Exit check for Phase 1:**
All 3 classes work independently. No imports from MapParser or Simulation yet.

---

## Phase 2 — Map Parser (10:30–12:00)
### الهدف: قراءة ملف الخريطة النصي وتحويله لكائنات Python

This is the most detail-heavy phase. Take it step by step.

---

### 2.1 — Understand the File Format

Before coding, study the format:
```
nb_drones: 2
start_hub: start 0 0 [color=green]
hub: waypoint1 1 0 [color=blue]
end_hub: goal 3 0 [color=red]
connection: start-waypoint1
connection: waypoint1-goal [max_link_capacity=2]
```

- [ ] Identify what each line **starts with** — this is your parsing trigger
- [ ] Identify the **core part** (name x y) and the **metadata part** ([key=value ...])
- [ ] Note: comments start with `#` → skip them
- [ ] Note: empty lines → skip them

---

### 2.2 — Create `src/MapParser.py`

- [ ] Create `src/MapParser.py`
- [ ] Add `import sys` at the top (needed for `sys.exit(1)` and `sys.stderr`)

> 🔬 **Research Checkpoint — sys.exit and sys.stderr (مدة: 5 دقائق)**
> What does `sys.exit(1)` do? (exits the program with error code 1)
> What is `sys.stderr`? (the error output stream — errors should go there, not stdout)
> Why write `print("Error...", file=sys.stderr)` instead of just `print("Error...")`?

- [ ] Define class `MapParser` with:
  ```
  filepath: str
  nb_drones: int = 0
  start_hub: str = ""
  end_hub: str = ""
  network: Network = Network()
  _seen_connections: set[str] = set()   ← for detecting duplicates
  ```

- [ ] Implement `parse(self) -> None`:
  - Open the file with `with open(self.filepath, "r") as f`
  - Read all lines: `lines = f.readlines()`
  - Loop with `enumerate(lines, start=1)` to track line numbers
  - For each line: strip whitespace, skip if empty or starts with `#`
  - Route each line to the correct private method based on its prefix
  - Wrap the private method call in `try/except ValueError`
    → on error: print `"Parse error on line {num}: {msg}"` then `sys.exit(1)`
  - After the loop: call `_validate()`

- [ ] Implement `_validate(self) -> None`:
  - Check `nb_drones > 0` else exit with error
  - Check `start_hub != ""` else exit with error
  - Check `end_hub != ""` else exit with error

- [ ] Implement `_parse_nb_drones(self, line: str) -> None`:
  - Split on `":"`, take second part, convert to `int`
  - Raise `ValueError` if not a positive integer

- [ ] Implement `_parse_metadata(self, meta_str: str) -> dict[str, str]`:
  - Strip `"[] "` from the string
  - Split by spaces → loop through each `"key=value"` piece
  - Split each piece on `"="`, store in dict
  - Return the dict (empty dict if no metadata)

> 🔬 **Research Checkpoint — str.split() (مدة: 5 دقائق)**
> What is the difference between:
> - `"a:b:c".split(":")` → `["a", "b", "c"]`
> - `"a:b:c".split(":", 1)` → `["a", "b:c"]`  ← splits ONLY at first `:`
> You NEED `split(":", 1)` for the metadata to avoid breaking zone names.

- [ ] Implement `_parse_zone_line(self, line: str) -> str`:
  - Split on `":"` (max 1 split) to get the part after the prefix
  - Check if `"["` exists in rest → split to get core and metadata
  - Call `_parse_metadata` on the metadata part
  - Split the core by spaces → `parts[0]` = name, `parts[1]` = x, `parts[2]` = y
  - Validate: name not already in `network.zones`
  - Get `zone_type` from metadata (default `"normal"`) — validate it's in `Zone.VALID_TYPES`
  - Get `color` from metadata (default `None`)
  - Get `max_drones` from metadata (default `1`) — validate it's a positive int
  - Create `Zone(...)` and call `network.add_zone(zone)`
  - Return the zone name (so `parse()` can set `start_hub` or `end_hub`)

- [ ] Implement `_parse_connection_line(self, line: str) -> None`:
  - Split on `":"` then check for `"["` (same pattern as zones)
  - Split core on `"-"` to get zone1 and zone2
  - Validate both zones exist in `network.zones`
  - Create `pair_key = "-".join(sorted([zone1, zone2]))`
  - Check `pair_key not in _seen_connections` → raise `ValueError` if duplicate
  - Get `max_link_capacity` from metadata (default `1`)
  - Create `Connection(...)` and call `network.add_connection(conn)`

✅ **Test 2:**
```bash
# From the src/ directory:
cd src
python3 -c "
from MapParser import MapParser
p = MapParser('../maps/easy/01_linear_path.txt')
p.parse()
print('Drones:', p.nb_drones)          # 2
print('Start:', p.start_hub)           # start
print('End:', p.end_hub)               # goal
print('Zones:', list(p.network.zones.keys()))
print('Connections:', len(p.network.connections))
# Check metadata is applied:
print('waypoint1 type:', p.network.zones['waypoint1'].zone_type)  # normal
"
```

✅ **Test 2b — Error handling:**
```bash
python3 -c "
from MapParser import MapParser
p = MapParser('../maps/easy/01_linear_path.txt')
p.parse()
# Check a priority/restricted map:
" 
python3 -c "
from MapParser import MapParser
p = MapParser('../maps/medium/03_priority_puzzle.txt')
p.parse()
print('fast_junction type:', p.network.zones['fast_junction'].zone_type)  # priority
print('slow_path1 type:', p.network.zones['slow_path1'].zone_type)       # restricted
print('merge_point max_drones:', p.network.zones['merge_point'].max_drones) # 3
"
```

✅ **Exit check for Phase 2:**
The metadata (zone type, color, max_drones) is correctly read and stored in Zone objects.

---

## 🥗 Lunch Break (12:00–13:00)

Take a full break. Don't think about code.
When you come back, you'll tackle the hardest algorithm.

---

## Phase 3 — Pathfinding (13:00–14:30)
### الهدف: إيجاد أفضل مسار بين البداية والنهاية

---

### 3.1 — Understand Dijkstra Before Coding

> 🔬 **Research Checkpoint — Dijkstra's Algorithm (مدة: 30 دقائق)**
> This is the most important algorithm in this project.
> Do NOT skip this. Study until you can explain it yourself.
>
> **Watch/Read one of these:**
> - Search: "Dijkstra's algorithm explained visually"
> - Or draw it by hand on paper using this example:
>   ```
>   start --(cost 1)--> A --(cost 2)--> goal
>   start --(cost 1)--> B --(cost 1)--> goal
>   ```
>   The answer is: start → B → goal (total cost 2, not 3)
>
> **Key ideas to understand:**
> - We use a Priority Queue (heap) — always process the CHEAPEST node next
> - We keep a `visited` set — never re-process a node we've already finalized
> - Each step: pop cheapest, look at neighbors, push them with (my_cost + step_cost)
> - When we reach the destination: we're DONE (it's the cheapest path)
>
> 🔬 **Research Checkpoint — heapq (مدة: 10 دقائق)**
> Search: "Python heapq tutorial"
> Understand:
> - `heapq.heappush(heap, (cost, item))` — adds item with priority
> - `heapq.heappop(heap)` — removes and returns the LOWEST cost item
> - Python's heap is a MIN-heap (smallest value comes out first)
> - We store tuples `(cost, zone_name, path)` — Python compares tuples left to right

---

### 3.2 — Create `src/pathfinder.py`

- [ ] Create `src/pathfinder.py`
- [ ] Import `heapq`, `Optional`, `Network`
- [ ] Define class `Pathfinder` with `network: Network` in `__init__`

- [ ] Implement `find_path(self, start: str, end: str) -> Optional[list[str]]`:

  ```
  Step 1: Validate start and end exist in network.zones
          Return None if either is missing.

  Step 2: Initialize the heap with the starting point:
          heap = [(0.0, start, [start])]
          Each entry: (accumulated_cost, current_zone, path_so_far)

  Step 3: Initialize best_cost = {} (empty dict)
          This stores the cheapest cost found to reach each zone.

  Step 4: While heap is not empty:
            cost, current, path = heapq.heappop(heap)

            If current is already in best_cost → skip (we found it cheaper before)
            Else → record: best_cost[current] = cost

            If current == end → RETURN path (we're done!)

            For each (neighbor_name, conn) in network.get_neighbors(current):
              If neighbor in best_cost → skip
              neighbor_zone = network.zones[neighbor_name]
              If neighbor_zone.is_blocked() → skip

              Determine step_cost:
                - restricted → 2.0
                - priority   → 0.9  (same real cost as normal, but preferred)
                - normal     → 1.0

              new_cost = cost + step_cost
              new_path = path + [neighbor_name]
              heapq.heappush(heap, (new_cost, neighbor_name, new_path))

  Step 5: Return None (heap exhausted, no path found)
  ```

✅ **Test 3:**
```python
from MapParser import MapParser
from pathfinder import Pathfinder

p = MapParser('../maps/easy/01_linear_path.txt')
p.parse()
finder = Pathfinder(p.network)
path = finder.find_path('start', 'goal')
print(path)  # ['start', 'waypoint1', 'waypoint2', 'goal']

# Test with fork map — should find a valid path
p2 = MapParser('../maps/easy/02_simple_fork.txt')
p2.parse()
finder2 = Pathfinder(p2.network)
path2 = finder2.find_path('start', 'goal')
print(path2)  # one of: ['start','junction','path_a','goal'] or via path_b

# Test with priority map — should prefer fast_junction path
p3 = MapParser('../maps/medium/03_priority_puzzle.txt')
p3.parse()
finder3 = Pathfinder(p3.network)
path3 = finder3.find_path('start', 'goal')
print(path3)  # should include fast_junction (priority zones are preferred)
```

✅ **Exit check for Phase 3:**
- Returns correct path for linear map ✓
- Avoids blocked zones ✓
- Prefers priority zones over normal ✓
- Returns `None` for impossible maps ✓

---

## Phase 4 — Simulation (14:30–16:30)
### الهدف: تحريك الطائرات جولة بجولة مع احترام القواعد

This is the most complex phase. Two classes: `Drone` then `Simulation`.

---

### 4.1 — Understand the Rules First

Read Chapter VII of the PDF again, focusing on:
- [ ] Zone occupancy rules (max_drones)
- [ ] Connection capacity rules (max_link_capacity)
- [ ] Restricted zone rule (2 turns — drone is "in transit" on turn 1, arrives turn 2)
- [ ] Key rule: "drones moving OUT of a zone free up capacity for THAT SAME TURN"

> **Concrete example of the capacity rule:**
> ```
> Zone A has max_drones=1. D1 is in A. D2 wants to enter A. D1 wants to leave A.
> → On this turn: D1 leaves A (freeing 1 space) AND D2 enters A (using 1 space)
> → Net: A still has 1 drone — VALID. Both moves happen.
> ```
> This means when checking if D2 can enter A, you must subtract D1's departure first.

---

### 4.2 — Create `src/drone.py`

**State machine for a drone:**
```
Normal move:     current_zone="A" → move_to("B") → current_zone="B"
Restricted move: current_zone="A" → start_transit_to("B") → in_transit=True
Next turn:       in_transit=True → complete_transit() → current_zone="B", in_transit=False
```

- [ ] Create `src/drone.py`
- [ ] Define class `Drone` with:
  ```
  id: str                     — "D1", "D2", etc.
  current_zone: str           — where the drone IS right now
  path: list[str] = []        — planned route
  path_index: int = 0         — position in path
  in_transit: bool = False    — True when mid-transit to restricted zone
  transit_destination: str="" — where it's heading (only when in_transit=True)
  ```
- [ ] Add `set_path(self, path: list[str]) -> None`
- [ ] Add `is_done(self, end_zone: str) -> bool`
  - `return self.current_zone == end_zone and not self.in_transit`
- [ ] Add `get_next_zone(self) -> Optional[str]`
  - return `self.path[self.path_index + 1]` if it exists, else `None`
- [ ] Add `start_transit_to(self, destination: str) -> None`
  - set `in_transit = True`, `transit_destination = destination`
  - do NOT change `current_zone` or `path_index` yet
- [ ] Add `complete_transit(self) -> None`
  - set `in_transit = False`
  - increment `path_index`
  - set `current_zone = transit_destination`
  - clear `transit_destination = ""`
- [ ] Add `move_to(self, destination: str) -> None`
  - increment `path_index`
  - set `current_zone = destination`
- [ ] Add `__str__`

✅ **Test 4.1:**
```python
from drone import Drone
d = Drone("D1", "start")
d.set_path(["start", "A", "B", "goal"])

print(d.get_next_zone())    # A
d.move_to("A")
print(d.current_zone)       # A
print(d.get_next_zone())    # B

d.start_transit_to("B")
print(d.in_transit)         # True
print(d.current_zone)       # A  (still A until transit completes!)

d.complete_transit()
print(d.in_transit)         # False
print(d.current_zone)       # B

d.move_to("goal")
print(d.is_done("goal"))    # True
```

---

### 4.3 — Create `src/simulation.py`

This is the most complex file. Build it in sub-steps.

- [ ] Create `src/simulation.py`
- [ ] Import `Network`, `Drone`
- [ ] Define class `Simulation` with:
  ```
  network: Network
  end_hub: str
  drones: list[Drone]
  zone_occupancy: dict[str, int]    ← how many drones in each zone right now
  history: list[dict[str, str]]     ← snapshots for the visualizer
  MAX_TURNS = 1000                  ← class constant
  ```

- [ ] In `__init__`:
  - Create `nb_drones` Drone objects (`D1`, `D2`, ...)
  - Call `drone.set_path(path)` for each
  - Initialize `zone_occupancy`: all zeros, except `start_hub = nb_drones`
  - Call `_save_snapshot()`

- [ ] Add `run(self) -> int`:
  ```
  turn = 1
  while not _all_done():
      moves = _run_one_turn()
      if moves: print(" ".join(moves))
      _save_snapshot()
      turn += 1
      if turn > MAX_TURNS: print warning and break
  print(f"Simulation finished in {turn-1} turns.")
  return turn - 1
  ```

- [ ] Add `_all_done(self) -> bool`:
  - `return all(drone.is_done(self.end_hub) for drone in self.drones)`

- [ ] Add `_save_snapshot(self) -> None`:
  - build dict `{drone.id: drone.transit_destination if in_transit else drone.current_zone}`
  - append to `self.history`

- [ ] Add `_run_one_turn(self) -> list[str]`:
  This is the core logic. Follow these steps IN ORDER:

  ```
  Step A: Count transit arrivals (drones completing restricted transit THIS turn)
          transit_arrivals: dict[str, int] = {}
          for each drone where in_transit is True:
              transit_arrivals[drone.transit_destination] += 1

  Step B: Setup tracking variables for planned moves:
          departures: dict[str, int] = {all zones: 0}
          new_arrivals: dict[str, int] = copy of transit_arrivals
          link_usage: dict[str, int] = {}
          planned: list of (drone, destination, is_restricted)

  Step C: For each drone (not done, not in_transit):
            next_zone_name = drone.get_next_zone()
            if None → skip

            is_end_zone = (next_zone_name == end_hub)

            effective_occ = zone_occupancy[next_zone] - departures[next_zone] + new_arrivals[next_zone]
            has_zone_space = is_end_zone OR (effective_occ < next_zone.max_drones)

            conn = network.find_connection(drone.current_zone, next_zone_name)
            link_key = f"{min(from,to)}-{max(from,to)}"
            has_link_space = (link_usage[link_key] < conn.max_link_capacity)

            if NOT (has_zone_space AND has_link_space): → drone waits, skip

            Record the move:
              departures[drone.current_zone] += 1
              link_usage[link_key] += 1
              if NOT restricted: new_arrivals[next_zone] += 1
              planned.append((drone, next_zone_name, is_restricted))

  Step D: Apply transit completions (Phase A drones arrive):
            for each drone in_transit:
              drone.complete_transit()
              moves.append(f"{drone.id}-{drone.current_zone}")

  Step E: Apply planned moves (Phase B):
            for (drone, dest, is_restricted) in planned:
              from_zone = drone.current_zone
              if is_restricted:
                drone.start_transit_to(dest)
                moves.append(f"{drone.id}-{from_zone}-{dest}")
              else:
                drone.move_to(dest)
                moves.append(f"{drone.id}-{dest}")

  Step F: Rebuild zone_occupancy from scratch:
            zone_occupancy = {all zones: 0}
            for each drone not in_transit:
              zone_occupancy[drone.current_zone] += 1

  Return moves
  ```

✅ **Test 4 — Full integration test:**
```bash
cd src
python3 -c "
from MapParser import MapParser
from pathfinder import Pathfinder
from simulation import Simulation

p = MapParser('../maps/easy/01_linear_path.txt')
p.parse()

finder = Pathfinder(p.network)
path = finder.find_path(p.start_hub, p.end_hub)
print('Path:', path)

sim = Simulation(p.network, p.nb_drones, p.start_hub, p.end_hub, path)
turns = sim.run()
print('Total turns:', turns)
# Expected output:
# D1-waypoint1
# D1-waypoint2 D2-waypoint1
# D1-goal D2-waypoint2
# D2-goal
# Total turns: 4
"
```

✅ **Test 4b — Restricted zones:**
```bash
python3 -c "
from MapParser import MapParser
from pathfinder import Pathfinder
from simulation import Simulation

p = MapParser('../maps/medium/03_priority_puzzle.txt')
p.parse()
finder = Pathfinder(p.network)
path = finder.find_path(p.start_hub, p.end_hub)
print('Path:', path)
sim = Simulation(p.network, p.nb_drones, p.start_hub, p.end_hub, path)
sim.run()
"
```

✅ **Exit check for Phase 4:**
- Linear map: runs in ≤ 6 turns ✓
- No two drones in same zone at same time (unless max_drones > 1) ✓
- Restricted zones cause drone to appear in transit for 1 turn ✓

---

## Phase 5 — Visual Output (16:30–17:30)
### الهدف: عرض مرئي للمحاكاة

---

### 5.1 — Terminal Color Output (Simple)

Add colored terminal output to see drone movements clearly.

> 🔬 **Research Checkpoint — ANSI color codes (مدة: 5 دقائق)**
> Search: "Python ANSI color codes terminal"
> Understand:
> - `"\033[92m"` = green text
> - `"\033[0m"`  = reset to normal
> - `print("\033[92m" + "hello" + "\033[0m")` prints green "hello"
> These are built into the terminal — no library needed.

- [ ] In `simulation.py`, modify the print in `run()` to use colors:
  ```python
  # Example: print turn header in yellow, moves in white
  print(f"\033[93mTurn {turn}:\033[0m {' '.join(moves)}")
  ```

---

### 5.2 — Create `src/visualizer.py`

> 🔬 **Research Checkpoint — matplotlib basics (مدة: 20 دقائق)**
> Run this in a Python shell and study what each line does:
> ```python
> import matplotlib.pyplot as plt
> fig, ax = plt.subplots()
> ax.scatter(0, 0, s=1000, c='green')     # draw a circle at (0,0)
> ax.scatter(3, 0, s=1000, c='red')       # draw a circle at (3,0)
> ax.plot([0, 3], [0, 0], 'k-')           # draw a line from (0,0) to (3,0)
> ax.text(0, 0, "start", ha='center')     # label
> plt.show()
> ```
> Understand: `ax.scatter`, `ax.text`, `ax.add_patch`, `plt.pause`, `plt.ion`

- [ ] Create `src/visualizer.py`
- [ ] Import `matplotlib.pyplot as plt`, `FancyArrowPatch`, `Network`
- [ ] Define `ZONE_TYPE_COLORS` dict at the top (outside the class):
  ```python
  ZONE_TYPE_COLORS = {
      "normal": "lightblue",
      "restricted": "salmon",
      "priority": "lightgreen",
      "blocked": "dimgray",
  }
  ```
- [ ] Define class `Visualizer` with `network` and `history` in `__init__`
- [ ] Implement `animate(self) -> None`:
  - `plt.ion()` — enable interactive mode
  - Create figure with `plt.subplots(figsize=(12, 8))`
  - Call `_draw_connections(ax)` once
  - Call `_draw_zones(ax)` once
  - Setup empty `drone_markers: list = []`
  - Loop over `enumerate(self.history)`:
    - Remove old markers
    - Draw each drone as a scatter point (diamond marker `"D"`)
    - Update title with turn number
    - `plt.draw()` and `plt.pause(0.6)`
  - `plt.ioff()` then `plt.show()`

- [ ] Implement `_draw_connections(self, ax) -> None`:
  - Keep a `drawn: set[str]` to avoid drawing each connection twice
  - For each zone, get neighbors, for each use `FancyArrowPatch` with `arrowstyle="<|-|>"`

- [ ] Implement `_draw_zones(self, ax) -> None`:
  - For each zone: use `zone.color` if set, else look up in `ZONE_TYPE_COLORS`
  - `ax.scatter(zone.x, zone.y, s=4000, c=color, ...)`
  - `ax.text(zone.x, zone.y, zone.name, ha='center', va='center', ...)`

✅ **Test 5:**
Run `make run` — you should see:
1. Terminal output with turn-by-turn moves
2. A matplotlib window animating drone positions

---

## Phase 6 — Main & Makefile (17:30–18:30)
### الهدف: ربط كل شيء معاً في نقطة دخول واحدة

---

### 6.1 — Create `src/main.py`

- [ ] Create `src/main.py`
- [ ] Import: `sys`, `MapParser`, `Pathfinder`, `Simulation`, `Visualizer`
- [ ] Define `def main() -> None:`
- [ ] Add: `if __name__ == "__main__": main()`

- [ ] In `main()`:
  1. Check `len(sys.argv) != 2` → print usage and `sys.exit(1)`
  2. `map_file = sys.argv[1]`
  3. Parse: `parser = MapParser(map_file)` then `parser.parse()`
  4. Print summary (drones, zones, connections count)
  5. Find path: `finder = Pathfinder(parser.network)` then `path = finder.find_path(...)`
  6. If `path is None` → print error and exit
  7. Print the path
  8. Run simulation: `sim = Simulation(...)` then `sim.run()`
  9. Run visualizer in `try/except` (so it's optional):
     ```python
     try:
         vis = Visualizer(parser.network, sim.history)
         vis.animate()
     except Exception as e:
         print(f"Visualizer could not run: {e}")
     ```

---

### 6.2 — Update Makefile

- [ ] Verify the Makefile has:
  ```makefile
  PYTHON = python3
  MAIN = src/main.py

  install:
      $(PIP) install mypy flake8 matplotlib

  run:
      $(PYTHON) $(MAIN) maps/easy/01_linear_path.txt

  debug:
      $(PYTHON) -m pdb $(MAIN) maps/easy/01_linear_path.txt

  clean:
      find . -type d -name "__pycache__" -exec rm -r {} +
      rm -rf .mypy_cache

  lint:
      flake8 src/
      mypy src/ --warn-return-any --warn-unused-ignores \
          --ignore-missing-imports --disallow-untyped-defs \
          --check-untyped-defs

  lint-strict:
      flake8 src/
      mypy src/ --strict
  ```

✅ **Test 6:**
```bash
make run     # should run and show animation
make debug   # should drop into pdb debugger
make clean   # should remove __pycache__ folders
```

---

## Phase 7 — Testing & Lint (18:30–19:30)
### الهدف: التأكد أن كل شيء يعمل بدون أخطاء

---

### 7.1 — Run All Maps

Run the program on every provided map and record the turn count:

| Map | Expected (from PDF) | Your result | Status |
|-----|--------------------|-----------  |--------|
| `maps/easy/01_linear_path.txt`       | ≤ 6 turns  | ___  | ⬜ |
| `maps/easy/02_simple_fork.txt`       | ≤ 8 turns  | ___  | ⬜ |
| `maps/easy/03_basic_capacity.txt`    | ≤ 6 turns  | ___  | ⬜ |
| `maps/medium/01_dead_end_trap.txt`   | ≤ 12 turns | ___  | ⬜ |
| `maps/medium/02_circular_loop.txt`   | ≤ 15 turns | ___  | ⬜ |
| `maps/medium/03_priority_puzzle.txt` | ≤ 12 turns | ___  | ⬜ |
| `maps/hard/01_maze_nightmare.txt`    | ≤ 30 turns | ___  | ⬜ |
| `maps/hard/02_capacity_hell.txt`     | ≤ 35 turns | ___  | ⬜ |
| `maps/hard/03_ultimate_challenge.txt`| ≤ 45 turns | ___  | ⬜ |

```bash
# Run all maps quickly:
for f in maps/easy/*.txt maps/medium/*.txt maps/hard/*.txt; do
    echo "=== $f ==="
    python3 src/main.py "$f" 2>&1 | grep -E "Turn|Simulation finished"
done
```

---

### 7.2 — Run Linter (flake8)

> 🔬 **What is flake8?**
> A tool that checks your code style — spacing, line length, unused imports, etc.
> The project REQUIRES it to pass.

```bash
make lint   # or: flake8 src/
```

Common flake8 errors and fixes:
| Error | Meaning | Fix |
|-------|---------|-----|
| `E302` | expected 2 blank lines before function | add blank lines |
| `E501` | line too long (>79 chars) | split the line |
| `F401` | imported but unused | remove the import |
| `W291` | trailing whitespace | remove spaces at end of lines |

- [ ] Fix all flake8 errors (zero errors required)

---

### 7.3 — Run Type Checker (mypy)

> 🔬 **What is mypy?**
> A tool that checks your type hints are correct — catches bugs before running.
> Example: if a function says `-> int` but returns `None`, mypy will catch it.

```bash
mypy src/ --warn-return-any --warn-unused-ignores \
    --ignore-missing-imports --disallow-untyped-defs \
    --check-untyped-defs
```

Common mypy errors and fixes:
| Error | Meaning | Fix |
|-------|---------|-----|
| `error: Missing return statement` | function says `-> str` but has no return | add return |
| `error: Argument 1 has incompatible type "None"` | passed None where str expected | add None check |
| `error: Function is missing a return type annotation` | no `-> None` on function | add `-> None` |

- [ ] Fix all mypy errors (zero errors required)

---

### 7.4 — Final Checklist

- [ ] `make run` works and shows correct output + animation
- [ ] `make lint` passes with zero errors
- [ ] `mypy src/` passes with zero errors
- [ ] All easy maps run in ≤ benchmark turns
- [ ] No `print` statements left for debugging (only intended output)
- [ ] No hardcoded file paths (always use `sys.argv[1]`)
- [ ] Every function has a type hint on every parameter and return value
- [ ] Every class and function has a docstring

---

## 🎯 End of Day Summary

When you finish, you will have built:

```
src/
├── zone.py          — Zone class (data model)
├── connection.py    — Connection class (data model)
├── network.py       — Network class (graph container)
├── MapParser.py     — File parser (text → objects)
├── pathfinder.py    — Pathfinder class (Dijkstra algorithm)
├── drone.py         — Drone class (state machine)
├── simulation.py    — Simulation class (turn engine)
├── visualizer.py    — Visualizer class (matplotlib animation)
└── main.py          — Entry point (connects everything)
```

**Concepts you will have practiced:**
- Object-Oriented Programming (classes, methods, attributes)
- Python type hints (str, int, Optional, list, dict, tuple)
- File I/O (reading text files line by line)
- Graph algorithms (Dijkstra with heapq)
- Simulation logic (turn-based, capacity constraints)
- Python standard library: `sys`, `heapq`, `typing`
- External library: `matplotlib`
- Code quality: `flake8` + `mypy`

**Algorithms you will understand:**
- Dijkstra's shortest path
- Priority Queue (min-heap)
- Greedy capacity checking in simulation turns
