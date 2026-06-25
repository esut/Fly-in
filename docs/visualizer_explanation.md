# شرح ملف `src/visualizer.py`

## ما هو دور هذا الملف؟

`Visualizer` يرسم **أنيميشن متحرك** للمحاكاة باستخدام مكتبة `matplotlib`.
- يرسم المناطق كدوائر ملونة
- يرسم الروابط كأسهم بين الدوائر
- يحرّك الطائرات (معينات زرقاء) جولة بجولة

هذا الجزء اختياري (يُغلف بـ `try/except` في main.py) ولكنه يجعل فهم المحاكاة بصرياً أسهل.

## علاقته بالملفات الأخرى

```
visualizer.py
  ← يستورد   Network (network.py)
  ← يستخدمه  main.py (آخر خطوة بعد انتهاء Simulation)
  ← يتلقى    history من Simulation (مواقع الطائرات لكل جولة)
  لا يُعدّل أي بيانات — فقط يقرأ ويرسم
```

---

## شرح الكود سطراً بسطر

```python
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from network import Network
```
**السطور 1-3:** الاستيرادات.
- `matplotlib.pyplot` → مكتبة الرسم الرئيسية في Python
- `FancyArrowPatch` → لرسم أسهم جميلة بين المناطق
- `Network` → للوصول لمناطق الخريطة وروابطها

---

```python
ZONE_TYPE_COLORS: dict[str, str] = {
    "normal":     "lightblue",
    "restricted": "salmon",
    "priority":   "lightgreen",
    "blocked":    "dimgray",
}
```
**السطور 6-11:** قاموس يعين لوناً افتراضياً لكل نوع منطقة.
- `normal` → أزرق فاتح
- `restricted` → لون سلمون (برتقالي محمر) — خطر
- `priority` → أخضر فاتح — مفضّل
- `blocked` → رمادي داكن — ممنوع

إذا كانت المنطقة تملك لوناً خاصاً (`zone.color`) فيُستخدم ذلك بدلاً من هذا الافتراضي.

---

```python
class Visualizer:
    """
    Draws the map and animates drone movements turn by turn using matplotlib.
    ...
    """

    def __init__(self, network: Network, history: list[dict[str, str]]) -> None:
        self.network = network
        self.history = history
```
**السطور 14-27:** الكلاس ودالة البناء.
- `network` → الخريطة (المناطق والروابط)
- `history` → قائمة من القواميس. كل عنصر = جولة، والقاموس هو `{drone_id: zone_name}`
  - مثلاً: `[{"D1":"start","D2":"start"}, {"D1":"A","D2":"start"}, ...]`

---

```python
    def animate(self) -> None:
        """Draw the network and animate the drones through all recorded turns."""
        plt.ion()
        fig, ax = plt.subplots(figsize=(12, 8))
```
**السطور 29-32:**
- `plt.ion()` → تشغيل "التفاعلي" (Interactive Mode) — يسمح تحديث الرسم بدون إيقاف البرنامج
- `plt.subplots(figsize=(12, 8))` → إنشاء نافذة رسم 12×8 بوصة

---

```python
        # Draw connections as arrows (only once, they don't change)
        self._draw_connections(ax)

        # Draw zones as circles (only once, they don't change)
        self._draw_zones(ax)

        ax.grid(True, linestyle="--", alpha=0.4)
        ax.set_facecolor("#f8f9fa")
        ax.margins(0.25)
        plt.axis("equal")
```
**السطور 34-41:** رسم الأجزاء الثابتة مرة واحدة.
- الروابط والمناطق لا تتغير → نرسمها مرة واحدة
- `grid` → شبكة خطوط خفيفة في الخلفية
- `set_facecolor` → لون خلفية الرسم (رمادي فاتح جداً)
- `margins(0.25)` → هامش حول الرسم لمنع التصاق الدوائر بالحواف
- `axis("equal")` → نضمن أن الوحدات في المحورين متساوية (الدوائر لا تبدو بيضاوية)

---

```python
        # Animate: redraw drone markers each turn
        drone_markers: list[object] = []

        for turn, snapshot in enumerate(self.history):
            # Remove old drone markers
            for marker in drone_markers:
                marker.remove()
            drone_markers.clear()
```
**السطور 43-50:** حلقة الأنيميشن.
- `drone_markers` → قائمة العناصر الرسومية للطائرات
- في كل جولة: نحذف العلامات القديمة ثم نرسم الجديدة
- هذا يعطي وهم الحركة

---

```python
            for drone_id, zone_name in snapshot.items():
                zone = self.network.zones.get(zone_name)
                if zone is None:
                    continue

                drone_number = int(drone_id[1:])
                offset_x = (drone_number % 3 - 1) * 0.12
                offset_y = (drone_number % 2) * 0.12
```
**السطور 52-59:** لكل طائرة في هذه الجولة:
- نحصل على كائن Zone بالاسم
- نحسب **إزاحة** صغيرة حتى لا تتراكب الطائرات عند نفس النقطة
  - مثلاً: D1 offset=(0,0), D2 offset=(0.12,0.12), D3 offset=(-0.12,0)
  - `drone_id[1:]` → يأخذ الرقم من "D3" → `"3"` → `int` → `3`

---

```python
                scatter = ax.scatter(
                    zone.x + offset_x,
                    zone.y + offset_y,
                    s=500,
                    c="royalblue",
                    marker="D",
                    edgecolors="gold",
                    linewidths=1.5,
                    zorder=4,
                )
                label = ax.text(...)
                drone_markers.append(scatter)
                drone_markers.append(label)
```
**السطور 61-76:** رسم كل طائرة كـ "معين أزرق" مع اسمها.
- `ax.scatter(x, y, ...)` → رسم نقطة بالإحداثيات
- `s=500` → حجم العلامة
- `c="royalblue"` → اللون الأزرق الملكي
- `marker="D"` → شكل معين ◆
- `edgecolors="gold"` → حافة ذهبية
- `zorder=4` → تُرسم فوق الدوائر (الـ zorder الأعلى = أمام)

---

```python
            ax.set_title(f"Fly-in Simulation  —  Turn {turn}", ...)
            plt.draw()
            plt.pause(0.6)
```
**السطور 78-81:**
- `set_title` → يظهر رقم الجولة في أعلى النافذة
- `plt.draw()` → يُحدّث الرسم
- `plt.pause(0.6)` → ينتظر 0.6 ثانية قبل الجولة التالية (يمكن تغييره لتسريع/إبطاء الأنيميشن)

---

```python
        plt.ioff()
        plt.show()
```
**السطران 83-84:**
- `plt.ioff()` → إيقاف الوضع التفاعلي
- `plt.show()` → إبقاء النافذة مفتوحة حتى يغلقها المستخدم

---

```python
    def _draw_connections(self, ax: plt.Axes) -> None:
        drawn: set[str] = set()
        for zone_name in self.network.zones:
            for neighbor_name, conn in self.network.get_neighbors(zone_name):
                pair = conn.key()
                if pair in drawn:
                    continue
                drawn.add(pair)

                z1 = self.network.zones[zone_name]
                z2 = self.network.zones[neighbor_name]

                arrow = FancyArrowPatch(
                    (z1.x, z1.y),
                    (z2.x, z2.y),
                    arrowstyle="<|-|>",
                    ...
                )
                ax.add_patch(arrow)
```
**السطور 87-114:** رسم الروابط كأسهم.
- `drawn` → مجموعة لتجنب رسم نفس الرابط مرتين
- `conn.key()` → مفتاح فريد للرابط (أبجدي)
- `FancyArrowPatch` → يرسم سهماً جميلاً ثنائي الرأس `<|-|>` بين إحداثيات منطقتين
- إذا `max_link_capacity > 1` → يطبع `cap=2` في منتصف الرابط

---

```python
    def _draw_zones(self, ax: plt.Axes) -> None:
        for name, zone in self.network.zones.items():
            if zone.color:
                color = zone.color
            else:
                color = ZONE_TYPE_COLORS.get(zone.zone_type, "lightblue")

            ax.scatter(zone.x, zone.y, s=4000, ...)
            ax.text(zone.x, zone.y, name, ...)
```
**السطور 116-129:** رسم المناطق كدوائر.
- إذا المنطقة لها لون خاص (من الخريطة) → نستخدمه
- وإلا → نستخدم اللون من قاموس `ZONE_TYPE_COLORS`
- `s=4000` → دوائر كبيرة واضحة
- `ax.text(...)` → اسم المنطقة في وسط الدائرة

---

## كيف يبدو الإخراج المرئي؟

```
┌─────────────────────────────────────────┐
│    Fly-in Simulation — Turn 2           │
│                                         │
│   ○ start        ◆D2                   │
│      │                                  │
│   ○ A   ─────── ○ B(restricted)        │
│      │                                  │
│   ◆D1─→ ○ goal                         │
└─────────────────────────────────────────┘
```
- الدوائر الكبيرة = مناطق (ملونة حسب النوع)
- المعينات الزرقاء = طائرات
- الأسهم = روابط بين المناطق
- الرقم في الأعلى = رقم الجولة الحالية
