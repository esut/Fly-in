# شرح ملف `src/zone.py`

## ما هو دور هذا الملف؟

هذا الملف يعرّف **كلاس `Zone`** — أي "المنطقة" أو الموقع في الخريطة.
كل منطقة في الخريطة (مثل `start`, `roof1`, `goal`) هي **كائن من نوع `Zone`**.

## علاقته بالملفات الأخرى

```
zone.py
  ← يستخدمه  network.py    (يخزن كائنات Zone في قاموس)
  ← يستخدمه  MapParser.py  (ينشئ كائنات Zone من قراءة الملف)
  ← يستخدمه  pathfinder.py (يقرأ zone_type لمعرفة تكلفة الحركة)
  ← يستخدمه  simulation.py (يقرأ max_drones و zone_type)
  ← يستخدمه  visualizer.py (يقرأ x, y, color لرسم الدوائر)
```

---

## شرح الكود سطراً بسطر

```python
from typing import Optional
```
**السطر 1:** نستورد `Optional` من مكتبة `typing`.
`Optional[str]` تعني أن القيمة ممكن تكون `str` أو `None`.
مثلاً: `color: Optional[str]` يعني اللون قد يكون موجوداً أو لا.

---

```python
class Zone:
    """A single location on the map that drones can visit."""
```
**السطر 4-5:** نعرّف الكلاس `Zone`.
الـ docstring تشرح أن كائن Zone = موقع واحد في الخريطة.

---

```python
    VALID_TYPES = ["normal", "restricted", "priority", "blocked"]
```
**السطر 7:** قائمة ثابتة بأنواع المناطق المسموح بها.
- `normal` → منطقة عادية، تكلفة 1 جولة
- `restricted` → منطقة خطرة، تكلفة 2 جولة
- `priority` → منطقة مفضلة، تكلفة 1 جولة (يُفضّلها الـ pathfinder)
- `blocked` → ممنوع الدخول نهائياً

يستخدم هذه القائمة `MapParser.py` للتحقق من أن نوع المنطقة صحيح.

---

```python
    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        zone_type: str = "normal",
        color: Optional[str] = None,
        max_drones: int = 1,
    ) -> None:
```
**السطور 9-18:** دالة البناء (constructor).
تُستدعى عندما نكتب `Zone(name="hub", x=0, y=0)`.
- `name` → الاسم الفريد للمنطقة (مثل `"hub"`, `"roof1"`)
- `x, y` → الإحداثيات على الخريطة (تستخدمها `visualizer.py` للرسم)
- `zone_type` → نوع المنطقة (القيمة الافتراضية `"normal"`)
- `color` → اللون الاختياري للعرض المرئي (مثل `"red"`, `"blue"`)
- `max_drones` → أقصى عدد طائرات تتواجد هنا في نفس الوقت (افتراضي 1)

---

```python
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.color = color
        self.max_drones = max_drones
```
**السطور 19-24:** نحفظ كل القيم كـ attributes في الكائن.
بعد هذا يمكن الوصول لها من أي مكان بكتابة `zone.name`, `zone.x`, إلخ.

---

```python
    def movement_cost(self) -> int:
        """How many simulation turns it costs a drone to enter this zone."""
        if self.zone_type == "restricted":
            return 2
        return 1
```
**السطور 26-30:** دالة تعيد تكلفة الدخول إلى هذه المنطقة بالجولات.
- منطقة `restricted` → 2 جولات (جولة للسفر + جولة للوصول)
- أي نوع آخر → 1 جولة

يستخدمها `pathfinder.py` لحساب أقصر مسار.

---

```python
    def is_blocked(self) -> bool:
        """Drones cannot enter blocked zones at all."""
        return self.zone_type == "blocked"
```
**السطور 32-34:** دالة تعيد `True` إذا كانت المنطقة محجوبة.
يستخدمها `pathfinder.py` لتخطي هذه المناطق أثناء البحث عن المسار.

---

```python
    def __str__(self) -> str:
        return f"Zone({self.name}, type={self.zone_type}, max_drones={self.max_drones})"
```
**السطران 36-37:** دالة خاصة — تُستدعى تلقائياً عند طباعة كائن Zone.
مثلاً: `print(zone)` سيطبع: `Zone(roof1, type=restricted, max_drones=1)`.

---

## ملخص: ما الذي يحفظه كائن Zone؟

| Attribute    | النوع           | المعنى                                    |
|-------------|-----------------|-------------------------------------------|
| `name`      | `str`           | الاسم الفريد للمنطقة                      |
| `x`         | `int`           | الإحداثية الأفقية (للرسم)                 |
| `y`         | `int`           | الإحداثية الرأسية (للرسم)                 |
| `zone_type` | `str`           | النوع: normal/restricted/priority/blocked |
| `color`     | `Optional[str]` | اللون الاختياري للعرض                     |
| `max_drones`| `int`           | أقصى عدد طائرات في نفس الوقت             |
