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
