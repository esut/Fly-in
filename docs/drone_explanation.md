# شرح ملف `src/drone.py`

## ما هو دور هذا الملف؟

`Drone` يمثل **طائرة واحدة** في المحاكاة.
كل طائرة لها مسار محدد تتبعه، وتتقدم خطوة خطوة عبر الجولات.

**الميزة الأهم:** التعامل مع **المناطق المقيدة (restricted)** التي تستغرق جولتين للدخول.

## علاقته بالملفات الأخرى

```
drone.py
  ← يستخدمه  simulation.py (ينشئ كائنات Drone ويتحكم بها)
  ← يتلقى    مساره من main.py (عبر Simulation)
  → يُخبر    simulation.py بموقعه الحالي وما إذا كان في عبور
```

---

## شرح الكود سطراً بسطر

```python
from typing import Optional
```
**السطر 1:** نستورد `Optional` لأن `get_next_zone()` قد تعيد `None`.

---

```python
class Drone:
    """
    Represents a single drone flying through the map.

    A drone follows a pre-planned path zone by zone.
    When the next zone is 'restricted', entering it takes 2 turns:
        Turn 1: drone leaves current zone, enters the link (in_transit = True)
        Turn 2: drone arrives at the restricted zone (in_transit = False)
    """
```
**السطور 3-11:** الكلاس مع docstring يشرح آلية الجولتين للمناطق المقيدة.

---

```python
    def __init__(self, drone_id: str, start_zone: str) -> None:
        self.id = drone_id
        self.current_zone = start_zone
        self.path: list[str] = []
        self.path_index: int = 0
        self.in_transit: bool = False
        self.transit_destination: str = ""
```
**السطور 13-21:** دالة البناء.

| Attribute              | الوصف                                                          |
|-----------------------|----------------------------------------------------------------|
| `id`                  | اسم الطائرة: `"D1"`, `"D2"`, إلخ                             |
| `current_zone`        | اسم المنطقة التي الطائرة فيها **الآن** (بعد اكتمال آخر حركة)|
| `path`                | قائمة مناطق من البداية للنهاية: `["start","A","B","goal"]`   |
| `path_index`          | موقعنا في المسار (0 = في البداية)                            |
| `in_transit`          | `True` إذا الطائرة في الهواء نحو منطقة restricted            |
| `transit_destination` | اسم المنطقة التي نتجه إليها (فقط عندما `in_transit=True`)    |

---

```python
    def set_path(self, path: list[str]) -> None:
        """Assign a path to this drone and reset its position to the start."""
        self.path = path
        self.path_index = 0
```
**السطور 23-27:** تعيين المسار وإعادة الموضع للبداية.
يستدعيها `Simulation.__init__()` مرة واحدة لكل طائرة.

---

```python
    def is_done(self, end_zone: str) -> bool:
        """Return True if the drone has reached the end zone (and is not mid-transit)."""
        return self.current_zone == end_zone and not self.in_transit
```
**السطران 29-31:** الطائرة "انتهت" فقط إذا:
1. هي في منطقة النهاية
2. **و** ليست في عبور (تأكد أنها وصلت فعلاً وليست متجهة لمكان آخر)

---

```python
    def get_next_zone(self) -> Optional[str]:
        """Return the name of the next zone in the path, or None if already at the end."""
        next_index = self.path_index + 1
        if next_index < len(self.path):
            return self.path[next_index]
        return None
```
**السطور 33-38:** تعيد اسم المنطقة التالية في المسار.
- `path_index` هو موضعنا الحالي
- المنطقة التالية في `path_index + 1`
- إذا وصلنا لآخر المسار → `None` (لا يوجد "التالي")

**مثال:** المسار `["start", "A", "B", "goal"]`، الطائرة في `path_index=1` (عند "A")
→ `get_next_zone()` تعيد `"B"`

---

```python
    def start_transit_to(self, destination: str) -> None:
        """
        Begin a 2-turn move toward a restricted zone.
        The drone leaves its current zone but has not yet arrived at destination.
        """
        self.in_transit = True
        self.transit_destination = destination
```
**السطور 40-46:** تبدأ رحلة الجولتين نحو منطقة `restricted`.
- نضع `in_transit = True` → الطائرة الآن "في الهواء"
- نحفظ الوجهة في `transit_destination`
- لاحظ: **لا نغير** `current_zone` أو `path_index` هنا — سيتغيران في الجولة القادمة

---

```python
    def complete_transit(self) -> None:
        """Finish the 2-turn move — the drone arrives at its transit destination."""
        self.in_transit = False
        self.path_index += 1
        self.current_zone = self.transit_destination
        self.transit_destination = ""
```
**السطور 48-53:** الجولة الثانية — الطائرة تصل لوجهتها.
- `in_transit = False` → لم نعد في عبور
- `path_index += 1` → تقدمنا خطوة في المسار
- `current_zone = transit_destination` → وصلنا!
- `transit_destination = ""` → تنظيف

---

```python
    def move_to(self, destination: str) -> None:
        """Instantly move to the next zone (1-turn normal move)."""
        self.path_index += 1
        self.current_zone = destination
```
**السطران 55-58:** الحركة العادية (جولة واحدة).
- `path_index += 1` → تقدمنا في المسار
- `current_zone = destination` → وصلنا في نفس الجولة

---

```python
    def __str__(self) -> str:
        status = f"transit→{self.transit_destination}" if self.in_transit else self.current_zone
        return f"Drone({self.id} at {status})"
```
**السطران 60-62:** طريقة الطباعة.
- إذا في عبور → `Drone(D1 at transit→restricted_zone)`
- وإلا → `Drone(D1 at current_zone)`

---

## رسم توضيحي لحالة الطائرة

```
المسار: ["start", "A", "restricted_B", "goal"]

جولة 0: path_index=0, current_zone="start", in_transit=False
         ↓ تبدأ حركة نحو A (normal)
جولة 1: path_index=1, current_zone="A", in_transit=False
         ↓ تبدأ حركة نحو restricted_B → start_transit_to("restricted_B")
جولة 2: path_index=1, current_zone="A", in_transit=True, transit_destination="restricted_B"
         (الطائرة في الهواء بين A وB — لم تصل بعد)
         ↓ complete_transit() تُستدعى في الجولة التالية
جولة 3: path_index=2, current_zone="restricted_B", in_transit=False
         ↓ تتحرك نحو goal (normal)
جولة 4: path_index=3, current_zone="goal" ✓ DONE
```
