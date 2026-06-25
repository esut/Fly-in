# شرح ملف `src/connection.py`

## ما هو دور هذا الملف؟

هذا الملف يعرّف **كلاس `Connection`** — أي "الرابط" أو "المسار" بين منطقتين.
مثلاً: الخط `connection: hub-roof1` في الخريطة يصبح كائن `Connection`.
الروابط **ثنائية الاتجاه** — إذا كان هناك رابط بين A وB فالطائرة تسير في كلا الاتجاهين.

## علاقته بالملفات الأخرى

```
connection.py
  ← يستخدمه  network.py    (يخزن كائنات Connection في قائمة)
  ← يستخدمه  MapParser.py  (ينشئ كائنات Connection من قراءة الملف)
  ← يستخدمه  pathfinder.py (يتنقل عبر الروابط للبحث عن المسار)
  ← يستخدمه  simulation.py (يتحقق من سعة الرابط max_link_capacity)
  ← يستخدمه  visualizer.py (يرسم الأسهم بين المناطق)
```

---

## شرح الكود سطراً بسطر

```python
class Connection:
    """A bidirectional link between two zones."""
```
**السطر 1-2:** تعريف الكلاس. الـ docstring تقول إنه "رابط ثنائي الاتجاه بين منطقتين".

---

```python
    def __init__(
        self,
        zone1: str,
        zone2: str,
        max_link_capacity: int = 1,
    ) -> None:
```
**السطور 4-9:** دالة البناء.
- `zone1` → اسم المنطقة الأولى (نص، ليس كائن Zone)
- `zone2` → اسم المنطقة الثانية
- `max_link_capacity` → أقصى عدد طائرات تمر على هذا الرابط في نفس الوقت (افتراضي 1)

نلاحظ: نخزن **أسماء** المناطق وليس كائنات Zone. هذا أبسط ويكفي.

---

```python
        self.zone1 = zone1
        self.zone2 = zone2
        self.max_link_capacity = max_link_capacity
```
**السطور 10-12:** حفظ القيم كـ attributes.

---

```python
    def connects(self, zone_name: str) -> bool:
        """Check if this connection touches the given zone."""
        return zone_name == self.zone1 or zone_name == self.zone2
```
**السطور 14-16:** تعيد `True` إذا كان الرابط يمس المنطقة المعطاة.
مثلاً: `conn.connects("hub")` → يعيد `True` إذا كان الرابط بين `hub` وأي منطقة أخرى.
يستخدمها `network.get_neighbors()` لإيجاد جيران منطقة معينة.

---

```python
    def other_end(self, zone_name: str) -> str:
        """Given one zone, return the zone on the other end of this connection."""
        if zone_name == self.zone1:
            return self.zone2
        return self.zone1
```
**السطور 18-22:** بإعطائها اسم أحد طرفي الرابط، تعيد الطرف الآخر.
مثلاً: إذا الرابط هو `hub-roof1` وأعطيناها `"hub"` → تعيد `"roof1"`.
يستخدمها `network.get_neighbors()` لمعرفة الجار.

---

```python
    def key(self) -> str:
        """A consistent string key for this connection (alphabetical order)."""
        a, b = sorted([self.zone1, self.zone2])
        return f"{a}-{b}"
```
**السطور 24-27:** تعيد مفتاحاً ثابتاً للرابط بترتيب أبجدي.
مثلاً: سواء كان الرابط `hub-roof1` أو `roof1-hub` → المفتاح دائماً `"hub-roof1"`.
يستخدمها `visualizer.py` لتجنب رسم نفس الرابط مرتين.
يستخدمها `MapParser.py` للكشف عن الروابط المكررة.

---

```python
    def __str__(self) -> str:
        return f"Connection({self.zone1} <-> {self.zone2}, cap={self.max_link_capacity})"
```
**السطران 29-30:** طريقة طباعة الكائن.
مثلاً: `print(conn)` → `Connection(hub <-> roof1, cap=1)`

---

## ملخص

| Attribute           | النوع  | المعنى                                    |
|--------------------|--------|-------------------------------------------|
| `zone1`            | `str`  | اسم المنطقة الأولى                        |
| `zone2`            | `str`  | اسم المنطقة الثانية                       |
| `max_link_capacity`| `int`  | أقصى عدد طائرات تسير عليه في نفس الجولة  |

## مثال عملي

```
connection: hub-roof1 [max_link_capacity=2]
```
هذا الكود في الخريطة ينشئ:
```python
Connection(zone1="hub", zone2="roof1", max_link_capacity=2)
```
يعني: رابط بين `hub` و `roof1`، وطائرتان يمكنهما استخدامه في نفس الجولة.
