# شرح ملف `MapParser.py` — سطر بسطر

## نظرة عامة
ملف `MapParser.py` هو المسؤول عن **قراءة ملف الخريطة النصي (map file)** وتحويله إلى كائنات Python ( Zones, Connections, Network ) يمكن للباقي من النظام (البحث عن المسار، المحاكاة، العرض المرئي) استخدامها لاحقاً.

---

## 1. الاستيرادات (Imports)

```python
from zone import Zone
from connection import Connection
from network import Network
```
- **`Zone`**: كائن يمثل منطقة/محطة في الشبكة (لها اسم، إحداثيات x,y، نوع).
- **`Connection`**: كائن يمثل رابطاً ثنائي الاتجاه بين منطقتين.
- **`Network`**: هيكل البيانات الرئيسي الذي يخزن جميع المناطق والروابط على شكل رسم بياني (Graph).

---

## 2. تعريف الصنف `MapParser`

```python
class MapParser:
    """Parses the map text file into Zone and Connection objects."""
```
الصنف الأساسي الذي يحتوي على كل منطق تحليل الملف.

---

## 3. الدالة البانية `__init__`

```python
def __init__(self, filepath: str) -> None:
    self.filepath = filepath
    self.nb_drones: int = 0
    self.start_hub: str = ""
    self.end_hub: str = ""
    self.network: Network = Network()
```
| السطر | الوصف |
|-------|-------|
| 8 | يستقبل مسار الملف النصي (`filepath`). |
| 10 | `nb_drones`: عدد الطائرات بدون طيار (الدرونز) الذي سيتم تعريفه من الملف. |
| 11 | `start_hub`: اسم منطقة الانطلاق. |
| 12 | `end_hub`: اسم منطقة الوصول. |
| 13 | `network`: كائن شبكة فارغ سيتم ملؤه بالمناطق والروابط. |

---

## 4. الدالة الرئيسية `parse`

```python
def parse(self) -> None:
```
### 4.1 فتح الملف وقراءة الأسطر
```python
    try:
        with open(self.filepath, 'r') as file:
            lines = file.readlines()
```
- يفتح الملف للقراءة (`'r'`) ويحفظ جميع الأسطر في قائمة `lines`.
- محاط بـ `try/except` لمعالجة الأخطاء gracefully.

### 4.2 الحلقة على كل سطر
```python
        for line in lines:
            line = line.strip()
```
- يمر على كل سطر في الملف.
- `strip()` يزيل المسافات البيضاء والأسطر الجديدة من بداية ونهاية السطر.

### 4.3 تخطي الأسطر الفارغة والتعليقات
```python
            if not line or line.startswith('#'):
                continue
```
- إذا كان السطر فارغاً أو يبدأ بـ `#` (تعليق)، يتم تجاهله.

### 4.4 تحليل سطر `nb_drones`
```python
            if line.startswith('nb_drones'):
                parts = line.split(':')
                self.nb_drones = int(parts[1].strip())
                print(f"find  drone:{self.nb_drones}")
```
- يبحث عن سطر يبدأ بـ `nb_drones`.
- يقسم السطر عند `:` → الجزء الأول هو `nb_drones`، والجزء الثاني هو العدد.
- يحول العدد إلى رقم صحيح (`int`) ويخزنه.

### 4.5 تحليل سطر `start_hub` و `end_hub`
```python
            elif line.startswith('start_hub:'):
                self.start_hub = self.parse_zone_line(line, default_type="normal")
            elif line.startswith('end_hub:'):
                self.end_hub = self.parse_zone_line(line, default_type="normal")
```
- يحدد منطقة الانطلاق ومنطقة الوصول.
- يمرر `default_type="normal"` لأن هذه المناطق لا تحمل نوعاً خاصاً في الملف.

### 4.6 تحليل سطر `hub` (مناطق عادية)
```python
            elif line.startswith('hub:'):
                self.parse_zone_line(line, default_type="normal")
```
- يقرأ أي منطقة عادية أخرى في الشبكة.

### 4.7 تحليل سطر `connection` (روابط)
```python
            elif line.startswith('connection:'):
                self.parse_connection_line(line)
```
- يقرأ الرابط بين منطقتين.

### 4.8 معالجة الأخطاء
```python
        except FileNotFoundError:
            print(f"Error: Could not find the file {self.filepath}")
        except Exception as e:
            print(f"Parsing Error:{e}")
```
- `FileNotFoundError`: إذا لم يوجد الملف.
- `Exception`: أي خطأ آخر أثناء التحليل.

---

## 5. الدالة `parse_zone_line`

```python
def parse_zone_line(self, line: str, default_type: str = "normal") -> None:
```
### 5.1 فصل البادئة عن باقي السطر
```python
    prefix, rest_of_line = line.split(':', 1)
    rest_of_line = rest_of_line.strip()
```
- يقسم السطر مرة واحدة عند أول `:` فقط.
- الباقي (`rest_of_line`) هو البيانات الفعلية للمنطقة.

### 5.2 استخراج البيانات الوصفية (Metadata)
```python
    metadata_str = ""
    if '[' in rest_of_line:
        core_info, meta_info = rest_of_line.split('[', 1)
        metadata_str = "[" + meta_info
    else:
        core_info = rest_of_line
```
- إذا كان السطر يحتوي على `[`، فهناك بيانات إضافية (مثل `max_drones=3`).
- `core_info`: الجزء الأساسي (الاسم والإحداثيات).
- `meta_info`: الجزء داخل الأقواس.

### 5.3 استخراج الاسم والإحداثيات
```python
    data_parts = core_info.split()

    if len(data_parts) < 3:
        raise ValueError(f"error: {line}")

    name = data_parts[0]
    x = int(data_parts[1])
    y = int(data_parts[2])
```
- يقسم `core_info` إلى كلمات.
- يتأكد من وجود 3 أجزاء على الأقل (الاسم، x، y).
- يحول الإحداثيات إلى أعداد صحيحة.

### 5.4 إنشاء كائن `Zone` وإضافته للشبكة
```python
    new_zone = Zone(name=name, x=x, y=y, zone_type=default_type)
    self.network.add_zone(new_zone)
    print(f" add new zone :{name}, X={x}, Y={y}")
```
- ينشئ كائن `Zone`.
- يضيفه إلى `Network` (يحفظه في القاموس `zones` ويجهز قائمة الجوار `adjacency_list`).

### 5.5 إرجاع اسم المنطقة
```python
    return name
```
- يعيد اسم المنطقة ليتم تخزينه في `start_hub` أو `end_hub`.

---

## 6. الدالة `parse_metadata`

```python
def parse_metadata(self, meta_str: str) -> dict[str, str]:
```
### 6.1 تنظيف النص
```python
    meta_str = meta_str.strip(" []")
    if not meta_str:
        return {}
```
- يزيل الأقواس والمسافات من البداية والنهاية.
- إذا كان فارغاً، يرجع قاموساً فارغاً.

### 6.2 تقسيم إلى أزواج مفتاح=قيمة
```python
    meta_dict = {}
    parts = meta_str.split()

    for part in parts:
        if '=' in part:
            key, value = part.split('=', 1)
            meta_dict[key] = value
```
- يقسم النص إلى كلمات.
- كل كلمة تحتوي على `=` تُقسم إلى مفتاح وقيمة.

**مثال:**
```
[max_link_capacity=5 max_drones=10]
```
يُحوَّل إلى:
```python
{'max_link_capacity': '5', 'max_drones': '10'}
```

---

## 7. الدالة `parse_connection_line`

```python
def parse_connection_line(self, line: str) -> None:
```
### 7.1 فصل البادئة
```python
    prefix, rest_of_line = line.split(':', 1)
    rest_of_line = rest_of_line.strip()
```
- نفس فكرة `parse_zone_line`: يفصل `connection:` عن البيانات.

### 7.2 استخراج البيانات الوصفية (إذا وجدت)
```python
    meta_dict = {}
    if '[' in rest_of_line:
        core_info, meta_info = rest_of_line.split('[', 1)
        meta_dict = self.parse_metadata("[" + meta_info)
    else:
        core_info = rest_of_line
```
- يستخدم `parse_metadata` لاستخراج السعة القصوى للرابط مثلاً.

### 7.3 استخراج اسمي المنطقتين
```python
    core_info = core_info.strip()
    try:
        zone1, zone2 = core_info.split('-')
    except ValueError:
        raise ValueError(f"  error  zone1-zone2: {line}")
```
- يقسم `core_info` عند `-` للحصول على اسم المنطقة الأولى والثانية.
- مثال: `A-B` → `zone1="A"`, `zone2="B"`.

### 7.4 إنشاء كائن `Connection` وإضافته
```python
    capacity = int(meta_dict.get('max_link_capacity', 1))
    new_conn = Connection(zone1, zone2, capacity)
    self.network.add_connection(new_conn)
    print(f" done {zone1} and {zone2} capacity {capacity}")
```
- يأخذ السعة من الميتاداتيا، وإذا لم تكن موجودة تكون القيمة الافتراضية `1`.
- يضيف الرابط إلى الشبكة (يضيفه لقائمة جوار `zone1` وقائمة جوار `zone2`).

---

## 8. البلوك الرئيسي `if __name__ == "__main__"`

```python
if __name__ == "__main__":
    from pathfinder import Pathfinder

    parser = MapParser("../maps/eas")
    parser.parse()
```
### 8.1 إنشاء المحلل وتشغيله
- ينشئ كائن `MapParser` مع مسار ملف الخريطة.
- يطلب منه `parse()` لقراءة الملف وبناء الشبكة.

### 8.2 اختبار إيجاد المسار (BFS)
```python
    print("\n--- Pathfinding Test ---")
    if parser.start_hub and parser.end_hub:
        finder = Pathfinder(parser.network)
        path = finder.find_shortest_path_bfs(parser.start_hub, parser.end_hub)
```
- إذا عُرفت نقطة البداية والنهاية، يستخدم `Pathfinder` لإيجاد أقصر مسار بينهما باستخدام خوارزمية BFS.

### 8.3 تشغيل المحاكاة
```python
    if path:
        print(f"✅ تم العثور على أقصر مسار: {' -> '.join(path)}\n")
        print("--- بدء المحاكاة ---")
        from simulation import Simulation
        sim = Simulation(parser.network, parser.nb_drones, parser.start_hub, parser.end_hub, path)
        sim.run()
```
- إذا وُجد مسار، ينشئ محاكاة (`Simulation`) ويرسل لها:
  - الشبكة (`network`)
  - عدد الدرونز (`nb_drones`)
  - نقطة البداية والنهاية
  - المسار (`path`)

### 8.4 تشغيل العرض المرئي
```python
        print("--- جاري تشغيل العرض المرئي ---")
        from visualizer import Visualizer
        vis = Visualizer(parser.network, sim.history)
        vis.animate()
```
- ينشئ `Visualizer` ويمرر له:
  - الشبكة لرسم المناطق والروابط.
  - `sim.history`: سجل جولات الدرونز لإنشاء الرسوم المتحركة.

---

## تنسيق ملف الخريطة المتوقع (Map File Format)

| البادئة | الصيغة | مثال |
|-----------|--------|------|
| `nb_drones` | `nb_drones: <عدد>` | `nb_drones: 5` |
| `start_hub` | `start_hub: <الاسم> <x> <y>` | `start_hub: A 0 0` |
| `end_hub` | `end_hub: <الاسم> <x> <y>` | `end_hub: Z 10 10` |
| `hub` | `hub: <الاسم> <x> <y> [ميتاداتيا]` | `hub: B 5 5 [max_drones=2]` |
| `connection` | `connection: <المنطقة1>-<المنطقة2> [max_link_capacity=<عدد>]` | `connection: A-B [max_link_capacity=3]` |

---

## ملخص تدفق العمل

1. **الاستيراد**: يستورد الصنفات الأساسية (`Zone`, `Connection`, `Network`).
2. **التهيئة**: يخزن مسار الملف ويجهز متغيرات الشبكة.
3. **التحليل**: يقرأ الملف سطراً بسطر ويتعرف على نوع كل سطر.
4. **بناء الشبكة**: ينشئ كائنات `Zone` و `Connection` ويضيفها إلى `Network`.
5. **الاختبار**: في البلوك الرئيسي، يختبر إيجاد المسار وتشغيل المحاكاة والعرض المرئي.

---

## ملاحظات تقنية

- الملف لا يعيد كائن `Network` صراحة، بل يخزنه كسمة `parser.network`.
- الدوال `parse_zone_line` و `parse_connection_line` مسؤولة عن تقسيم السطر وتحويله إلى كائنات.
- البيانات الوصفية (metadata) اختيارية وتُعالج بواسطة `parse_metadata`.
- يوجد بعض المطابعات (`print`) داخل الدوال لأغراض التصحيح (debugging).
