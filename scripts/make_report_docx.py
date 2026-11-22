"""把《PPT 逐页解读报告》Markdown 转成排版好的 DOCX。"""
from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "articles" / "2026-11-22-困境资产中的因子思维-PPT逐页解读报告.md"
OUT = ROOT / "articles" / "assets" / "困境资产中的因子思维-PPT逐页解读报告.docx"
IMG = ROOT / "articles" / "assets" / "distressed-factor-workflow.png"

INK = RGBColor(62, 44, 35)
MUTED = RGBColor(122, 106, 95)
ORANGE = RGBColor(242, 140, 40)
GREEN = RGBColor(91, 140, 90)


def set_east_asian(style, name="Microsoft YaHei"):
    style.font.name = name
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:eastAsia"), name)
    rfonts.set(qn("w:ascii"), name)
    rfonts.set(qn("w:hAnsi"), name)


def add_page_number(paragraph):
    run = paragraph.add_run()
    fld_char1 = OxmlElement("w:fldChar"); fld_char1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve"); instr.text = "PAGE"
    fld_char2 = OxmlElement("w:fldChar"); fld_char2.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char1); run._r.append(instr); run._r.append(fld_char2)


def shade(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def add_inline(paragraph, text, base_size=11, color=INK):
    parts = re.split(r"(\*\*.*?\*\*|`.*?`)", text)
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            run = paragraph.add_run(part[2:-2]); run.bold = True
        elif part.startswith("`") and part.endswith("`"):
            run = paragraph.add_run(part[1:-1])
            run.font.name = "Consolas"
            run._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
        else:
            run = paragraph.add_run(part)
        run.font.size = Pt(base_size)
        run.font.color.rgb = color


def parse_table(lines):
    rows = []
    for line in lines:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
            continue
        rows.append(cells)
    if not rows:
        return
    ncols = max(len(r) for r in rows)
    table = doc.add_table(rows=len(rows), cols=ncols)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(rows):
        for j in range(ncols):
            cell = table.cell(i, j)
            cell.text = ""
            p = cell.paragraphs[0]
            text = row[j] if j < len(row) else ""
            add_inline(p, text, base_size=10)
            if i == 0:
                for run in p.runs:
                    run.bold = True
                shade(cell, "FDE3C4")
    doc.add_paragraph()


doc = Document()
for section in doc.sections:
    section.top_margin = Inches(0.85)
    section.bottom_margin = Inches(0.8)
    section.left_margin = Inches(0.9)
    section.right_margin = Inches(0.9)

styles = doc.styles
set_east_asian(styles["Normal"])
styles["Normal"].font.size = Pt(11)
styles["Normal"].paragraph_format.line_spacing = 1.5
for name, size, color in [("Title", 30, INK), ("Heading 1", 20, INK),
                          ("Heading 2", 15, ORANGE), ("Heading 3", 12.5, GREEN)]:
    st = styles[name]
    set_east_asian(st)
    st.font.size = Pt(size)
    st.font.bold = True
    st.font.color.rgb = color

footer = doc.sections[0].footer
fp = footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = fp.add_run("困境资产中的因子思维 ｜ PPT 逐页解读报告 ｜ ")
run.font.size = Pt(8); run.font.color.rgb = MUTED
add_page_number(fp)

# cover
p = doc.add_paragraph()
r = p.add_run("内部交流 ｜ 投资方法论")
r.font.size = Pt(12); r.bold = True; r.font.color.rgb = ORANGE
p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(80)
r = p.add_run("困境资产中的因子思维")
r.font.size = Pt(34); r.bold = True; r.font.color.rgb = INK
p = doc.add_paragraph()
r = p.add_run("PPT 逐页解读报告")
r.font.size = Pt(24); r.font.color.rgb = MUTED
p = doc.add_paragraph()
r = p.add_run("14 页 PPT · 30 分钟分享 · 说人话版讲稿 + 注释 + 答疑")
r.font.size = Pt(12); r.font.color.rgb = MUTED
p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(36)
r = p.add_run("2026-11-22")
r.font.size = Pt(11); r.font.color.rgb = MUTED
doc.add_page_break()

doc.add_heading("目录", level=1)
for line in [
    "0. 这份报告怎么用",
    "1. 整体逻辑：一条主线，三幕",
    "2. 逐页解读（第 1–14 页）",
    "3. 30 分钟节奏表",
    "4. 十个高频追问与回答",
    "5. 一页速查卡",
    "6. 使用建议",
]:
    p = doc.add_paragraph(style="List Bullet")
    add_inline(p, line, base_size=11)
doc.add_page_break()


lines = MD.read_text(encoding="utf-8").splitlines()
i = 0
first_h1_skipped = False
while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    if not stripped:
        i += 1
        continue
    if stripped.startswith("```"):
        i += 1
        code_lines = []
        while i < len(lines) and not lines[i].strip().startswith("```"):
            code_lines.append(lines[i])
            i += 1
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.2)
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run("\n".join(code_lines))
        r.font.name = "Consolas"; r.font.size = Pt(9.5)
        i += 1
        continue
    if stripped.startswith("|") and i + 1 < len(lines) and set(lines[i + 1].strip()) <= set("|-: "):
        table_lines = []
        while i < len(lines) and lines[i].strip().startswith("|"):
            table_lines.append(lines[i])
            i += 1
        parse_table(table_lines)
        continue
    if stripped.startswith("# "):
        if not first_h1_skipped:
            first_h1_skipped = True
        else:
            doc.add_heading(stripped[2:], level=1)
        i += 1
        continue
    if stripped.startswith("## "):
        doc.add_heading(stripped[3:], level=1)
        i += 1
        continue
    if stripped.startswith("### "):
        doc.add_heading(stripped[4:], level=2)
        i += 1
        continue
    if stripped.startswith("> "):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        add_inline(p, stripped[2:], base_size=11, color=MUTED)
        i += 1
        continue
    if re.match(r"^\d+\.\s", stripped):
        p = doc.add_paragraph(style="List Number")
        add_inline(p, re.sub(r"^\d+\.\s", "", stripped), base_size=11)
        i += 1
        continue
    if stripped.startswith("- ") or stripped.startswith("• "):
        p = doc.add_paragraph(style="List Bullet")
        add_inline(p, stripped[2:], base_size=11)
        i += 1
        continue
    if stripped.startswith("!["):
        i += 1
        continue
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    add_inline(p, stripped, base_size=11)
    i += 1

if IMG.exists():
    doc.add_page_break()
    doc.add_heading("附：工作流图", level=1)
    doc.add_picture(str(IMG), width=Inches(6.3))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.save(str(OUT))
print("saved", OUT)
