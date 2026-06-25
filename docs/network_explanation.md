# شرح ملف `src/network.py`

## ما هو دور هذا الملف؟

**`Network`** هو "حاوية الخريطة" — يجمع كل المناطق وكل الروابط في مكان واحد.
فكّر فيه كـ "قاموس المدينة": فيه كل الأحياء (zones) وكل الطرق بينها (connections).

## علاقته بالملفات الأخرى

```
network.py
  ← يُنشئه   MapParser.py  (يملأه بالمناطق والروابط)
  ← يستخدمه  pathfinder.py (يسأله: من هم جيران هذه المنطقة؟)
  ← يستخدمه  simulation.py (يسأله: ما سعة هذه المنطقة؟)
  ← يستخدمه  visualizer.py (يرسم كل مناطقه وروابطه)
  ← يُمرَّر  إلى Simulation و Visualizer عبر main.py
```

---

## شرح الكود سطراً بسطر

```python
from zone import Zone
from connection import Connection
```
**السطران 1-2:** نستورد الكلاسين `Zone` و `Connection`.
هذا يعني أن `network.py` يعتمد على كلا الملفين.

---

```python
class Network:
    """Holds all zones and connections that make up the map."""
```
**السطران 5-6:** تعريف الكلاس مع docstring يشرح وظيفته.

---

```python
    def __init__(self) -> None:
        """Start with an empty network."""
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []
```
**السطور 8-11:** دالة البناء. تنشئ كائن `Network` فارغاً.

- `self.zones` → قاموس: **اسم المنطقة** → **كائن Zone**
  - مثلاً: `{"hub": Zone(...), "roof1": Zone(...), "goal": Zone(...)}`
  - القاموس يجعل البحث عن منطقة بالاسم سريعاً جداً `O(1)`.

- `self.connections` → قائمة بكل كائنات `Connection`
  - مثلاً: `[Connection("hub","roof1"), Connection("roof1","goal")]`

---

```python
    def add_zone(self, zone: Zone) -> None:
        """Add a zone to the network."""
        self.zones[zone.name] = zone
```
**السطور 13-15:** إضافة منطقة للشبكة.
- نأخذ اسم المنطقة `zone.name` كمفتاح في القاموس.
- يستدعيه `MapParser.py` لكل سطر `hub:`, `start_hub:`, `end_hub:` يقرأه.

---

```python
    def add_connection(self, conn: Connection) -> None:
        """Add a connection (link) between two zones."""
        self.connections.append(conn)
```
**السطور 17-19:** إضافة رابط للشبكة.
- نضيف الكائن `Connection` لآخر القائمة.
- يستدعيه `MapParser.py` لكل سطر `connection:` يقرأه.

---

```python
    def get_neighbors(self, zone_name: str) -> list[tuple[str, Connection]]:
        """
        Return all zones reachable from zone_name, along with the connection used.

        Returns:
            list of (neighbor_name, connection) pairs
        """
        result: list[tuple[str, Connection]] = []
        for conn in self.connections:
            if conn.connects(zone_name):
                neighbor = conn.other_end(zone_name)
                result.append((neighbor, conn))
        return result
```
**السطور 21-32:** **أهم دالة في الكلاس.**
- تأخذ اسم منطقة وتعيد كل المناطق المتصلة بها، مع الرابط المستخدم.
- **كيف تعمل:**
  1. نبدأ بقائمة فارغة `result`
  2. نمر على **كل** الروابط في الشبكة
  3. إذا كان الرابط `conn` يمس `zone_name` (عبر `conn.connects(zone_name)`)
  4. نعرف الطرف الآخر عبر `conn.other_end(zone_name)`
  5. نضيف الزوج `(neighbor, conn)` للنتيجة
- **مثال:** لو عندنا: hub→roof1، hub→corridorA
  - `get_neighbors("hub")` → `[("roof1", conn1), ("corridorA", conn2)]`
- يستخدمها `pathfinder.py` أثناء البحث عن المسار.
- يستخدمها `visualizer.py` لرسم الروابط.

---

```python
    def find_connection(self, zone_a: str, zone_b: str) -> Connection | None:
        """Find the connection between two zones, or None if none exists."""
        for conn in self.connections:
            if conn.connects(zone_a) and conn.connects(zone_b):
                return conn
        return None
```
**السطور 34-38:** تبحث عن الرابط المباشر بين منطقتين.
- تمر على كل الروابط وتعيد الذي يربط `zone_a` بـ `zone_b`.
- إذا لم تجد → تعيد `None`.
- يستخدمها `simulation.py` للتحقق من سعة الرابط قبل تحريك الطائرة.

---

## كيف تبدو الشبكة بعد تحميل خريطة؟

```
الخريطة:              الشبكة بعد التحميل:
hub 0 0               zones = {
roof1 3 4               "hub":   Zone("hub",   0, 0, "normal")
goal 10 10              "roof1": Zone("roof1", 3, 4, "normal")
hub-roof1               "goal":  Zone("goal", 10,10, "normal")
roof1-goal            }
                      connections = [
                        Connection("hub",   "roof1"),
                        Connection("roof1", "goal")
                      ]
```
