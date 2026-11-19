"""Build the two editable Chinese reports from their reviewed Markdown sources.

Run with python-docx from the Codex document runtime. Render and inspect the
resulting DOCX files before delivery; this builder does not validate pagination.
"""
from pathlib import Path
import re
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

HERE = Path(__file__).resolve().parent


def east_asian(style, name):
    style.font.name = 'Calibri'
    style.element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), name)
    style.font.color.rgb = RGBColor(0, 0, 0)


def setup(compact=False):
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    sec.top_margin = sec.bottom_margin = Cm(2.2)
    sec.left_margin = sec.right_margin = Cm(2.4)
    sec.footer_distance = Cm(1.0)
    normal = doc.styles['Normal']
    east_asian(normal, '宋体')
    normal.font.size = Pt(11.5)
    normal.paragraph_format.line_spacing = 1.13 if compact else 1.27
    normal.paragraph_format.space_after = Pt(4 if compact else 7)
    normal.paragraph_format.widow_control = True
    for name, size in [('Title', 22), ('Heading 1', 16), ('Heading 2', 12.5)]:
        s = doc.styles[name]
        east_asian(s, '黑体')
        s.font.size = Pt(size)
        s.font.bold = name != 'Title'
        s.paragraph_format.space_before = Pt((5 if compact else 10) if name != 'Title' else 0)
        s.paragraph_format.space_after = Pt(4 if compact else 9)
        s.paragraph_format.keep_with_next = True
    east_asian(doc.styles['Caption'], '宋体')
    doc.styles['Caption'].font.size = Pt(10)
    # Word's default Title may contain a themed blue bottom border.
    for border in list(doc.styles.element.iter(qn('w:pBdr'))):
        border.getparent().remove(border)
    foot = sec.footer.paragraphs[0]
    foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = foot.add_run()
    r.font.size = Pt(9)
    field = OxmlElement('w:fldSimple')
    field.set(qn('w:instr'), 'PAGE')
    r._r.addnext(field)
    doc.core_properties.author = '课程项目'
    doc.core_properties.subject = '计算机组成原理课程设计与答辩准备'
    return doc


def add_table(doc, lines):
    rows = [[v.strip() for v in line.strip('|').split('|')] for line in lines]
    rows = [row for row in rows if not all(re.fullmatch(r':?-+:?', v) for v in row)]
    table = doc.add_table(rows=0, cols=len(rows[0]))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    widths = [3.1, 7.4, 5.7] if len(rows[0]) == 3 else [16.2 / len(rows[0])] * len(rows[0])
    for col, width in zip(table.columns, widths):
        col.width = Cm(width)
    pr = table._tbl.tblPr
    borders = OxmlElement('w:tblBorders')
    for side in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        el = OxmlElement('w:' + side)
        for key, val in {'val': 'single', 'sz': '4', 'color': 'D9D9D9'}.items():
            el.set(qn('w:' + key), val)
        borders.append(el)
    pr.append(borders)
    for i, values in enumerate(rows):
        row = table.add_row()
        trpr = row._tr.get_or_add_trPr()
        trpr.append(OxmlElement('w:cantSplit'))
        if i == 0:
            trpr.append(OxmlElement('w:tblHeader'))
        for j, (cell, value) in enumerate(zip(row.cells, values)):
            cell.width = Cm(widths[j])
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            cp = cell._tc.get_or_add_tcPr()
            margins = OxmlElement('w:tcMar')
            for side in ('top', 'bottom', 'left', 'right'):
                m = OxmlElement('w:' + side)
                m.set(qn('w:w'), '85')
                m.set(qn('w:type'), 'dxa')
                margins.append(m)
            cp.append(margins)
            if i == 0:
                fill = OxmlElement('w:shd')
                fill.set(qn('w:fill'), 'E8EDF2')
                cp.append(fill)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.12
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i == 0 or j == 0 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(value)
            r.font.size = Pt(10)
            r.bold = i == 0
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.line_spacing = 0.5


def build(source, output):
    doc = setup(compact=source.stem == 'defense-guide')
    lines = source.read_text(encoding='utf-8').splitlines()
    i = 0
    page_before = False
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line:
            continue
        if line == '<!-- pagebreak -->':
            page_before = True
            continue
        elif line.startswith('|'):
            group = [line]
            while i < len(lines) and lines[i].strip().startswith('|'):
                group.append(lines[i].strip())
                i += 1
            add_table(doc, group)
        elif line.startswith('!['):
            match = re.fullmatch(r'!\[(.*?)\]\((.*?)\)', line)
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.keep_with_next = True
            r = p.add_run()
            shape = r.add_picture(str((source.parent / match[2]).resolve()), width=Cm(11.4))
            shape._inline.docPr.set('descr', match[1])
        elif line.startswith('# '):
            doc.add_paragraph(line[2:], 'Title')
            doc.core_properties.title = line[2:]
        elif line.startswith('## '):
            p = doc.add_paragraph(line[3:], 'Heading 1')
            if page_before:
                p.paragraph_format.page_break_before = True
                page_before = False
        elif line.startswith('### '):
            p = doc.add_paragraph(line[4:], 'Heading 2')
            if page_before:
                p.paragraph_format.page_break_before = True
                page_before = False
        else:
            p = doc.add_paragraph(line, 'Caption' if line.startswith('图 1 ') else 'Normal')
            if re.match(r'^\d+\. ', line):
                p.paragraph_format.left_indent = Cm(0.55)
                p.paragraph_format.first_line_indent = Cm(-0.55)
    doc.save(output)
    print(output)


if __name__ == '__main__':
    build(HERE / 'course-report.md', HERE / '课程设计报告_整理版.docx')
    build(HERE / 'defense-guide.md', HERE / '答辩讲稿与准备_整理版.docx')
