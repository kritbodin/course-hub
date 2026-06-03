# คู่มือสร้างเว็บรวมรายวิชา (JSON + Static + GitHub Pages)

> สำหรับนำไปทำต่อใน **Claude Cowork** — มีโค้ดเริ่มต้นครบทุกไฟล์ + prompt สำเร็จรูปท้ายเอกสาร

---

## 1. ภาพรวมโปรเจกต์

**เป้าหมาย:** เว็บหน้าเดียวที่รวมทุกวิชาที่สอน นักศึกษาเข้ามาดู ตารางสอน / สไลด์ / งานรายสัปดาห์ ส่วนการส่งงานใช้ MS Teams Assignment ตามเดิม

**สถาปัตยกรรม (ไม่มีเซิร์ฟเวอร์):**

| ส่วน | เครื่องมือ |
|------|-----------|
| ข้อมูลวิชา | ไฟล์ `courses.json` (แก้ใน VS Code / Cowork) |
| สร้างหน้าเว็บ | สคริปต์ Python + Jinja2 (`build.py`) |
| ไฟล์สไลด์/เอกสาร | OneDrive (ทำลิงก์มาใส่ใน JSON) |
| โฮสต์เว็บ | GitHub Pages (ฟรี ไม่ต้องจดโดเมน) |
| ส่งงาน | MS Teams Assignment |

**หลักการ:** แก้ข้อมูลที่ JSON → รัน `build.py` → ได้ HTML → push ขึ้น GitHub → เว็บอัปเดตอัตโนมัติ

---

## 2. Repository — สร้างใหม่แยกเฉพาะ

- สร้าง repo ใหม่ชื่อเช่น **`course-hub`** หรือ **`my-courses`**
- ตั้งเป็น **Public** (GitHub Pages ฟรีรองรับเฉพาะ repo public; ถ้า private ต้องเสียเงิน)
- ⚠️ ห้ามใส่ข้อมูลส่วนตัว/รหัสผ่าน/ข้อมูลนักศึกษา ลงใน repo เพราะเป็น public
- ลิงก์ Teams และ OneDrive ที่ใส่ ควรเป็นลิงก์แบบ "ดูอย่างเดียว / anyone with the link"

---

## 3. โครงสร้างโปรเจกต์

```
course-hub/
├── data/
│   └── courses.json        ← ข้อมูลวิชาทั้งหมด (แก้แค่ไฟล์นี้เป็นหลัก)
├── templates/
│   ├── index.html          ← หน้ารวมวิชา
│   └── course.html          ← หน้ารายวิชา
├── static/
│   └── style.css            ← สไตล์
├── build.py                 ← สคริปต์สร้างเว็บ
├── requirements.txt
└── docs/                    ← โฟลเดอร์ผลลัพธ์ (GitHub Pages เสิร์ฟจากตรงนี้)
```

---

## 4. ไฟล์เริ่มต้น (โค้ดครบ)

### 4.1 `requirements.txt`
```
Jinja2
```

### 4.2 `data/courses.json`
```json
{
  "courses": [
    {
      "code": "CS101",
      "name": "การเขียนโปรแกรมเบื้องต้น",
      "semester": "1/2569",
      "schedule": "จันทร์ 09:00-12:00 ห้อง 1201",
      "teams_link": "https://teams.microsoft.com/l/team/xxxx",
      "weeks": [
        {
          "week": 1,
          "topic": "แนะนำรายวิชาและการติดตั้งเครื่องมือ",
          "slide_url": "https://onedrive.live.com/xxxx",
          "assignment": "ติดตั้ง Python และ VS Code"
        },
        {
          "week": 2,
          "topic": "ตัวแปรและชนิดข้อมูล",
          "slide_url": "https://onedrive.live.com/xxxx",
          "assignment": "แบบฝึกหัดบทที่ 2 (ส่งใน Teams)"
        }
      ]
    },
    {
      "code": "DM402",
      "name": "การทำเหมืองข้อมูล",
      "semester": "1/2569",
      "schedule": "พุธ 13:00-16:00 ห้อง 1305",
      "teams_link": "https://teams.microsoft.com/l/team/yyyy",
      "weeks": [
        {
          "week": 1,
          "topic": "แนะนำการทำเหมืองข้อมูล",
          "slide_url": "https://onedrive.live.com/yyyy",
          "assignment": ""
        }
      ]
    }
  ]
}
```

### 4.3 `build.py`
```python
import json
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).parent
DATA = ROOT / "data" / "courses.json"
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
OUTPUT = ROOT / "docs"


def main():
    # 1) อ่านข้อมูลวิชา
    with open(DATA, encoding="utf-8") as f:
        courses = json.load(f)["courses"]

    # 2) เตรียม Jinja2
    env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=True)

    # 3) ล้างและสร้างโฟลเดอร์ผลลัพธ์ใหม่
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True)

    # 4) คัดลอกไฟล์ static (CSS ฯลฯ)
    if STATIC.exists():
        shutil.copytree(STATIC, OUTPUT / "static")

    # 5) สร้างหน้ารวมวิชา
    index_html = env.get_template("index.html").render(courses=courses)
    (OUTPUT / "index.html").write_text(index_html, encoding="utf-8")

    # 6) สร้างหน้าของแต่ละวิชา
    course_tmpl = env.get_template("course.html")
    for course in courses:
        page = course_tmpl.render(course=course)
        (OUTPUT / f"{course['code']}.html").write_text(page, encoding="utf-8")

    # 7) บอก GitHub Pages ไม่ต้องประมวลผลด้วย Jekyll
    (OUTPUT / ".nojekyll").write_text("", encoding="utf-8")

    print(f"สร้างเว็บสำเร็จ: {len(courses)} วิชา -> {OUTPUT}")


if __name__ == "__main__":
    main()
```

### 4.4 `templates/index.html`
```html
<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>รายวิชาที่สอน</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="static/style.css">
</head>
<body>
  <header class="site-header">
    <h1>รายวิชาที่สอน</h1>
    <p class="muted">มหาวิทยาลัยราชภัฏศรีสะเกษ</p>
  </header>
  <main>
    <div class="course-grid">
      {% for course in courses %}
      <a class="course-card" href="{{ course.code }}.html">
        <span class="code">{{ course.code }}</span>
        <span class="name">{{ course.name }}</span>
        <span class="term">ภาคเรียน {{ course.semester }}</span>
      </a>
      {% endfor %}
    </div>
  </main>
</body>
</html>
```

### 4.5 `templates/course.html`
```html
<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ course.code }} - {{ course.name }}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@400;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="static/style.css">
</head>
<body>
  <header class="site-header">
    <p><a href="index.html">← กลับหน้ารวมวิชา</a></p>
    <h1>{{ course.name }}</h1>
    <p class="muted">{{ course.code }} · ภาคเรียน {{ course.semester }}</p>
  </header>
  <main>
    <section class="info-box">
      <p><strong>ตารางสอน:</strong> {{ course.schedule }}</p>
      {% if course.teams_link %}
      <p><a class="btn" href="{{ course.teams_link }}" target="_blank" rel="noopener">เปิด MS Teams (ส่งงาน)</a></p>
      {% endif %}
    </section>

    <section>
      <h2>เนื้อหารายสัปดาห์</h2>
      <table>
        <thead>
          <tr>
            <th>สัปดาห์</th>
            <th>หัวข้อ</th>
            <th>สไลด์/เอกสาร</th>
            <th>งาน</th>
          </tr>
        </thead>
        <tbody>
          {% for w in course.weeks %}
          <tr>
            <td>{{ w.week }}</td>
            <td>{{ w.topic }}</td>
            <td>
              {% if w.slide_url %}
                <a href="{{ w.slide_url }}" target="_blank" rel="noopener">เปิดสไลด์</a>
              {% else %}-{% endif %}
            </td>
            <td>{{ w.assignment or "-" }}</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </section>
  </main>
</body>
</html>
```

### 4.6 `static/style.css`
```css
:root {
  --bg: #f7f8fa;
  --card: #ffffff;
  --ink: #1f2933;
  --muted: #6b7280;
  --accent: #2563eb;
  --border: #e5e7eb;
}
* { box-sizing: border-box; }
body {
  font-family: "Sarabun", system-ui, sans-serif;
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  line-height: 1.6;
}
.site-header {
  background: var(--card);
  padding: 2rem 1.25rem;
  border-bottom: 1px solid var(--border);
}
.site-header h1 { margin: .25rem 0; }
.muted { color: var(--muted); }
main { max-width: 880px; margin: 0 auto; padding: 1.5rem 1.25rem; }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }

.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1rem;
}
.course-card {
  display: flex;
  flex-direction: column;
  gap: .35rem;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.25rem;
  color: var(--ink);
  transition: box-shadow .15s, transform .15s;
}
.course-card:hover {
  text-decoration: none;
  box-shadow: 0 6px 20px rgba(0,0,0,.08);
  transform: translateY(-2px);
}
.course-card .code { font-weight: 700; color: var(--accent); }
.course-card .name { font-size: 1.1rem; font-weight: 600; }
.course-card .term { font-size: .9rem; color: var(--muted); }

.info-box {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1rem 1.25rem;
  margin-bottom: 1.5rem;
}
.btn {
  display: inline-block;
  background: var(--accent);
  color: #fff;
  padding: .55rem 1rem;
  border-radius: 8px;
}
.btn:hover { text-decoration: none; opacity: .9; }

table { width: 100%; border-collapse: collapse; background: var(--card); border-radius: 12px; overflow: hidden; }
th, td { text-align: left; padding: .75rem; border-bottom: 1px solid var(--border); vertical-align: top; }
th { background: #eef2ff; font-weight: 600; }
tr:last-child td { border-bottom: none; }

@media (max-width: 560px) {
  table, thead, tbody, th, td, tr { display: block; }
  thead { display: none; }
  tr { margin-bottom: 1rem; border: 1px solid var(--border); border-radius: 10px; }
  td { border: none; }
  td::before { content: attr(data-label); font-weight: 600; display: block; color: var(--muted); }
}
```

---

## 5. รันในเครื่อง (ทดสอบก่อน deploy)

```bash
# สร้าง virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# ติดตั้ง
pip install -r requirements.txt

# สร้างเว็บ
python build.py
```

จากนั้นเปิดไฟล์ `docs/index.html` ในเบราว์เซอร์เพื่อดูผลลัพธ์

---

## 6. Deploy ขึ้น GitHub Pages

1. push โค้ดทั้งหมดขึ้น repo (รวมโฟลเดอร์ `docs/` ที่ build แล้ว)
2. ไปที่ repo บน GitHub → **Settings** → **Pages**
3. หัวข้อ **Build and deployment** → Source เลือก **Deploy from a branch**
4. Branch เลือก **main** + โฟลเดอร์ **/docs** → กด **Save**
5. รอ 1–2 นาที จะได้ URL เช่น `https://ชื่อผู้ใช้.github.io/course-hub/`

---

## 7. Workflow ประจำ (ทุกครั้งที่อัปเดต)

```
1. แก้ data/courses.json  (เพิ่มสัปดาห์ / แก้ลิงก์ / เพิ่มวิชา)
2. python build.py
3. git add . && git commit -m "update week X" && git push
4. เว็บอัปเดตเองภายในไม่กี่นาที
```

**ภาคเรียนใหม่:** ก๊อปบล็อกวิชาเดิมใน JSON → แก้ `semester`, `schedule`, `teams_link` → เนื้อหารายสัปดาห์ใช้ซ้ำได้เลย

---

## 8. การเชื่อม OneDrive

1. ใน OneDrive คลิกขวาไฟล์/โฟลเดอร์ → **Share**
2. ตั้งสิทธิ์เป็น **Anyone with the link** + **Can view** (ดูอย่างเดียว)
3. คัดลอกลิงก์ → วางในช่อง `slide_url` ของ JSON
4. จัดโฟลเดอร์ OneDrive ให้คงที่ เช่น `วิชา/ภาคเรียน/สัปดาห์` เพื่อกันลิงก์เสียเมื่อย้ายไฟล์

---

## 9. วิธีทำต่อใน Claude Cowork

เปิด Claude Cowork แล้ว **แนบไฟล์คู่มือนี้** พร้อมวาง prompt นี้:

> ผมต้องการสร้างเว็บรวมรายวิชาแบบ static (JSON + Jinja2 + GitHub Pages) ตามคู่มือที่แนบมานี้
> ช่วยทำให้ผมตามนี้:
> 1. สร้างโฟลเดอร์โปรเจกต์ `course-hub` และไฟล์ทั้งหมดตามคู่มือ (build.py, templates, static, data/courses.json, requirements.txt)
> 2. รัน `python build.py` ให้ดูว่าได้ผลลัพธ์ใน docs/ ถูกต้อง
> 3. อธิบายขั้นตอน push ขึ้น GitHub repo ของผม และตั้งค่า GitHub Pages ให้เสิร์ฟจากโฟลเดอร์ /docs
> 4. หลังจากนั้นช่วยผมเพิ่มข้อมูลวิชาจริงของผมทีละวิชา
>
> เริ่มจากสร้างไฟล์ทั้งหมดก่อนได้เลย

จากนั้นทำงานต่อกับ Cowork ได้ต่อเนื่องในที่เดียว ทั้งแก้ไฟล์ รัน และ deploy
