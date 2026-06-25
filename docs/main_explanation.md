# شرح ملف `src/main.py`

## ما هو دور هذا الملف؟

`main.py` هو **نقطة دخول البرنامج** — أول ما يُشغَّل عند تشغيل المشروع.
يربط كل الأجزاء الأخرى معاً بالترتيب الصحيح.

**الترتيب:**
```
1. قراءة مسار الخريطة من سطر الأوامر
2. تحليل الخريطة (MapParser)
3. إيجاد أفضل مسار (Pathfinder)
4. تشغيل المحاكاة (Simulation)
5. عرض الأنيميشن (Visualizer)
```

## طريقة التشغيل

```bash
python main.py ../maps/easy/01_linear_path.txt
```

## علاقته بالملفات الأخرى

```
main.py
  ← يستورد   MapParser   (map_parser.py)
  ← يستورد   Pathfinder  (pathfinder.py)
  ← يستورد   Simulation  (simulation.py)
  ← يستورد   Visualizer  (visualizer.py)
  → يمرر     network من MapParser → Pathfinder → Simulation → Visualizer
  → يمرر     path من Pathfinder → Simulation
  → يمرر     history من Simulation → Visualizer
```

هذا الملف لا يعرف كيف يعمل كل كلاس — فقط يستدعيهم بالترتيب.

---

## شرح الكود سطراً بسطر

```python
import sys
from MapParser import MapParser
from pathfinder import Pathfinder
from simulation import Simulation
from visualizer import Visualizer
```
**السطور 1-5:** الاستيرادات.
- `sys` → للوصول لـ `sys.argv` (معاملات سطر الأوامر) ولـ `sys.exit()`
- باقي الاستيرادات → الكلاسات الأربعة الرئيسية

---

```python
def main() -> None:
    """
    Entry point for the Fly-in drone routing simulation.

    Usage:
        python main.py <map_file>
    """
```
**السطور 8-14:** تعريف الدالة الرئيسية مع docstring يشرح طريقة الاستخدام.

---

```python
    if len(sys.argv) != 2:
        print("Usage: python main.py <map_file>", file=sys.stderr)
        sys.exit(1)

    map_file = sys.argv[1]
```
**السطور 15-19:** التحقق من المعاملات.
- `sys.argv` → قائمة بما كتبه المستخدم: `["main.py", "path/to/map.txt"]`
- `sys.argv[0]` → اسم الملف نفسه (`main.py`)
- `sys.argv[1]` → المعامل الأول (مسار الخريطة)
- إذا المستخدم لم يعطِ مسار → طباعة استخدام صحيح والخروج بكود خطأ 1

---

```python
    # Step 1: Parse the map file
    parser = MapParser(map_file)
    parser.parse()

    print(f"Map loaded: {parser.nb_drones} drones, "
          f"start='{parser.start_hub}', end='{parser.end_hub}'")
    print(f"Zones: {len(parser.network.zones)}, "
          f"Connections: {len(parser.network.connections)}\n")
```
**السطور 21-28:** الخطوة الأولى — تحليل الخريطة.
- `MapParser(map_file)` → إنشاء كائن Parser مع مسار الملف
- `parser.parse()` → قراءة الملف وبناء الشبكة (قد يوقف البرنامج عند خطأ)
- بعد `parse()`: `parser.network`, `parser.nb_drones`, `parser.start_hub`, `parser.end_hub` جاهزة
- نطبع ملخصاً للتأكيد

---

```python
    # Step 2: Find the best path from start to end
    finder = Pathfinder(parser.network)
    path = finder.find_path(parser.start_hub, parser.end_hub)

    if path is None:
        print("Error: no valid path found from start to end.", file=sys.stderr)
        sys.exit(1)

    print(f"Path found ({len(path) - 1} steps): {' -> '.join(path)}\n")
```
**السطور 30-38:** الخطوة الثانية — إيجاد المسار.
- نمرر `parser.network` للـ `Pathfinder` (الشبكة التي بناها الـ Parser)
- `find_path(start, end)` → يعيد قائمة مناطق أو `None`
- إذا لا يوجد مسار (مثلاً كل الطرق محجوبة) → خطأ وخروج
- نطبع المسار: `Path found (3 steps): start -> A -> B -> goal`

---

```python
    # Step 3: Run the simulation
    sim = Simulation(
        network=parser.network,
        nb_drones=parser.nb_drones,
        start_hub=parser.start_hub,
        end_hub=parser.end_hub,
        path=path,
    )
    sim.run()
```
**السطور 40-49:** الخطوة الثالثة — تشغيل المحاكاة.
- نمرر **كل شيء** من الخطوتين السابقتين: الشبكة، عدد الطائرات، البداية، النهاية، المسار
- `sim.run()` → يطبع كل جولة ويعيد عدد الجولات الكلي

---

```python
    # Step 4: Show the animated visualizer
    try:
        vis = Visualizer(parser.network, sim.history)
        vis.animate()
    except Exception as e:
        print(f"Visualizer could not run: {e}")
```
**السطور 51-55:** الخطوة الرابعة — الرسم المتحرك.
- `sim.history` → مواقع الطائرات لكل جولة (حُفظت أثناء `sim.run()`)
- نلفّ الـ Visualizer بـ `try/except` لأنه اختياري — إذا لم تكن مكتبة `matplotlib` مثبتة أو حدث خطأ رسومي، البرنامج لا يتعطل

---

```python
if __name__ == "__main__":
    main()
```
**السطران 58-59:** نمط Python القياسي.
- إذا شُغِّل الملف مباشرة (`python main.py`) → استدعاء `main()`
- إذا استُورد كـ module من ملف آخر → لا يُستدعى `main()` تلقائياً

---

## تدفق البيانات

```
map_file (string)
    ↓
MapParser.parse()
    ↓ ينتج
parser.network     ──────────────────────────────────→ Simulation
parser.nb_drones   ──────────────────────────────────→ Simulation
parser.start_hub   ──────────────────────────────────→ Simulation
parser.end_hub     ──────────────────────────────────→ Simulation
parser.network     ──→ Pathfinder.find_path()
                              ↓ ينتج
                         path (list[str])  ──────────→ Simulation
                                                            ↓ ينتج
                                               sim.history ──→ Visualizer
```
