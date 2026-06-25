# شرح ملف `src/simulation.py`

## ما هو دور هذا الملف؟

`Simulation` هو **قلب البرنامج** — ينفّذ المحاكاة جولة بجولة ويطبع النتائج.

كل جولة:
1. الطائرات التي كانت "في عبور" نحو منطقة restricted **تصل** إلى وجهتها
2. الطائرات الأخرى **تحاول التحرك** للمنطقة التالية (إذا سمحت السعة)
3. الجولة تُطبع بالصيغة المطلوبة: `D1-zone1 D2-zone2`

## علاقته بالملفات الأخرى

```
simulation.py
  ← يستورد   Network (network.py)
  ← يستورد   Drone   (drone.py)
  ← يستخدمه  main.py (يشغله بعد إيجاد المسار)
  → يطبع     نتائج كل جولة على الشاشة
  → يُرسل    self.history إلى Visualizer للرسم المتحرك
```

---

## شرح الكود سطراً بسطر

```python
from network import Network
from drone import Drone
```
**السطران 1-2:** الاستيرادات الضرورية.

---

```python
class Simulation:
    """
    Runs the drone routing simulation turn by turn.
    ...
    """

    MAX_TURNS = 1000
```
**السطور 4-28:** تعريف الكلاس.
`MAX_TURNS = 1000` → حد أقصى للجولات لمنع الحلقة اللانهائية في حالة الـ deadlock.

---

```python
    def __init__(
        self,
        network: Network,
        nb_drones: int,
        start_hub: str,
        end_hub: str,
        path: list[str],
    ) -> None:
```
**السطور 30-38:** دالة البناء — تأخذ:
- `network` → الخريطة
- `nb_drones` → عدد الطائرات
- `start_hub` → اسم منطقة البداية
- `end_hub` → اسم منطقة النهاية
- `path` → المسار الذي ستتبعه كل الطائرات

---

```python
        self.drones: list[Drone] = []
        for i in range(1, nb_drones + 1):
            drone = Drone(f"D{i}", start_hub)
            drone.set_path(path)
            self.drones.append(drone)
```
**السطور 43-47:** إنشاء جميع كائنات Drone وتعيين المسار لكل واحدة.
- `f"D{i}"` → يعطيها أسماء D1, D2, D3, ...
- `drone.set_path(path)` → كل الطائرات تتبع نفس المسار (الـ simulation يتحكم بالتوقيت)

---

```python
        self.zone_occupancy: dict[str, int] = {z: 0 for z in network.zones}
        self.zone_occupancy[start_hub] = nb_drones
```
**السطران 49-50:** قاموس يتتبع كم طائرة في كل منطقة.
- نبدأ بصفر في كل مكان
- ثم نضع كل الطائرات في منطقة البداية (مسموح لها بالتجمع هناك)

---

```python
        self.history: list[dict[str, str]] = []
        self._save_snapshot()
```
**السطران 52-53:** `history` يحفظ "لقطات" مواقع الطائرات لكل جولة.
هذا يُستخدم لاحقاً بواسطة `Visualizer` لرسم الأنيميشن.

---

```python
    def run(self) -> int:
        """Run the full simulation. Returns total number of turns taken."""
        turn = 1
        while not self._all_done():
            moves = self._run_one_turn()
            if moves:
                print(" ".join(moves))
            self._save_snapshot()
            turn += 1
            if turn > self.MAX_TURNS:
                print("Warning: simulation stopped (deadlock or too many turns).")
                break
        total_turns = turn - 1
        print(f"\nSimulation finished in {total_turns} turns.")
        return total_turns
```
**السطور 55-68:** الدالة الرئيسية.
1. كل جولة: نشغل `_run_one_turn()` الذي يعيد قائمة بالحركات
2. نطبع الحركات مفصولة بمسافة: `D1-roof1 D2-goal`
3. نحفظ لقطة جديدة
4. إذا تجاوزنا 1000 جولة → نوقف (تجنب deadlock لا نهائي)

---

```python
    def _all_done(self) -> bool:
        """Return True when every drone has reached the end zone."""
        return all(drone.is_done(self.end_hub) for drone in self.drones)
```
**السطران 70-72:** تتحقق أن كل طائرة وصلت للهدف.
`all(...)` تعيد `True` فقط إذا كان الشرط صحيحاً لكل عنصر.

---

```python
    def _save_snapshot(self) -> None:
        """Record current drone positions for the visualizer."""
        snapshot: dict[str, str] = {}
        for drone in self.drones:
            if drone.in_transit:
                snapshot[drone.id] = drone.transit_destination
            else:
                snapshot[drone.id] = drone.current_zone
        self.history.append(snapshot)
```
**السطور 74-82:** تسجيل أماكن الطائرات في هذه اللحظة.
- إذا الطائرة "في عبور" → نسجلها عند وجهتها (تقريباً)
- وإلا → نسجلها عند موقعها الفعلي
- تُستخدم هذه البيانات بواسطة `Visualizer`

---

```python
    def _run_one_turn(self) -> list[str]:
        """Execute one simulation turn and return the list of move strings."""
        moves: list[str] = []
```
**أهم دالة في الملف.** تعيد قائمة نصوص الحركات لهذه الجولة.

---

```python
        # --- Count how many transit drones will arrive at each zone this turn ---
        transit_arrivals: dict[str, int] = {}
        for drone in self.drones:
            if drone.in_transit:
                dest = drone.transit_destination
                transit_arrivals[dest] = transit_arrivals.get(dest, 0) + 1
```
**السطور 90-96:** نحسب كم طائرة ستصل من العبور هذه الجولة.
هذا مهم لحساب السعة الفعلية عند تقرير من يتحرك.
مثلاً: إذا طائرتان ستصلان لمنطقة Z هذه الجولة، فلا يمكن لطائرة ثالثة الدخول (إلا إذا `max_drones >= 3`).

---

```python
        # --- Phase B: decide which free drones can move ---
        departures: dict[str, int] = {z: 0 for z in self.network.zones}
        new_arrivals: dict[str, int] = dict(transit_arrivals)
        link_usage: dict[str, int] = {}
        planned: list[tuple[Drone, str, bool]] = []
```
**السطور 98-103:** إعداد متغيرات التتبع.
- `departures` → كم طائرة ستغادر كل منطقة (تُحرر مساحة)
- `new_arrivals` → كم طائرة ستصل لكل منطقة (تأخذ مساحة) — يبدأ بوصولات العبور
- `link_usage` → كم طائرة ستستخدم كل رابط هذه الجولة
- `planned` → قائمة الحركات المقررة (سنطبقها بعد القرار)

---

```python
        for drone in self.drones:
            if drone.is_done(self.end_hub) or drone.in_transit:
                continue

            next_zone_name = drone.get_next_zone()
            if next_zone_name is None:
                continue
```
**السطور 105-111:** نمر على الطائرات.
- إذا الطائرة وصلت للهدف أو في عبور → تخطّها
- إذا لا توجد منطقة تالية في المسار → تخطّها

---

```python
            # Effective occupancy of next_zone considering moves already planned this turn
            effective_occ = (
                self.zone_occupancy.get(next_zone_name, 0)
                - departures.get(next_zone_name, 0)
                + new_arrivals.get(next_zone_name, 0)
            )

            has_zone_space = is_end_zone or (effective_occ < next_zone.max_drones)
```
**السطور 115-122:** الحساب الذكي للسعة.
```
السعة الفعلية = الموجودون الآن - من سيغادرون + من سيصلون
```
- الطائرات التي غادرت هذه الجولة **تُفرج مساحة فوراً** (كما تنص القواعد)
- الطائرات التي ستصل هذه الجولة تأخذ مساحة
- إذا كانت المنطقة التالية هي النهاية → دائماً يُسمح (عدد لا محدود)

---

```python
            conn = self.network.find_connection(drone.current_zone, next_zone_name)
            link_key = f"{min(drone.current_zone, next_zone_name)}-{max(drone.current_zone, next_zone_name)}"
            has_link_space = True
            if conn:
                used = link_usage.get(link_key, 0)
                if used >= conn.max_link_capacity:
                    has_link_space = False
```
**السطور 124-130:** التحقق من سعة الرابط.
- `link_key` → مفتاح ثابت للرابط (أبجدي حتى `A-B` و`B-A` نفس المفتاح)
- إذا عدد الطائرات التي ستستخدم الرابط هذه الجولة = سعته القصوى → مليء

---

```python
            if not (has_zone_space and has_link_space):
                continue  # Drone waits this turn
```
**السطران 132-133:** إذا لا مساحة في المنطقة أو الرابط → الطائرة تنتظر هذه الجولة.

---

```python
            departures[drone.current_zone] = departures.get(drone.current_zone, 0) + 1
            if conn:
                link_usage[link_key] = link_usage.get(link_key, 0) + 1

            is_restricted = (next_zone.zone_type == "restricted")
            if not is_restricted:
                new_arrivals[next_zone_name] = new_arrivals.get(next_zone_name, 0) + 1

            planned.append((drone, next_zone_name, is_restricted))
```
**السطور 135-143:** نسجّل الحركة المخططة:
- نزيد `departures` للمنطقة الحالية
- نزيد `link_usage` للرابط المستخدم
- إذا الوجهة ليست restricted → نزيد `new_arrivals` (الطائرة ستصل هذه الجولة نفسها)
- إذا الوجهة restricted → لا نزيد `new_arrivals` (الطائرة ستصل الجولة القادمة)

---

```python
        # --- Apply Phase A: transit drones arrive ---
        for drone in self.drones:
            if drone.in_transit:
                dest = drone.transit_destination
                drone.complete_transit()
                moves.append(f"{drone.id}-{dest}")
```
**السطور 146-150:** تطبيق وصولات العبور.
- كل طائرة كانت `in_transit=True` تصل الآن
- نستدعي `complete_transit()` التي تحدّث موقع الطائرة
- نضيف `"D1-zoneName"` لقائمة الحركات

---

```python
        # --- Apply Phase B: planned moves execute ---
        for drone, destination, is_restricted in planned:
            from_zone = drone.current_zone
            if is_restricted:
                drone.start_transit_to(destination)
                moves.append(f"{drone.id}-{from_zone}-{destination}")
            else:
                drone.move_to(destination)
                moves.append(f"{drone.id}-{destination}")
```
**السطور 153-161:** تطبيق الحركات المخططة.
- إذا الوجهة restricted → نبدأ العبور (جولتان). الإخراج: `D1-zoneA-zoneBRestricted`
- وإلا → حركة عادية. الإخراج: `D1-zoneName`

---

```python
        # --- Rebuild zone occupancy from scratch ---
        self.zone_occupancy = {z: 0 for z in self.network.zones}
        for drone in self.drones:
            if not drone.in_transit:
                z = drone.current_zone
                if z in self.zone_occupancy:
                    self.zone_occupancy[z] += 1
```
**السطور 164-169:** إعادة حساب الشغل في كل منطقة.
- نبدأ من الصفر ونعيد العدّ من الطائرات الموجودة حالياً
- الطائرات "في عبور" لا تُحسب (هي في الهواء)
- أسهل من تعديل القاموس القديم — ونتجنب أخطاء الجمع/الطرح

---

## مثال لجولة كاملة

```
قبل الجولة:
  D1 في "A" (path_index=1), يريد الذهاب لـ "B" (normal, max_drones=1)
  D2 في "start", يريد الذهاب لـ "A"
  zone_occupancy = {"start": 1, "A": 1, "B": 0, "goal": 0}

الحساب:
  D1: next="B", effective_occ("B") = 0 - 0 + 0 = 0 < 1 ✓ تتحرك
      departures["A"] += 1 = 1
      new_arrivals["B"] += 1 = 1
  D2: next="A", effective_occ("A") = 1 - 1 + 0 = 0 < 1 ✓ تتحرك (A مُفرَجة بواسطة D1)
      departures["start"] += 1 = 1
      new_arrivals["A"] += 1 = 1

النتيجة: D1-B D2-A
zone_occupancy = {"start": 0, "A": 1, "B": 1, "goal": 0}
```
