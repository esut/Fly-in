# شرح ملف `src/MapParser.py`

## ما هو دور هذا الملف؟

`MapParser` يقرأ **ملف الخريطة النصي** ويحوّله إلى كائنات Python قابلة للاستخدام.
بدونه، البرنامج لا يعرف شيئاً عن الخريطة.

**المدخل:** ملف نصي مثل:
```
nb_drones: 3
start_hub: hub 0 0 [color=green]
end_hub: goal 10 10 [color=yellow]
hub: roof1 3 4 [zone=restricted color=red]
connection: hub-roof1
connection: roof1-goal
```

**المخرج:** كائن `Network` مليء بـ `Zone`s و`Connection`s، + عدد الطائرات + أسماء البداية والنهاية.

## علاقته بالملفات الأخرى

```
MapParser.py
  ← يستورد   Zone (zone.py)
  ← يستورد   Connection (connection.py)
  ← يستورد   Network (network.py)
  ← يستخدمه  main.py (أول شيء يشغله البرنامج)
  → ينتج     network الذي يُمرَّر لـ Pathfinder و Simulation و Visualizer
```

---

## شرح الكود سطراً بسطر

```python
import sys
from zone import Zone
from connection import Connection
from network import Network
```
**السطور 1-4:** الاستيرادات.
- `sys` → لاستخدام `sys.exit(1)` عند الخطأ (يوقف البرنامج بكود خطأ 1)
- الثلاثة الأخرى → الكلاسات التي سننشئ منها الكائنات

---

```python
class MapParser:
    """
    Reads a map text file and builds a Network of Zone and Connection objects.
    ...
    """
```
**السطور 7-18:** تعريف الكلاس مع docstring يشرح الصيغة المقبولة.

---

```python
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.nb_drones: int = 0
        self.start_hub: str = ""
        self.end_hub: str = ""
        self.network: Network = Network()
        self._seen_connections: set[str] = set()
```
**السطور 20-27:** دالة البناء.
- `filepath` → مسار الملف الذي سنقرأه
- `nb_drones` → يُملأ عند قراءة سطر `nb_drones:`
- `start_hub` → اسم منطقة البداية (يُملأ عند قراءة `start_hub:`)
- `end_hub` → اسم منطقة النهاية
- `network` → الشبكة الفارغة التي سنملأها
- `_seen_connections` → مجموعة للكشف عن الروابط المكررة (A-B و B-A نفس الشيء)

---

```python
    def parse(self) -> None:
        try:
            with open(self.filepath, "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Error: file not found: {self.filepath}", file=sys.stderr)
            sys.exit(1)
```
**السطور 29-35:** فتح الملف وقراءة كل الأسطر دفعة واحدة.
- `with open(...)` → يضمن إغلاق الملف تلقائياً حتى لو حدث خطأ
- `f.readlines()` → تعيد قائمة من الأسطر `["السطر1\n", "السطر2\n", ...]`
- إذا الملف غير موجود → طباعة خطأ واستوقاف البرنامج

---

```python
        for line_number, raw_line in enumerate(lines, start=1):
            line = raw_line.strip()
```
**السطران 37-38:** نمر على كل الأسطر.
- `enumerate(lines, start=1)` → يعطينا رقم السطر (يبدأ من 1) مع محتواه
- `raw_line.strip()` → يحذف المسافات والسطر الجديد `\n` من الطرفين

---

```python
            if not line or line.startswith("#"):
                continue
```
**السطران 40-41:** تخطي الأسطر الفارغة والتعليقات (`#`).

---

```python
            try:
                if line.startswith("nb_drones:"):
                    self._parse_nb_drones(line)
                elif line.startswith("start_hub:"):
                    self.start_hub = self._parse_zone_line(line)
                elif line.startswith("end_hub:"):
                    self.end_hub = self._parse_zone_line(line)
                elif line.startswith("hub:"):
                    self._parse_zone_line(line)
                elif line.startswith("connection:"):
                    self._parse_connection_line(line)
                else:
                    raise ValueError(f"unknown line format: '{line}'")
            except ValueError as error:
                print(f"Parse error on line {line_number}: {error}", file=sys.stderr)
                sys.exit(1)
```
**السطور 43-57:** قلب دالة `parse()`.
- ننظر لبداية كل سطر لمعرفة نوعه
- نستدعي الدالة المناسبة لكل نوع
- إذا كان السطر غير معروف → خطأ
- أي `ValueError` من الدوال الداخلية يُطبع مع رقم السطر ثم يوقف البرنامج

---

```python
    def _validate(self) -> None:
        """Check that the parsed map is complete and valid."""
        if self.nb_drones <= 0:
            ...sys.exit(1)
        if not self.start_hub:
            ...sys.exit(1)
        if not self.end_hub:
            ...sys.exit(1)
```
**السطور 59-67:** التحقق النهائي بعد قراءة الملف كله.
يتأكد أن: عدد الطائرات > 0، ومنطقة البداية موجودة، ومنطقة النهاية موجودة.

---

```python
    def _parse_nb_drones(self, line: str) -> None:
        _, value_str = line.split(":", 1)
        try:
            value = int(value_str.strip())
        except ValueError:
            raise ValueError(f"nb_drones must be an integer, got: '{value_str.strip()}'")
        if value <= 0:
            raise ValueError(f"nb_drones must be positive, got: {value}")
        self.nb_drones = value
```
**السطور 69-78:** تحليل سطر `nb_drones: 5`.
- `line.split(":", 1)` → يقسم عند أول `:` فقط → `["nb_drones", " 5"]`
- `int(value_str.strip())` → يحول `" 5"` إلى الرقم `5`
- يتحقق أن الرقم موجب

---

```python
    def _parse_metadata(self, meta_str: str) -> dict[str, str]:
        meta_str = meta_str.strip("[] ")
        result: dict[str, str] = {}
        for part in meta_str.split():
            if "=" in part:
                key, value = part.split("=", 1)
                result[key.strip()] = value.strip()
        return result
```
**السطور 80-89:** تحليل الـ metadata مثل `[zone=restricted color=red max_drones=2]`.
1. `strip("[] ")` → يحذف الأقواس المربعة والمسافات → `"zone=restricted color=red"`
2. `split()` → يقسم عند المسافات → `["zone=restricted", "color=red"]`
3. لكل جزء يحتوي `=`، يقسمه ويحفظه في القاموس
4. النتيجة: `{"zone": "restricted", "color": "red"}`

**هذه الدالة كانت مكسورة في الكود الأصلي** — كانت تحلل الـ metadata لكنها لا تطبقها على كائن Zone. الآن تعمل بشكل صحيح.

---

```python
    def _parse_zone_line(self, line: str) -> str:
        _, rest = line.split(":", 1)
        rest = rest.strip()

        meta: dict[str, str] = {}
        if "[" in rest:
            core_part, meta_part = rest.split("[", 1)
            meta = self._parse_metadata("[" + meta_part)
        else:
            core_part = rest

        parts = core_part.strip().split()
        name = parts[0]
        x = int(parts[1])
        y = int(parts[2])
        zone_type = meta.get("zone", "normal")
        color = meta.get("color", None)
        max_drones = int(meta.get("max_drones", "1"))

        zone = Zone(name=name, x=x, y=y, zone_type=zone_type,
                    color=color, max_drones=max_drones)
        self.network.add_zone(zone)
        return name
```
**السطور 91-126:** تحليل سطر `hub: roof1 3 4 [zone=restricted color=red]`.
1. يقسم السطر عند `:` → يحصل على الجزء بعد البادئة
2. إذا كان هناك `[` → يفصل الجزء الأساسي عن الـ metadata
3. يستخرج `name`, `x`, `y` من الجزء الأساسي
4. يستخرج `zone_type`, `color`, `max_drones` من الـ metadata (مع قيم افتراضية)
5. ينشئ كائن `Zone` ويضيفه للشبكة
6. يعيد الاسم (يستخدمه `parse()` لتعيين `start_hub` أو `end_hub`)

---

```python
    def _parse_connection_line(self, line: str) -> None:
        ...
        zone1, zone2 = core_part.split("-", 1)
        ...
        pair_key = "-".join(sorted([zone1, zone2]))
        if pair_key in self._seen_connections:
            raise ValueError(f"duplicate connection...")
        self._seen_connections.add(pair_key)
        ...
        conn = Connection(zone1, zone2, capacity)
        self.network.add_connection(conn)
```
**السطور 128-168:** تحليل سطر `connection: hub-roof1 [max_link_capacity=2]`.
- يقسم عند `-` للحصول على اسمي المنطقتين
- يتحقق أن المنطقتين موجودتان في الشبكة (يجب تعريف المنطقة قبل الرابط)
- يكشف الروابط المكررة: `sorted([zone1, zone2])` يجعل `hub-roof1` و `roof1-hub` نفس المفتاح
- ينشئ كائن `Connection` ويضيفه للشبكة
