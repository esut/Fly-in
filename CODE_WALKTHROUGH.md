# Fly-in — Complete Code Walkthrough

> A line-by-line explanation of the **Fly-in Drone Routing Simulation** project.
> Everything below is based on the actual files in this folder, with line numbers
> taken directly from the source (`cat -n` verified).

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Project Structure](#project-structure)
3. [End-to-End Data Flow](#end-to-end-data-flow)
4. [The Map File Format](#the-map-file-format)
5. [Module-by-Module Walkthrough](#module-by-module-walkthrough)
   - [models.py — data models](#modelspy--data-models)
   - [graph.py — the graph data structure](#graphpy--the-graph-data-structure)
   - [pathfinder.py — BFS pathfinding](#pathfinderpy--bfs-pathfinding)
   - [mapParse.py — map file parser](#mapparsepy--map-file-parser)
   - [simulation.py — the turn-based engine](#simulationpy--the-turn-based-engine)
   - [display.py — colored terminal output](#displaypy--colored-terminal-output)
   - [main.py — entry point](#mainpy--entry-point)
6. [Supporting Files](#supporting-files)
7. [A Worked Example](#a-worked-example)
8. [Observations, Quirks & Potential Issues](#observations-quirks--potential-issues)
9. [Glossary](#glossary)

---

## Project Overview

Fly-in is a **drone routing simulation** written in Python 3.13 (a 42 school project by
`mosiraj-`). It answers the question:

> Given a map of *zones* connected by *links*, move a fleet of *drones* from a start
> zone to an end zone in the fewest possible turns, while respecting **capacity limits**
> (how many drones fit in a zone, and how many may cross a link per turn).

The program does three things, in order:

1. **Parse** a text map file (`mapParse.py` → `models.py`).
2. **Find paths** from start to end using a breadth-first search that enumerates
   every simple path and sorts them by cost (`pathfinder.py` on top of `graph.py`).
3. **Simulate** the drones turn by turn, moving as many as possible each turn under
   the capacity rules (`simulation.py`, rendered by `display.py`).

The whole thing is orchestrated by `main.py`.

### Verification

Running the program on the easiest map produces this real output:

```text
$ python3 main.py maps/easy/01_linear_path.txt

=== FLY-IN SIMULATION ===
Drones  : 2
────────────────────────────────────────
D1-waypoint1
D1-waypoint2 D2-waypoint1
D1-goal D2-waypoint2
D2-goal

Total turns: 4
```

Two drones travel `start → waypoint1 → waypoint2 → goal`, one zone per turn, and the
simulation finishes in 4 turns. This file explains exactly how that happens.

---

## Project Structure

```
fly-in/
├── main.py          # Entry point: wires everything together
├── models.py        # Zone, Connection classes + ParseError exception
├── graph.py         # Graph data structure (zones + adjacency lists)
├── pathfinder.py    # BFS algorithm: finds all simple paths, cheapest first
├── mapParse.py      # Parses .txt map files into Zone/Connection objects
├── simulation.py    # Turn-based drone movement engine (capacity rules)
├── display.py       # ANSI-colored terminal output (Color + Display)
├── maps/            # Map files (easy / medium / hard / challenger)
├── Makefile         # install / run / debug / clean / lint targets
├── pyproject.toml   # uv project metadata (requires Python >= 3.13)
├── uv.lock          # uv dependency lockfile
├── .python-version  # pins Python 3.13
├── .gitignore       # ignores __pycache__, .venv, maps/, etc.
└── README.md        # Project readme (goal, usage, algorithm notes)
```

The modules form a strict dependency chain (no circular imports):

```
main.py
  └─ mapParse.py ──> models.py
  └─ graph.py   ──> models.py
  └─ pathfinder.py ──> graph.py
  └─ simulation.py ──> display.py, graph.py, models.py
```

---

## End-to-End Data Flow

```
┌──────────────┐    ┌──────────────────┐    ┌──────────────┐    ┌─────────────────┐
│  map file    │───▶│  MapParse.parse()│───▶│  Graph       │───▶│  Pathfinder     │
│  (.txt)      │    │  (mapParse.py)   │    │  (graph.py)  │    │  .find_all_paths│
└──────────────┘    └──────────────────┘    └──────────────┘    └────────┬────────┘
                                                                         │ list of paths
     ┌───────────────────────────────────────────────────────────────────┘
     ▼
┌──────────────┐    ┌──────────────────┐    ┌───────────────────────────────┐
│  Simulation  │◀───│  main.py picks   │    │  Display (colored turn logs)  │
│  .run()      │    │  top-2 paths,    │    └───────────────────────────────┘
│ (simulation  │    │  assigns drones  │
│  .py)        │    │  round-robin     │
└──────────────┘    └──────────────────┘
```

1. `MapParse(map_file).parse()` reads the text file and produces
   `(nb_drones, zones, start, end, connections)`.
2. `build_graph()` converts zones + connections into a `Graph` (adjacency lists).
3. `Pathfinder(graph).find_all_paths(start, end)` returns **every** simple path from
   start to end, sorted by total *entry cost* (cheapest first).
4. `main.py` keeps the **two cheapest** paths and assigns drones to them round-robin
   (drone 1 → path A, drone 2 → path B, drone 3 → path A, …).
5. `Simulation(...).run()` moves drones along their assigned paths turn by turn,
   respecting zone and link capacity, until all drones reach the end.
6. `Display` prints the header and one line per turn of the form `D1-zone D2-zone`.
7. `main.py` prints `Total turns: N`.

---

## The Map File Format

Before diving into code, here is the input format the parser expects. Example
(`maps/easy/02_simple_fork.txt`):

```text
start_hub: start 0 0 [color=green]
hub: junction 1 0 [color=yellow max_drones=2]
hub: path_a 2 1 [color=blue]
hub: path_b 2 -1 [color=blue]
end_hub: goal 3 0 [color=red]

connection: start-junction [max_link_capacity=2]
connection: junction-path_a
```

| Directive | Format | Meaning |
|---|---|---|
| `nb_drones: N` | `nb_drones: 5` | How many drones to simulate |
| `start_hub: ...` | `start_hub: name x y [meta]` | The zone drones start in |
| `end_hub: ...` | `end_hub: name x y [meta]` | The zone drones must reach |
| `hub: ...` | `hub: name x y [meta]` | A regular zone |
| `connection: ...` | `connection: a-b [meta]` | A bidirectional link between zones `a` and `b` |

**Metadata** is an optional `[key=value ...]` suffix:

| Key | Applies to | Values | Effect |
|---|---|---|---|
| `color` | zones | `red, green, blue, …` | Terminal color for the zone name |
| `zone` | zones | `normal` (default), `restricted`, `priority`, `blocked` | `restricted` ⇒ entry cost 2; `blocked` ⇒ excluded from paths |
| `max_drones` | zones | int (default 1) | Max drones that can occupy the zone simultaneously |
| `max_link_capacity` | connections | int (default 1) | Max drones that can cross the link per turn |

Lines starting with `#` are comments; anything from `#` onward is stripped.
Blank lines are ignored.

---

## Module-by-Module Walkthrough

### models.py — data models

This is the smallest and most fundamental module. It defines the two data classes
that every other module imports, plus a custom exception.

```python
 1  from typing import Optional
 2
 3  class ParseError(Exception):
 4      pass
```

- **Line 1** — imports `Optional` from `typing`, used for type hints below
  (`color: Optional[str]`).
- **Lines 3–4** — defines `ParseError`, a trivial subclass of Python's built-in
  `Exception` with an empty body. It exists so the code can raise/`except` a
  *semantically meaningful* error type (a parsing problem) rather than a bare
  `Exception`. The parser raises it on invalid zone definitions.

```python
 6  class Zone:
 7      """Represents a zone (hub, start_hub, or end_hub) in the drone network."""
 8      def __init__(
 9          self,
10          name: str,
11          x: int,
12          y: int,
13          zone_type: str = "normal",
14          color: Optional[str] = None,
15          max_drones: int = 1,
16      ) -> None:
17          self.name: str = name
18          self.x: int = x
19          self.y: int = y
20          self.zone_type: str = zone_type
21          self.color: Optional[str] = color
22          self.max_drones: int = max_drones
23
24          if zone_type not in ["normal","restricted", "priority", "blocked"]:
25              raise ParseError("Invalid zone type")
26          if zone_type == "restricted":
27              self.entry_cost: int = 2
28          else:
29              self.entry_cost = 1
```

- **Line 6–7** — the `Zone` class: one node in the network (a hub, the start, or the
  end). The docstring states its role.
- **Lines 8–16** — `__init__` signature. Required: `name`, `x`, `y`. Optional with
  defaults: `zone_type="normal"`, `color=None`, `max_drones=1`.
- **Lines 17–22** — plain attribute assignments:
  - `name` — unique identifier, used as a key everywhere (graph dict keys, path lists).
  - `x`, `y` — coordinates. ⚠️ **They are parsed but never used for pathfinding or
    simulation** — they are pure metadata (handy for drawing the map, but unused here).
  - `zone_type` — one of `normal` / `restricted` / `priority` / `blocked`.
  - `color` — optional display color for the terminal output.
  - `max_drones` — capacity: how many drones may occupy this zone at once (default 1).
- **Lines 24–25** — validates `zone_type` against a hard-coded whitelist; raises
  `ParseError` if unknown. (Note the missing space after the comma on line 24 —
  cosmetic only.)
- **Lines 26–29** — computes `entry_cost`:
  - `restricted` zones cost **2** (they slow drones down),
  - everything else costs **1** (including `priority` and `blocked`).
  - `entry_cost` is used later both by the pathfinder (path "cost" = sum of entry
    costs) and by the simulation (a drone entering a `restricted` zone must wait an
    extra turn, see `simulation.py`).

```python
32  class Connection:
33      """Represents a bidirectional connection (edge) between two zones."""
34      def __init__(
35          self, zone_a: str, zone_b: str, max_link_capacity: int = 1
36      ) -> None:
37          self.zone_a: str = zone_a
38          self.zone_b: str = zone_b
39          self.max_link_capacity: int = max_link_capacity
```

- **Lines 32–33** — the `Connection` class: one undirected edge between two zones.
- **Lines 34–36** — constructor takes the two zone *names* (strings, not `Zone`
  objects — the graph resolves them) and an optional link capacity.
- **Lines 37–39** — attribute assignments:
  - `zone_a`, `zone_b` — endpoint names. The connection is **bidirectional**; the
    simulation treats `a-b` the same as `b-a`.
  - `max_link_capacity` — max drones that may traverse this link in a single turn
    (default 1).

---

### graph.py — the graph data structure

Builds and queries the network as an **adjacency list**: a dict mapping each zone
name to a list of neighboring zone names.

```python
 1  from models import Zone
 2
 3
 4  class Graph:
 5      """
 6      The map of the simulation.
 7      Holds all zones and the connections between them.
 8
 9      Example of what it looks like inside:
10          zones      = { "A": Zone_A, "B": Zone_B, "C": Zone_C }
11          neighbors  = { "A": ["B", "C"],
12                         "B": ["A"],
13                         "C": ["A"] }
14      """
15
16      def __init__(self) -> None:
17          self.zones: dict[str, Zone] = {}
18          self.neighbors: dict[str, list[str]] = {}
```

- **Line 1** — imports `Zone` (for the type hint of `self.zones`).
- **Lines 5–14** — class docstring with a concrete example of the internal state:
  two dicts.
- **Lines 16–18** — the constructor initializes the two core structures:
  - `self.zones` — `{zone_name → Zone object}`. Lets the rest of the program look
    up full zone data (capacity, type, cost) by name.
  - `self.neighbors` — `{zone_name → [neighbor names]}`. The actual adjacency list
    used for pathfinding.

```python
20      def add_zone(self, zone: Zone) -> None:
21          """Register a zone so the graph knows it exists."""
22          self.zones[zone.name] = zone
23          self.neighbors[zone.name] = []
```

- **Lines 20–23** — registers a `Zone`: stores it in `zones` keyed by its name, and
  pre-creates an **empty** neighbor list so later appends don't hit a `KeyError`.

```python
25      def add_connection(self, zone_a_name: str, zone_b_name: str) -> None:
26          """Create a two-way link between two zones."""
27          self.neighbors[zone_a_name].append(zone_b_name)
28          self.neighbors[zone_b_name].append(zone_a_name)
```

- **Lines 25–28** — wires two zones together **both ways** (the connection is
  undirected). `add_zone` must have been called for both endpoints first, otherwise
  lines 27–28 raise `KeyError` — this is a latent assumption: **all zones referenced
  by a connection must be defined with a `hub:` line first** (the map files follow
  this convention).

```python
30      def get_neighbors(self, zone_name: str) -> list[str]:
31          """Return the list of zones reachable from zone_name in one step."""
32          return self.neighbors.get(zone_name, [])
```

- **Lines 30–32** — query used by the pathfinder. `dict.get` with a default `[]`
  means an unknown zone name returns an empty list instead of raising — safe
  defensive behaviour.

---

### pathfinder.py — BFS pathfinding

Implements a **Breadth-First Search that enumerates every simple path** from start to
end, then sorts them by total entry cost so the cheapest paths come first.

```python
 1  from collections import deque
 2  from typing import Optional
 3  from graph import Graph
 4
 5
 6  class Pathfinder:
 7
 8      def __init__(self, network: Graph) -> None:
 9          self.network: Graph = network
```

- **Line 1** — `deque` (double-ended queue) from `collections`; the BFS frontier is a
  FIFO queue, and `popleft()` on a `deque` is O(1) (unlike a list's `pop(0)`, which
  is O(n)).
- **Line 2** — `Optional` is **imported but never used** in this file (dead import;
  `flake8` would flag it, `mypy` might not).
- **Line 3** — imports `Graph` for the type hint.
- **Lines 8–9** — constructor stores the graph as `self.network`.

```python
11      def calculate_cost(self, path):
12          """Calculate the total entry cost of a given path."""
13          total = 0
14          for zone in path:
15              total += self.network.zones[zone].entry_cost
16          return total
```

- **Lines 11–16** — sums the `entry_cost` of every zone in a path (each zone counted
  once, including start and end). Since normal zones cost 1 and restricted zones cost
  2, this is essentially *path length* with a penalty for restricted zones. It is
  used as the sort key at line 39. (Note: it is **not** annotated with a return type,
  unlike the rest of the file — `mypy` in strict mode would complain.)

```python
18      def find_all_paths(self, start: str, end: str) -> list[list[str]]:
19          """
20          Find all simple paths from start to end using BFS.
21          Returns a list of paths sorted by length (shortest first).
22          """
23          all_paths: list[list[str]] = []
24          queue: deque[list[str]] = deque([[start]])
25
26          while queue:
27              path = queue.popleft()
28              current = path[-1]
29
30              if current == end:
31                  all_paths.append(path)
32                  continue
33
34              for neighbor in self.network.get_neighbors(current):
35                  if neighbor not in path:
36                      if self.network.zones[neighbor].zone_type != "blocked":
37                          queue.append(path + [neighbor])
38
39          return sorted(all_paths, key=self.calculate_cost)
```

- **Lines 23–24** — initial state: `all_paths` will collect every finished path; the
  queue starts with the single partial path `[start]`.
- **Lines 26–28** — main loop. Pop the oldest partial path; its last element is the
  zone we're currently exploring from.
- **Lines 30–32** — if we've reached `end`, this partial path is complete: save it
  and **do not expand it further** (`continue`). Note the algorithm keeps searching
  for *other* paths rather than stopping at the first — it finds all of them.
- **Lines 34–37** — expansion step, the heart of BFS:
  - `neighbor not in path` prevents cycles: a path never visits a zone twice
    ("simple path").
  - `zone_type != "blocked"` filters out blocked zones entirely.
  - `queue.append(path + [neighbor])` extends the path. Because the queue is FIFO and
    every path has equal edge weight (1 zone per step), **the first complete path
    found is guaranteed to be a shortest path** — this is the key BFS property.
- **Line 39** — sorts all found paths by `calculate_cost`, so index 0 is the
  cheapest (shortest + fewest restricted zones). `main.py` then takes the top two.

⚠️ **Complexity note:** enumerating *all* simple paths is exponential in the worst
case (it visits every simple path in the graph). The included maps are small enough
for this to be fine, but a truly huge maze would blow up — this is a deliberate
trade-off to get more than one candidate path for load-balancing drones.

---

### mapParse.py — map file parser

Reads a `.txt` map and converts it into `nb_drones`, `zones`, `start`, `end`, and
`connections`. It is the "front end" of the program.

```python
 1  from models import Zone, Connection, ParseError
 2  import sys
 3
 4
 5  class MapParse:
 6      def __init__(self, path: str) -> None:
 7          self.path: str = path
```

- **Lines 1–2** — imports the models and `sys` (for `sys.exit`).
- **Lines 6–7** — constructor stores the file path.

```python
 9      def clean_lines(self) -> list[str]:
10          """Read the file and return lines without blanks or comments."""
11          lines: list[str] = []
12          try:
13              with open(self.path, "r") as f:
14                  for row in f:
15                      line = row.split("#")[0].strip()
16                      if not line:
17                          continue
18                      lines.append(line)
19          except FileNotFoundError as f:
20              print(f"Error:{f}")
21          except Exception as e:
22              print(f"Error:{e}")
23
24          return lines
```

- **Lines 11–12** — accumulator list + try block.
- **Lines 13–14** — opens the file and iterates line by line.
- **Line 15** — the crucial line: `row.split("#")[0]` cuts everything from the first
  `#` onward (comment stripping), then `.strip()` removes surrounding whitespace.
- **Lines 16–17** — skips blank/whitespace-only lines.
- **Lines 19–22** — error handlers. ⚠️ They only `print` and **swallow** the error —
  `clean_lines` returns `[]` on failure instead of raising. The failure is detected
  indirectly later (`main.py` validates that zones/connections are non-empty).
- **Line 24** — returns the cleaned lines.

```python
26      def parse_metadata(self, meta: str) -> dict[str, str]:
27          """Parse metadata string "[color=red max_drones=3]" into a dict."""
28          meta_dict: dict[str, str] = {}
29          if not meta:
30              return meta_dict
31          clean = meta.replace("[", "").replace("]", "")
32          for item in clean.split(" "):
33              item = item.strip()
34              if "=" in item:
35                  key, value = item.split("=", 1)
36                  meta_dict[key.strip()] = value.strip()
37          return meta_dict
```

- **Lines 28–30** — empty metadata → empty dict, early return.
- **Line 31** — strips the surrounding `[` and `]`.
- **Lines 32–36** — splits on spaces; for each `key=value` token, splits on the first
  `=` only (`split("=", 1)` so values containing `=` survive), strips both sides and
  stores them. Any token without `=` is silently dropped.
- **Line 37** — returns e.g. `{"color": "red", "max_drones": "3"}` (all values are
  strings; conversion to int happens in the callers).

```python
39      def parse_nb_drones(self, line: str) -> int:
40          """'nb_drones: 5' -> ["nb_drones", " 5"]"""
41          try:
42              return int(line.split(":")[1].strip())
43          except (IndexError, ValueError, Exception):
44              print(f"Invalid nb_drones line: {line!r}")
45              sys.exit(1)
```

- **Lines 41–42** — `"nb_drones: 5".split(":")` → `["nb_drones", " 5"]`; index `[1]`
  is the number, stripped and converted to `int`.
- **Lines 43–45** — on any failure prints the offending line and **exits the whole
  program** with code 1. Note the tuple `(IndexError, ValueError, Exception)` — the
  bare `Exception` already covers the other two, so this is effectively a catch-all
  (slightly redundant, but harmless).

```python
47      def parse_zone(self, line: str) -> Zone:
48          """'hub: corridorA 4 3 [color=red]' -> Zone('corridorA', 4, 3)"""
49          try:
50              body = line.split(":", 1)[1] # corridorA 4 3 [color=red]
51              before_meta = body.split("[")[0] # corridorA 4 3
52              name, x, y = before_meta.split() # name="corridorA", x=4, y=3
53              meta_str = "[" + body.split("[")[1] if "[" in body else ""
54              meta = self.parse_metadata(meta_str)
55              zone_type = meta.get("zone", "normal")
56              color = meta.get("color", None)
57              max_drones = int(meta.get("max_drones", 1))
58              if max_drones <= 0:
59                  raise ParseError("invalid max_drones values")
60              if zone_type not in ["restricted", "normal", "priority", "blocked"]:
61                  raise ParseError("Invalid  zone type !!!!!")
62              return Zone(name, int(x), int(y), zone_type, color, max_drones)
63          except (IndexError, ValueError, Exception, ParseError):
64              print(f"Invalid zone line: {line!r}")
```

- **Line 50** — splits on the **first** colon only (`split(":", 1)`), keeping the
  body, e.g. `" corridorA 4 3 [color=red]"`.
- **Line 51** — takes everything before the `[` → `" corridorA 4 3"`.
- **Line 52** — unpacks the remaining whitespace-separated tokens into `name, x, y`.
  If there are more or fewer than 3 tokens, this raises `ValueError` → caught below.
- **Line 53** — re-constructs the metadata string with its brackets
  (`"[color=red]"`) or `""` if absent, ready for `parse_metadata`.
- **Lines 55–57** — pulls the optional values out of metadata with defaults:
  `zone`→`"normal"`, `color`→`None`, `max_drones`→`1` (converted to `int`).
- **Lines 58–59** — rejects non-positive `max_drones` with `ParseError`.
- **Lines 60–61** — re-validates `zone_type` against the whitelist (same check as in
  `models.py`, duplicated here).
- **Line 62** — builds and returns the `Zone` (coordinates converted with `int`).
- **Lines 63–64** — ⚠️ the except tuple again includes bare `Exception`, so *any*
  failure (including the two `ParseError`s just raised) ends here: it prints
  `"Invalid zone line: ..."` and **returns `None` implicitly**. The caller in
  `parse()` will then crash on `zone.name` — which `main.py` catches and reports as
  a generic error. So an invalid zone never produces a clean error message.

```python
66      def parse_connection(self, line: str) -> Connection:
67          """Parse a connection line into a Connection object."""
68          try:
69              body = line.split(":", 1)[1]
70              before_meta = body.split("[")[0]
71              a, b = before_meta.strip().split("-")
72              meta_str = "[" + body.split("[")[1] if "[" in body else ""
73              meta = self.parse_metadata(meta_str)
74              capacity = int(meta.get("max_link_capacity", 1))
75              if capacity <= 0:
76                  print("invalid capacity values")
77                  sys.exit(1)
78              return Connection(a.strip(), b.strip(), capacity)
79          except (IndexError, ValueError, Exception):
80              print(f"Invalid connection line: {line!r}")
```

- **Lines 69–70** — same split strategy as `parse_zone`: strip the `connection:`
  prefix and any metadata.
- **Line 71** — splits the two endpoints on the `-` character (e.g. `start-waypoint1`
  → `a="start"`, `b="waypoint1"`). Note: `strip()` is applied to the whole string
  first, then again per-endpoint at line 78.
- **Lines 72–74** — metadata → `max_link_capacity` (default 1).
- **Lines 75–77** — rejects non-positive capacities by printing and **exiting the
  program** (inconsistent with `parse_zone`, which merely returns `None`).
- **Lines 78–80** — builds the `Connection` and returns it; failures are printed and
  return `None` (same swallow-and-return-None pattern as `parse_zone`).

```python
82      def parse(self) -> tuple[int, dict[str, Zone], str, str, list[Connection]]:
83          """Read all lines and return parsed data."""
84          nb_drones: int = 0
85          zones: dict[str, Zone] = {}
86          start: str = ""
87          end: str = ""
88          connections: list[Connection] = []
89
90          for line in self.clean_lines():
91              if line.startswith("nb_drones:"):
92                  nb_drones = self.parse_nb_drones(line)
93              elif line.startswith("start_hub"):
94                  zone = self.parse_zone(line)
95                  zones[zone.name] = zone
96                  start = zone.name
97              elif line.startswith("end_hub"):
98                  zone = self.parse_zone(line)
99                  zones[zone.name] = zone
100                 end = zone.name
101             elif line.startswith("hub:"):
102                 zone = self.parse_zone(line)
103                 zones[zone.name] = zone
104             elif line.startswith("connection"):
105                 connections.append(self.parse_connection(line))
106
107         return nb_drones, zones, start, end, connections
```

- **Lines 84–88** — initializes the five accumulator values with safe defaults
  (`start`/`end` as empty strings — see the "missing start/end" note in the quirks
  section).
- **Lines 90–105** — the dispatcher. Each line is classified by prefix:
  - `nb_drones:` → parse the count (line 91–92).
  - `start_hub` → parse as a zone, register it, and remember its name as `start`
    (lines 93–96).
  - `end_hub` → same but for `end` (lines 97–100).
  - `hub:` → parse and register a regular zone (lines 101–103).
  - `connection` → parse and append (lines 104–105).
  - Anything else is silently ignored.
- **Line 107** — returns the tuple in the exact order `main.py` unpacks.

---

### simulation.py — the turn-based engine

The most complex module. It moves the drones along their pre-assigned paths, one turn
at a time, using a **snapshot-based collision/capacity engine** so that multiple
drones can safely swap positions in a single turn.

```python
 1  from display import Display
 2  from graph import Graph
 3  from models import Connection
 4
 5
 6  class Simulation:
 7      """Manages step-by-step drone routing execution in the terminal."""
 8
 9      def __init__(
10          self,
11          graph: Graph,
12          drone_paths: list[list[str]],
13          nb_drones: int,
14          connections: list[Connection],
15      ) -> None:
16          self.graph = graph
17          self.drone_paths = drone_paths
18          self.nb_drones = nb_drones
19          self.connections = connections
20
21          self.start_zone = drone_paths[0][0]
22          self.end_zone = drone_paths[0][-1]
23          self.display = Display(graph)
24
25          self.turn = 0
26          self.positions = [0] * nb_drones
27
28          self.cooldowns = [0] * nb_drones
```

- **Lines 1–3** — imports `Display` (output), `Graph` (types), `Connection` (types).
- **Lines 9–15** — constructor takes everything `main.py` prepared: the graph, the
  per-drone paths, the drone count, and the raw connection list (used to look up link
  capacities, which the graph does not store).
- **Lines 16–19** — plain storage.
- **Lines 21–22** — derives the start and end zone names from the *first* drone's
  path (all drones share the same start/end in this program). Used by
  `_zone_capacity` to give start/end unlimited capacity.
- **Line 23** — creates the `Display` object used for printing.
- **Line 25** — `self.turn`, the turn counter returned at the end (this is the
  program's score).
- **Line 26** — `self.positions`: a per-drone index into its own path. `0` means "at
  the first zone of the path" (the start). This is the drone's entire state.
- **Line 28** — `self.cooldowns`: a per-drone wait counter. When > 0 the drone is
  resting and cannot move; it ticks down by 1 each turn. Used to implement the
  `restricted` zone penalty (entry cost 2 ⇒ wait 1 turn).

```python
29      def _zone_capacity(self, zone_name: str) -> int:
30          if zone_name in (self.start_zone, self.end_zone):
31              return 999999
32          return self.graph.zones[zone_name].max_drones
```

- **Lines 29–32** — how many drones may occupy a zone:
  - The start and end zones are treated as **effectively unlimited** (999999) so the
    launch pad and the finish line never cause congestion.
  - Every other zone uses its `max_drones` value from the map file.

```python
34      def _link_capacity(self, zone_a: str, zone_b: str) -> int:
35          for conn in self.connections:
36              if (conn.zone_a == zone_a and conn.zone_b == zone_b) or \
37                 (conn.zone_a == zone_b and conn.zone_b == zone_a):
38                  return conn.max_link_capacity
39          return 1
```

- **Lines 34–39** — linear scan of the connection list to find the capacity of the
  link between two zones. The `or` branch checks **both directions** (because
  connections are undirected). If the link isn't found (shouldn't happen with valid
  maps), it falls back to capacity 1.

```python
41      def all_arrived(self) -> bool:
42          for drone_id in range(self.nb_drones):
43              if self.positions[drone_id] < len(self.drone_paths[drone_id]) - 1:
44                  return False
45          return True
```

- **Lines 41–45** — the loop-exit condition. A drone has "arrived" when its position
  index is at the last element of its path (the end zone). If **any** drone hasn't
  reached its last index, return `False`. The main loop in `run()` keeps going until
  this returns `True`.

```python
47      def _compute_turn(self) -> dict[int, str]:
48          moves = {}
49          zone_counts: dict[str, int] = {}
50
51          for drone_id in range(self.nb_drones):
52              curr_zone = self.drone_paths[drone_id][self.positions[drone_id]]
53              zone_counts[curr_zone] = zone_counts.get(curr_zone, 0) + 1
54
55          link_usage: dict[tuple[str, ...], int] = {}
56          planned_arrivals: dict[str, int] = {}
57          planned_departures: dict[str, int] = {}
```

- **Line 48** — `moves`: the result, mapping `drone_id → destination zone name` for
  every drone that gets to move this turn.
- **Lines 51–53** — **Phase 1 (the snapshot):** counts how many drones are standing
  in each zone at the start of this turn. `zone_counts[curr_zone]` is the baseline
  occupancy for the whole turn — it is *not* updated as drones move. This is what
  makes the engine "snapshot-based".
- **Lines 55–57** — **Phase 2 planning state** (all empty at the start of a turn):
  - `link_usage` — how many drones have *already been approved* to cross each link
    this turn, keyed by a sorted tuple of the two zone names (so `(a,b)` == `(b,a)`).
  - `planned_arrivals` — arrivals into each zone approved so far this turn.
  - `planned_departures` — departures out of each zone approved so far this turn.
  Together these let a drone that is about to *leave* a zone free up its space for
  another drone that wants to *enter* it in the same turn.

```python
59          for drone_id in range(self.nb_drones):
60              # --- ---
61              if self.cooldowns[drone_id] > 0:
62                  self.cooldowns[drone_id] -= 1
63                  continue
64              # --- ---
65              curr_idx = self.positions[drone_id]
66              path = self.drone_paths[drone_id]
67
68              if curr_idx >= len(path) - 1:
69                  continue
70
71              curr_zone = path[curr_idx]
72              next_zone = path[curr_idx + 1]
73              link = tuple(sorted((curr_zone, next_zone)))
```

- **Line 59** — per-drone planning loop (drone 0 first, then 1, 2, … — order
  matters slightly; earlier drones get first claim on links/space).
- **Lines 61–63** — **cooldown check:** if this drone is resting, decrement its
  cooldown by 1 and skip it for this turn. This is how a `restricted` zone costs 2
  turns: 1 turn to move in, 1 turn of cooldown before it can move out again.
- **Lines 65–66** — read the drone's current index and its whole path.
- **Lines 68–69** — if the drone is already at the last zone of its path (it has
  arrived), there's nothing to do.
- **Lines 71–72** — the move under consideration: from `curr_zone` to the next zone
  on the path.
- **Line 73** — normalizes the link key with `sorted()` so direction doesn't matter
  when counting usage.

```python
75              link_cap = self._link_capacity(curr_zone, next_zone)
76              if link_usage.get(link, 0) >= link_cap:
77                  continue
```

- **Lines 75–77** — **link capacity check:** if this turn's approved crossings of
  this link already equal its capacity, the drone waits (no move).

```python
79              expected_drones = (
80                  zone_counts.get(next_zone, 0)
81                  - planned_departures.get(next_zone, 0)
82                  + planned_arrivals.get(next_zone, 0)
83              )
84
85              if expected_drones >= self._zone_capacity(next_zone):
86                  continue
```

- **Lines 79–83** — **zone capacity check** — the clever part. It computes the
  *projected* number of drones that will occupy `next_zone` at the end of this turn:
  - `zone_counts[next_zone]` — drones currently there (snapshot),
  - minus drones already approved to **leave** it this turn,
  - plus drones already approved to **arrive** this turn.
- **Lines 85–86** — if that projection is at or above the zone's capacity, the drone
  stays put. Because departures and arrivals are both tracked, a drone can move into
  a zone in the *same* turn another drone moves out — no artificial one-turn delay,
  and no double-occupancy either.

```python
88              moves[drone_id] = next_zone
89              link_usage[link] = link_usage.get(link, 0) + 1
90              planned_arrivals[next_zone] = (
91                  planned_arrivals.get(next_zone, 0) + 1)
92              planned_departures[curr_zone] = (
93                  planned_departures.get(curr_zone, 0) + 1)
94
95              # -------------------------------------------------------------------------
96              next_zone_cost = self.graph.zones[next_zone].entry_cost
97              # -------------------------------------------------------------------------
98              self.cooldowns[drone_id] = next_zone_cost - 1
99              # -------------------------------------------------------------------------
```

- **Lines 88–93** — **reserve the move:** record it in `moves` and update the three
  planning dicts so subsequent drones see this drone's intended arrival/departure.
  This is the "commit while planning" trick that makes simultaneous moves safe.
- **Lines 95–99** — set the cooldown after moving: `entry_cost - 1`. For a normal
  zone (cost 1) that's 0 (move every turn). For a restricted zone (cost 2) that's 1
  (wait one extra turn). The long comment bars are decorative.

```python
101         return moves
```

- **Line 101** — returns the plan for this turn. `run()` will apply it.

```python
103     def run(self) -> int:
104         """Core execution entry point orchestrating
105             routing setups in the terminal."""
106         self.display.print_header(self.nb_drones)
107         """=== FLY-IN SIMULATION ===
108            Drones  : 4              """
```

- **Line 106** — prints the banner (`=== FLY-IN SIMULATION ===` / `Drones : N` /
  separator) via `Display`.
- **Lines 107–108** — ⚠️ a bare string literal with no assignment — it's just a
  stray comment fragment (probably leftover from an earlier version where the header
  text lived here). It has **no runtime effect**.

```python
110         while not self.all_arrived():
111             self.turn += 1
112
113             was_witting = (c > 0 for c in self.cooldowns)
114
115             moves = self._compute_turn()
116
117             if not moves and not self.all_arrived():
118                 if not was_witting:
119                     print(
120                         "\n[!] Simulation Deadlock: Drones are "
121                         "stuck. Exiting to prevent infinite loop."
122                     )
123                     break
124
125             for drone_id in moves:
126                 self.positions[drone_id] += 1
127
128             self.display.print_turn(moves)
129
130         return self.turn
```

- **Lines 110–111** — main loop; each iteration is one turn. `self.turn` is
  incremented first, so the reported total equals the number of turns executed.
- **Line 113** — ⚠️ **a real quirk:** `was_witting` is a *generator expression*, and
  **a generator object is always truthy** (even if it yields nothing). The deadlock
  check on line 118 (`if not was_witting:`) can therefore never be true, so the
  deadlock message is effectively dead code. The author probably meant
  `was_witting = any(c > 0 for c in self.cooldowns)`. Practical consequence: if the
  drones genuinely get stuck in a gridlock, the loop would run forever rather than
  abort — the safety valve doesn't work as written.
- **Line 115** — compute this turn's moves (the planning above).
- **Lines 117–123** — deadlock guard: if nobody moved **and** nobody is cooling down
  (i.e. nothing will change next turn either), print a warning and break. As noted,
  due to the generator bug the inner condition never fires.
- **Lines 125–126** — **commit:** advance each moving drone's position index by one.
  This happens *after* all planning is done, so every drone in `moves` moves
  simultaneously — the core of the snapshot model.
- **Line 128** — print this turn's movements (`D1-zone D2-zone …`).
- **Line 130** — return the total turn count, which `main.py` prints.

---

### display.py — colored terminal output

Handles all ANSI escape code formatting. It is a pure presentation layer — no logic.

```python
 1  from graph import Graph
 2
 3  class Color:
 4      RESET = "\033[0m"
 5      BOLD = "\033[1m"
 6
 7      MAP = {
 8          "red": "\033[91m",
 9          "green": "\033[92m",
10          "yellow": "\033[93m",
11          "blue": "\033[94m",
12          "magenta": "\033[95m",
13          "cyan": "\033[96m",
14          "white": "\033[97m",
15          "gray": "\033[90m",
16          "grey": "\033[90m",
17          "orange": "\033[38;5;208m",
18      }
```

- **Line 1** — imports `Graph` (only used for the type hint in `Display.__init__`).
- **Lines 3–5** — the `Color` class holds ANSI codes: `RESET` clears all formatting;
  `BOLD` enables bold. `\033` is the ESC character.
- **Lines 7–18** — `MAP`: a lookup of color names → ANSI codes. Bright variants are
  used for most colors (`\033[9Xm`); `orange` uses the 256-color escape
  `\033[38;5;208m` (basic ANSI has no orange). `gray` and `grey` map to the same code
  (aliases).

```python
20      @staticmethod
21      def paint(text: str, color: str) -> str:
22          code = Color.MAP.get(color.lower(), "")
23          return f"{code}{text}{Color.RESET}" if code else text
24
25      @staticmethod
26      def bold(text: str) -> str:
27          return f"{Color.BOLD}{text}{Color.RESET}"
```

- **Lines 20–23** — `paint` wraps text in `code + text + RESET`. `color.lower()`
  makes it case-insensitive; unknown colors get `""` and the text is returned
  unchanged (safe fallback).
- **Lines 25–27** — `bold` wraps text in the bold code + RESET.

```python
30  class Display:
31      def __init__(self, graph) -> None:
32          self.graph = graph
33
34      def _zone_label(self, zone_name: str) -> str:
35          zone = self.graph.zones.get(zone_name)
36
37          if zone and zone.color:
38              return Color.paint(zone_name, zone.color)
39
40          return zone_name
```

- **Lines 30–32** — `Display` holds a reference to the graph so it can look up zone
  colors. (The `graph` parameter has no type annotation.)
- **Lines 34–40** — `_zone_label` returns the zone name, painted with its map-defined
  color if it has one, otherwise plain. Used when printing turns.

```python
42      def print_header(self, nb_drones: int) -> None:
43          print(Color.bold("\n=== FLY-IN SIMULATION ==="))
44          print(f"Drones  : {nb_drones}")
45          print(Color.bold("─" * 40))
```

- **Lines 42–45** — prints the banner: bold title, the drone count, and a bold
  separator of 40 box-drawing characters (`─`).

```python
47      def print_turn(self, moves: dict[int, str]) -> None:
48          if not moves:
49              return
50
51          parts = []
52
53          for drone_id, zone in sorted(moves.items()):
54              drone = Color.paint(f"D{drone_id + 1}", "cyan")
55              parts.append(f"{drone}-{self._zone_label(zone)}")
56
57          print(f"{' '.join(parts)}")
```

- **Lines 47–49** — if nobody moved this turn, print nothing (an empty turn is not
  shown).
- **Lines 51–53** — builds one string per moving drone; `sorted(moves.items())`
  orders them by drone id (D1 before D2 before D3 …).
- **Lines 54–55** — the drone label is `D<id+1>` in **cyan** (id+1 because drone ids
  are 0-based internally but displayed 1-based), then `-`, then the destination zone
  (with its color).
- **Line 57** — prints all parts joined by spaces on one line, e.g.
  `D1-waypoint2 D2-waypoint1`.

```python
59      def print_footer(self, turns: int) -> None:
60          print(Color.bold("─" * 40))
61          print(f"{Color.bold('Total turns:')} {Color.paint(str(turns), 'green')}")
```

- **Lines 59–61** — prints a footer with the total turn count in green. ⚠️ **Never
  called** — `main.py` prints its own `Total turns:` line instead. Dead code (or a
  hook for future use).

---

### main.py — entry point

Ties everything together. This is the module executed by `python3 main.py <map>`.

```python
 1  from mapParse import MapParse
 2  from graph import Graph
 3  from pathfinder import Pathfinder
 4  from simulation import Simulation
 5  from models import Zone, Connection, ParseError
 6  import sys
```

- **Lines 1–6** — imports every component of the program plus `sys` (for `argv` and
  `exit`). All the local modules are importable because they live in the same folder
  and the script runs from that folder.

```python
 9  def build_graph(
10          zones: dict[str, Zone],
11          connections: list[Connection]
12          ) -> Graph:
13      """Create a Graph from the parsed zones and connections."""
14      graph = Graph()
15      for zone in zones.values():
16          graph.add_zone(zone)
17      for conn in connections:
18          graph.add_connection(conn.zone_a, conn.zone_b)
19      return graph
```

- **Lines 9–13** — helper that converts the parser's output into a `Graph`.
- **Lines 14–16** — creates the graph and registers every zone (from the dict's
  values; the keys are just names).
- **Lines 17–18** — wires up every connection (bidirectional, per `graph.py`).
- **Line 19** — returns the finished graph.

```python
22  def main() -> None:
23      """Entry point — usage: python main.py <map_file>"""
24      if len(sys.argv) < 2:
25          print("Usage: python main.py <map_file>")
26          return
27
28      map_file: str = sys.argv[1]
```

- **Lines 24–26** — usage guard: with no command-line argument, print usage and stop.
- **Line 28** — the map path is `sys.argv[1]`.

```python
30      try:
31          parser = MapParse(map_file)
32          nb_drones, zones, start, end, connections = parser.parse()
33      except Exception as e:
34          print(f"Error: {e}")
35          sys.exit(1)
```

- **Lines 30–32** — creates the parser and runs it; unpacks the five results.
- **Lines 33–35** — any exception during parsing → print `Error: …` and exit 1.
  (Because `clean_lines` swallows file errors, a missing file usually surfaces later
  as a validation failure rather than here.)

```python
37      if nb_drones <= 0:
38          print("Error: Invalid number of drones (must be > 0).")
39          sys.exit(1)
40      if start is None:
41          print("Parse error: missing start_hub definition.")
42          sys.exit(1)
43      if end is None:
44          print("Parse error: missing end_hub definition.")
45          sys.exit(1)
46      if not connections or not zones:
47          print("Parse error: missing connection or hub definition.")
48          sys.exit(1)
```

- **Lines 37–39** — rejects a non-positive drone count (e.g. `nb_drones: 0`).
- **Lines 40–42 & 43–45** — ⚠️ *intended* to detect a missing `start_hub`/`end_hub`,
  but `mapParse.parse()` initializes `start`/`end` to `""` (never `None`), so these
  checks **never trigger**. If a map is missing a start or end hub, the program
  proceeds and pathfinding simply finds no path (falling into the "No path found."
  branch at line 54–56). A correct check would be `if not start:`.
- **Lines 46–48** — a real guard: an empty zones dict or connections list (e.g. file
  not found / all lines were comments) aborts with a clear message.

```python
49      try:
50          graph = build_graph(zones, connections)
51          pathfinder = Pathfinder(graph)
52          all_paths = pathfinder.find_all_paths(start, end)
53
54          if not all_paths:
55              print("No path found.")
56              sys.exit(1)
57
58          best_paths = all_paths[:min(2, len(all_paths))]
59
60          drone_paths = [
61              best_paths[i % len(best_paths)]
62              for i in range(nb_drones)
63          ]
64
65          sim = Simulation(graph, drone_paths, nb_drones, connections)
66          turns = sim.run()
67      except (ParseError, Exception) as e:
68          print(f"Error: {e}")
69          sys.exit(1)
70      print(f"\nTotal turns: {turns}")
```

- **Line 50** — builds the graph from parsed data.
- **Lines 51–52** — creates the pathfinder and computes **all** simple paths from
  start to end, sorted cheapest first.
- **Lines 54–56** — if no path exists at all, report and exit.
- **Line 58** — keeps only the top **2** cheapest paths (or fewer if the map offers
  only one). Using two paths lets the fleet split up and avoids a single-lane
  bottleneck.
- **Lines 60–63** — assigns a path to every drone **round-robin**: drone 0 → path 0,
  drone 1 → path 1, drone 2 → path 0, drone 3 → path 1, … (`i % len(best_paths)`).
  All drones on the same path queue up behind each other; the simulation's capacity
  rules handle spacing.
- **Lines 65–66** — constructs the `Simulation` and runs it; the returned turn count
  is stored in `turns`.
- **Lines 67–69** — catch-all for anything thrown during build/path/sim; note that
  `(ParseError, Exception)` is again redundant (Exception covers ParseError).
- **Line 70** — prints the final score with a leading blank line.

```python
73  if __name__ == "__main__":
74      main()
```

- **Lines 73–74** — the standard guard: `main()` only runs when this file is executed
  directly (not when imported elsewhere).

---

## Supporting Files

### Makefile

```make
PYTHON = python3
UV = uv
SRC = main.py
MAP_FILE = maps/easy/01_linear_path.txt

install:
	$(UV) sync

run:
	$(UV) run $(PYTHON) $(SRC) $(MAP_FILE)

debug:
	$(UV) $(PYTHON) pdb $(MAIN_SCRIPT) $(MAP_FILE)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

lint:
	flake8 src
	mypy src --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	flake8 src
	mypy src --strict

.PHONY: install run debug clean lint lint-strict
```

- **`install`** — `uv sync`: installs dependencies from `pyproject.toml`/`uv.lock`
  (only `mypy` is declared) into the project venv.
- **`run`** — the main command: `uv run python3 main.py maps/easy/01_linear_path.txt`.
- **`debug`** — ⚠️ has two problems: `$(UV) $(PYTHON)` expands to `uv python3` (not a
  valid invocation), and `$(MAIN_SCRIPT)` is undefined (the variable is named `SRC`).
  This target is broken as written; the intended command is
  `uv run python3 -m pdb main.py maps/easy/01_linear_path.txt`.
- **`clean`** — removes `__pycache__` and `.mypy_cache` directories recursively.
- **`lint` / `lint-strict`** — ⚠️ both run `flake8 src` and `mypy src`, but the
  source files live in the **project root**, not in a `src/` folder — so these
  targets currently operate on a non-existent directory. The intended invocation
  would target `.` or the individual files.

### pyproject.toml

```toml
[project]
name = "test-fly-in"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.13"
dependencies = ["mypy"]
```

- `uv` project manifest. Declares `mypy` as the only dependency and requires Python
  3.13+ (matching `.python-version`). `name`/`description` look like placeholders.

### uv.lock

The dependency lockfile generated by `uv` (pins exact versions of `mypy` and its
transitive dependencies). It is what `uv sync` consults.

### .python-version

```
3.13
```

- Tells `uv` which Python version to use for this project.

### .gitignore

```
__pycache__/
.mypy_cache/

.venv/
.DS_Store
maps/
```

- Notably, **`maps/` is git-ignored** — the map files are not tracked in git
  (probably because they came from the project's external grader).

### README.md

The project's official readme. It describes the goal, features, algorithm (BFS +
snapshot simulation), and output format. ⚠️ A few claims are out of date relative to
the actual code:

- It lists a `Drone` class in `models.py`; there is none.
- The sample output shows `[Turn   1]` prefixes and a gray turn counter; the real
  output has neither.
- It says `make lint` checks the code — as noted above, the Makefile points at a
  non-existent `src/` directory.

---

## A Worked Example

Let's trace `maps/easy/01_linear_path.txt` end to end (this is the actual verified
output):

```
nb_drones: 2
start_hub: start 0 0 [color=green]
hub: waypoint1 1 0 [color=blue]
hub: waypoint2 2 0 [color=blue]
end_hub: goal 3 0 [color=red]
connection: start-waypoint1
connection: waypoint1-waypoint2
connection: waypoint2-goal
```

**Parsing** — `MapParse.parse()` produces:
- `nb_drones = 2`
- `zones = {start, waypoint1, waypoint2, goal}` (all `max_drones=1`, entry cost 1)
- `start = "start"`, `end = "goal"`
- `connections = [start-waypoint1, waypoint1-waypoint2, waypoint2-goal]`

**Graph** — `build_graph()` yields:
```
zones     = {start: Zone, waypoint1: Zone, waypoint2: Zone, goal: Zone}
neighbors = {start: [waypoint1], waypoint1: [start, waypoint2],
             waypoint2: [waypoint1, goal], goal: [waypoint2]}
```

**Pathfinding** — BFS enumerates all simple paths. Since the map is linear, there is
exactly one: `["start", "waypoint1", "waypoint2", "goal"]`, cost = 4. `best_paths`
holds just that one path; both drones get assigned it.

**Simulation** — `positions = [0, 0]`, `cooldowns = [0, 0]`. Turn by turn:

| Turn | Snapshot (`zone_counts`) | Who moves | Why the other waits |
|---|---|---|---|
| 1 | `{start: 2}` | D1 → waypoint1 | D2 blocked by **link capacity 1** on `start-waypoint1` |
| 2 | `{start: 1, waypoint1: 1}` | D1 → waypoint2, D2 → waypoint1 | D2's check: `zone_counts[waypoint1] − planned_departures[waypoint1] + planned_arrivals[waypoint1]` = `1 − 1 + 0` = 0 < capacity 1 ✓ — D1 leaving frees the zone for D2 in the same turn |
| 3 | `{waypoint1: 1, waypoint2: 1, start: 0}` | D1 → goal, D2 → waypoint2 | |
| 4 | `{waypoint2: 1, goal: 1}` | D2 → goal | |

Every drone is at the end of its path → `all_arrived()` is True → loop exits →
**`Total turns: 4`**. The turn-by-turn printout matches the verified output above.

---

## Observations, Quirks & Potential Issues

A short list of things worth knowing if you modify this code:

1. **Deadlock detection is broken** (`simulation.py:113`) — `was_witting` is a
   generator (always truthy), so the anti-infinite-loop break never fires. Fix:
   `was_witting = any(c > 0 for c in self.cooldowns)`.
2. **Missing start/end checks are dead code** (`main.py:40,43`) — the parser returns
   `""` for missing hubs, never `None`. Fix: `if not start:`. (The result today is
   the "No path found." branch instead of a clear message.)
3. **Redundant exception tuples** — `(IndexError, ValueError, Exception)` and
   `(ParseError, Exception)` appear in several places; the bare `Exception` makes the
   others meaningless. Harmless but noisy.
4. **Parser swallows errors** — `clean_lines` and `parse_zone` print and return
   `None`/`[]` on bad input, pushing confusing failures downstream (a bad zone line
   eventually crashes in `parse()` and surfaces as a generic `Error:` message).
5. **`make debug` and `make lint` are broken** — `debug` uses undefined
   `$(MAIN_SCRIPT)` and an invalid `uv python3` invocation; `lint` targets look for
   a `src/` directory that doesn't exist (files are in the root).
6. **Unused code** — `print_footer` in `display.py` is never called; `Optional` in
   `pathfinder.py` is never used; the docstring-literal at `simulation.py:107`.
7. **Exponential path enumeration** — `find_all_paths` enumerates *all* simple paths
   (intentional, to get 2 candidates), which can explode on large mazes.
8. **`x`, `y` coordinates are never used** beyond storage — they're metadata only.
9. **README drift** — the README's sample output and class list don't fully match
   the current code (no `Drone` class, no `[Turn N]` prefixes, no turn counter).
10. **Blocked zones in metadata** are validated (`zone=blocked` is accepted) but a
    blocked zone is only *meaningful* in pathfinding — it's excluded from paths and
    otherwise behaves like a normal zone if a path never visits it anyway.

---

## Glossary

| Term | Meaning |
|---|---|
| **Zone** | A node in the network: `start_hub`, `end_hub`, or regular `hub`. Has a capacity (`max_drones`) and an entry cost. |
| **Connection / link / edge** | A bidirectional route between two zones, with a per-turn capacity (`max_link_capacity`). |
| **Drone** | A unit that follows a pre-computed path, one zone per turn (subject to cooldowns). |
| **Turn** | One iteration of the simulation loop; all approved moves happen simultaneously. |
| **Position** | A drone's index into its path list; `positions[drone] == 0` at the start. |
| **Cooldown** | Per-drone wait counter; `> 0` means the drone can't move (used for `restricted` zones). |
| **Snapshot** | The zone-occupancy count taken at the start of a turn, used to plan moves consistently. |
| **Entry cost** | `1` for normal/priority/blocked zones, `2` for restricted. Path cost = sum over the path; cooldown after entry = cost − 1. |
| **BFS** | Breadth-first search — explores all zones at distance 1, then distance 2, etc. |
| **Simple path** | A path that visits no zone more than once (no cycles). |
| **Deadlock** | A state where no drone can move; the simulation's (currently ineffective) guard against it. |
| **ANSI escape code** | Terminal control sequences like `\033[92m` used to colorize output. |
