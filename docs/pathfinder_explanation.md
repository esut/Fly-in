# شرح ملف `src/pathfinder.py`

## ما هو دور هذا الملف؟

`Pathfinder` يجد **أفضل مسار** بين منطقة البداية ومنطقة النهاية.
يستخدم **خوارزمية ديكسترا (Dijkstra)** — وهي خوارزمية مشهورة لإيجاد أقصر مسار في الغرافات.

## لماذا ديكسترا وليس BFS؟

- **BFS** يجد المسار بأقل **عدد خطوات** (كل خطوة = 1)
- **ديكسترا** يجد المسار بأقل **تكلفة إجمالية** (خطوات مختلفة لها تكاليف مختلفة)

في مشروعنا:
- منطقة `normal` → تكلفة 1 جولة
- منطقة `restricted` → تكلفة 2 جولات
- منطقة `priority` → تكلفة 0.9 (لتفضيلها على Normal)
- منطقة `blocked` → مستحيل دخولها

لذا ديكسترا أفضل لأن لدينا تكاليف مختلفة.

## علاقته بالملفات الأخرى

```
pathfinder.py
  ← يستورد   Network (network.py)
  ← يستخدمه  main.py (يطلب منه إيجاد المسار بعد تحميل الخريطة)
  → ينتج      قائمة أسماء المناطق: ["start", "zone1", "zone2", "goal"]
               هذه القائمة تذهب لـ Simulation
```

---

## شرح الكود سطراً بسطر

```python
import heapq
from typing import Optional
from network import Network
```
**السطور 1-3:**
- `heapq` → مكتبة Python المدمجة لعمل **Priority Queue** (طابور ذو أولوية).
  - الفكرة: نضع عناصر فيه مع "أولوية"، وعند السحب يخرج العنصر ذو الأولوية الأعلى (الأقل تكلفة).
  - هذا هو قلب خوارزمية ديكسترا.
- `Optional` → لأن الدالة قد تعيد `None` إذا لم يوجد مسار
- `Network` → الشبكة التي سنبحث فيها

---

```python
class Pathfinder:
    """
    Finds the shortest path between two zones using Dijkstra's algorithm.
    ...
    """
```
**السطران 6-13:** تعريف الكلاس. الـ docstring يشرح الخوارزمية وتكاليف كل نوع.

---

```python
    def __init__(self, network: Network) -> None:
        self.network = network
```
**السطران 15-17:** دالة بناء بسيطة — فقط نحفظ الشبكة.

---

```python
    def find_path(self, start: str, end: str) -> Optional[list[str]]:
        """
        Find the lowest-cost path from start zone to end zone.
        ...
        """
        if start not in self.network.zones:
            return None
        if end not in self.network.zones:
            return None
```
**السطور 19-29:** تحقق أولي — إذا البداية أو النهاية غير موجودة في الشبكة → `None`.

---

```python
        # Each entry in the heap: (accumulated_cost, zone_name, path_so_far)
        heap: list[tuple[float, str, list[str]]] = [(0.0, start, [start])]
```
**السطران 31-32:** ننشئ الـ heap ونضع فيه نقطة البداية.
- كل عنصر: `(التكلفة_المتراكمة, اسم_المنطقة, المسار_حتى_الآن)`
- نبدأ من منطقة `start` بتكلفة 0 ومسار يحتوي فقط على `[start]`

---

```python
        # Remember the best cost found to reach each zone
        best_cost: dict[str, float] = {}
```
**السطران 34-35:** قاموس يحفظ أقل تكلفة وصلنا بها لكل منطقة.
- إذا وصلنا لمنطقة بطريق أرخص → نحدّث القاموس
- إذا وصلنا بطريق أغلى → نتجاهله

---

```python
        while heap:
            cost, current_zone, path = heapq.heappop(heap)
```
**السطران 37-38:** الحلقة الرئيسية.
- `heapq.heappop(heap)` → يسحب العنصر ذو **أقل تكلفة** من الـ heap
- هذا يضمن أننا نعالج المناطق بترتيب من الأرخص للأغلى

---

```python
            # Skip if we already found a cheaper way to this zone
            if current_zone in best_cost:
                continue
            best_cost[current_zone] = cost
```
**السطور 40-43:**
- إذا سبق وزرنا هذه المنطقة بتكلفة أقل → تخطّها (لأن ما وجدناه الآن أغلى)
- وإلا → هذا هو أرخص طريق لهذه المنطقة، نسجله

---

```python
            # Found the destination
            if current_zone == end:
                return path
```
**السطران 45-47:** إذا وصلنا للنهاية → نعيد المسار مباشرة.
بما أن ديكسترا يعالج المناطق بالترتيب من الأرخص، فأول مرة نصل للنهاية = الطريق الأمثل.

---

```python
            # Look at all reachable neighbors
            for neighbor_name, _conn in self.network.get_neighbors(current_zone):
                if neighbor_name in best_cost:
                    continue

                neighbor_zone = self.network.zones[neighbor_name]

                if neighbor_zone.is_blocked():
                    continue
```
**السطور 49-56:** نمر على جيران المنطقة الحالية.
- إذا سبق وزرنا الجار → تخطّه
- إذا الجار `blocked` → تخطّه (لا يمكن دخوله)

---

```python
                # Cost to step into the neighbor zone
                if neighbor_zone.zone_type == "restricted":
                    step_cost = 2.0
                elif neighbor_zone.zone_type == "priority":
                    step_cost = 0.9  # Slightly cheaper so priority zones are preferred
                else:
                    step_cost = 1.0

                new_cost = cost + step_cost
                new_path = path + [neighbor_name]
                heapq.heappush(heap, (new_cost, neighbor_name, new_path))
```
**السطور 58-67:** حساب تكلفة الدخول للجار وإضافته للـ heap.
- `restricted` → 2.0 (يكلف جولتين حقيقيتين)
- `priority` → 0.9 (ليس 1.0 حتى يُفضّل على Normal وهو نفس التكلفة الحقيقية)
- `normal` → 1.0
- `new_path = path + [neighbor_name]` → نبني المسار الجديد بإضافة الجار

---

```python
        return None  # No path found
```
**السطر 69:** إذا فرغ الـ heap ولم نصل للنهاية → لا يوجد مسار.

---

## مثال مرئي لكيفية عمل الخوارزمية

```
الخريطة:  start → A(normal) → B(restricted) → end
          start → C(priority) → end

heap يبدأ:  [(0.0, "start", ["start"])]

جولة 1: نسحب (0.0, "start")
  جيران start: A (تكلفة 1.0), C (تكلفة 0.9)
  heap: [(0.9, "C", ["start","C"]), (1.0, "A", ["start","A"])]

جولة 2: نسحب (0.9, "C")  ← الأرخص
  جيران C: end (تكلفة 0.9+1.0=1.9)
  heap: [(1.0, "A", ["start","A"]), (1.9, "end", ["start","C","end"])]

جولة 3: نسحب (1.0, "A")
  جيران A: B (تكلفة 1.0+2.0=3.0)
  heap: [(1.9, "end", ...), (3.0, "B", ...)]

جولة 4: نسحب (1.9, "end") ← وصلنا!
  نعيد: ["start", "C", "end"]
```

النتيجة: المسار عبر `C (priority)` يُختار لأن تكلفته 1.9 أقل من المسار عبر `B (restricted)`.
